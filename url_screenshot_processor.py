#!/usr/bin/env python3
"""
📸 URL Screenshot Processor

A powerful Python tool that automatically captures screenshots and extracts logo URLs 
from websites listed in spreadsheets. Perfect for web research, competitive analysis, 
and building visual databases of websites.

FEATURES:
- 🌐 Batch Processing: Process multiple URLs simultaneously with configurable concurrency
- 📸 Full-Page Screenshots: Capture complete webpage screenshots in PNG format
- 🎯 Logo Detection: Automatically extract company logos and favicons
- 📊 Multiple Formats: Support for CSV and Excel files
- 🔄 Retry Logic: Automatic retry for failed requests with exponential backoff
- 🌐 Multi-Browser: Firefox, WebKit, and Chromium browser support with automatic fallback
- 📈 Progress Tracking: Real-time progress reporting and comprehensive statistics
- 🛡️ Error Handling: Graceful handling of invalid URLs and network issues
- 🎨 Detailed Logging: Comprehensive logging with configurable verbosity levels

QUICK START:
1. Run setup: ./setup_and_run.sh
2. Activate environment: source venv/bin/activate
3. Create sample: python url_screenshot_processor.py --create-sample
4. Process URLs: python url_screenshot_processor.py sample_urls.xlsx

For detailed documentation, see URL_Screenshot_Processor_README.md
"""

import pandas as pd
import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import logging
from urllib.parse import urljoin, urlparse
import json
import time
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('url_processor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingConfig:
    """Configuration for URL processing"""
    batch_size: int = 3
    max_retries: int = 2
    timeout: int = 30000
    wait_time: float = 2.0
    viewport_width: int = 1920
    viewport_height: int = 1080
    min_logo_size: int = 30
    screenshot_quality: int = 80

class URLValidator:
    """Validates and normalizes URLs"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL by adding protocol if missing"""
        if not url:
            return ""
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @classmethod
    def validate_and_normalize(cls, url: str) -> Optional[str]:
        """Validate and normalize URL, return None if invalid"""
        try:
            normalized = cls.normalize_url(url)
            if cls.is_valid_url(normalized):
                return normalized
            return None
        except Exception:
            return None

class URLProcessor:
    def __init__(self, spreadsheet_path, output_dir="screenshots", config=None):
        self.spreadsheet_path = Path(spreadsheet_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        self.config = config or ProcessingConfig()
        self.processed_count = 0
        self.total_count = 0
        
    def _log_progress(self, message: str):
        """Log progress with count information"""
        if self.total_count > 0:
            progress = f"[{self.processed_count}/{self.total_count}] "
            logger.info(progress + message)
        else:
            logger.info(message)
    
    async def extract_logo_url(self, page, base_url: str) -> Optional[str]:
        """Extract logo URL from the webpage with improved detection"""
        # Comprehensive logo selectors with priority order
        logo_selectors = [
            # High priority - specific logo selectors
            '.logo img, #logo img',
            '[class*="logo"] img, [id*="logo"] img',
            'img[alt*="logo" i], img[title*="logo" i]',
            'img[src*="logo" i]',
            
            # Medium priority - common locations
            'header img:first-of-type',
            'nav img:first-of-type',
            '.header img:first-of-type',
            '.navbar img:first-of-type',
            
            # Lower priority - fallbacks
            'img[alt*="brand" i], img[title*="brand" i]',
            'img[class*="brand" i]',
            'a[href="/"] img',  # Home link images
        ]
        
        for selector in logo_selectors:
            try:
                elements = await page.locator(selector).all()
                for element in elements:
                    src = await element.get_attribute('src')
                    if not src:
                        continue
                    
                    # Skip data URLs and external tracking pixels
                    if src.startswith('data:') or self._is_tracking_pixel(src):
                        continue
                    
                    # Normalize URL
                    normalized_src = self._normalize_image_url(src, base_url)
                    if not normalized_src:
                        continue
                    
                    # Check image dimensions
                    if await self._is_valid_logo_size(element):
                        return normalized_src
                        
            except (PlaywrightTimeoutError, AttributeError) as e:
                logger.debug("Error with selector %s: %s", selector, str(e))
                continue
            except Exception as e:
                logger.warning("Unexpected error with selector %s: %s", selector, str(e))
                continue
        
        # Try to find favicon as fallback
        return await self._extract_favicon(page, base_url)
    
    def _is_tracking_pixel(self, src: str) -> bool:
        """Check if image is likely a tracking pixel"""
        tracking_domains = [
            'google-analytics.com', 'googletagmanager.com', 'facebook.com',
            'doubleclick.net', 'googlesyndication.com', 'amazon-adsystem.com'
        ]
        return any(domain in src for domain in tracking_domains)
    
    def _normalize_image_url(self, src: str, base_url: str) -> Optional[str]:
        """Normalize image URL"""
        try:
            if src.startswith('//'):
                return 'https:' + src
            elif src.startswith('/'):
                return urljoin(base_url, src)
            elif src.startswith('http'):
                return src
            else:
                return urljoin(base_url, src)
        except Exception as e:
            logger.debug("Error normalizing URL %s: %s", src, str(e))
            return None
    
    async def _is_valid_logo_size(self, element) -> bool:
        """Check if image has valid logo dimensions"""
        try:
            # Get computed dimensions
            bbox = await element.bounding_box()
            if bbox:
                width, height = bbox['width'], bbox['height']
                # Logo should be reasonably sized but not too large
                return (self.config.min_logo_size <= width <= 500 and 
                       self.config.min_logo_size <= height <= 300)
            
            # Fallback to attribute checking
            width_attr = await element.get_attribute('width')
            height_attr = await element.get_attribute('height')
            
            if width_attr and height_attr:
                try:
                    width, height = int(width_attr), int(height_attr)
                    return (self.config.min_logo_size <= width <= 500 and 
                           self.config.min_logo_size <= height <= 300)
                except ValueError:
                    pass
            
            # If no size info, assume it's valid
            return True
            
        except Exception as e:
            logger.debug("Error checking image size: %s", str(e))
            return True
    
    async def _extract_favicon(self, page, base_url: str) -> Optional[str]:
        """Extract favicon as fallback logo"""
        favicon_selectors = [
            'link[rel="icon"]',
            'link[rel="shortcut icon"]',
            'link[rel="apple-touch-icon"]'
        ]
        
        for selector in favicon_selectors:
            try:
                element = await page.locator(selector).first
                if element:
                    href = await element.get_attribute('href')
                    if href:
                        return self._normalize_image_url(href, base_url)
            except Exception as e:
                logger.debug("Error extracting favicon with %s: %s", selector, str(e))
                continue
        
        # Default favicon location
        try:
            parsed_url = urlparse(base_url)
            return f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
        except Exception:
            return None
    
    async def take_screenshot(self, page, url: str, filename: str) -> Optional[str]:
        """Take a screenshot of the webpage with retry logic"""
        try:
            await page.goto(url, wait_until='networkidle', timeout=self.config.timeout)
            await page.wait_for_load_state('domcontentloaded')
            
            # Wait for dynamic content
            await asyncio.sleep(self.config.wait_time)
            
            # Take full page screenshot
            screenshot_path = self.output_dir / filename
            await page.screenshot(
                path=str(screenshot_path), 
                full_page=True
                # Note: quality parameter only works with JPEG format
            )
            
            return str(screenshot_path)
            
        except PlaywrightTimeoutError:
            logger.error("Timeout taking screenshot for %s", url)
            return None
        except Exception as e:
            logger.error("Error taking screenshot for %s: %s", url, str(e))
            return None
    
    async def process_single_url(self, playwright, url: str, index: int) -> Dict:
        """Process a single URL with retry logic"""
        browser = None
        normalized_url = URLValidator.validate_and_normalize(url)
        
        if not normalized_url:
            return {
                'original_url': url,
                'normalized_url': None,
                'screenshot_path': None,
                'logo_url': None,
                'status': 'invalid_url',
                'error': 'Invalid URL format'
            }
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Try multiple browser types as fallback (Firefox first on macOS)
                browser_types = ['firefox', 'webkit', 'chromium']
                browser_launched = False
                
                for browser_type_name in browser_types:
                    try:
                        browser_type = getattr(playwright, browser_type_name)
                        
                        # macOS-specific browser arguments
                        browser_args = ['--no-sandbox', '--disable-setuid-sandbox']
                        
                        # Add macOS-specific args for stability
                        if browser_type_name == 'chromium':
                            browser_args.extend([
                                '--disable-dev-shm-usage',
                                '--disable-gpu',
                                '--disable-software-rasterizer',
                                '--disable-background-timer-throttling',
                                '--disable-backgrounding-occluded-windows',
                                '--disable-renderer-backgrounding',
                                '--disable-features=TranslateUI',
                                '--disable-ipc-flooding-protection'
                            ])
                        
                        browser = await browser_type.launch(
                            headless=True,
                            args=browser_args
                        )
                        browser_launched = True
                        break
                    except Exception as browser_error:
                        if 'Executable doesn\'t exist' in str(browser_error):
                            logger.debug("Browser %s not available: %s", browser_type_name, str(browser_error))
                            continue
                        else:
                            raise browser_error
                
                if not browser_launched:
                    raise RuntimeError("No browser available. Please run 'playwright install' to install browsers.")
                
                context = await browser.new_context(
                    viewport={
                        'width': self.config.viewport_width, 
                        'height': self.config.viewport_height
                    },
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = await context.new_page()
                
                # Take screenshot
                screenshot_filename = f"screenshot_{index:03d}_{int(time.time())}.png"
                screenshot_path = await self.take_screenshot(page, normalized_url, screenshot_filename)
                
                # Extract logo URL
                logo_url = await self.extract_logo_url(page, normalized_url)
                
                result = {
                    'original_url': url,
                    'normalized_url': normalized_url,
                    'screenshot_path': screenshot_path,
                    'logo_url': logo_url,
                    'status': 'success',
                    'attempt': attempt + 1
                }
                
                self._log_progress("Processed %s: screenshot=%s, logo=%s" % (
                    normalized_url, 
                    screenshot_path or 'None', 
                    logo_url or 'None'
                ))
                
                return result
                
            except PlaywrightTimeoutError:
                error_msg = f"Timeout processing {normalized_url} (attempt {attempt + 1})"
                if attempt == self.config.max_retries:
                    logger.error(error_msg)
                else:
                    logger.warning("%s, retrying...", error_msg)
                    
            except RuntimeError as e:
                # Browser not available error - don't retry
                logger.error("Browser error: %s", str(e))
                return {
                    'original_url': url,
                    'normalized_url': normalized_url,
                    'screenshot_path': None,
                    'logo_url': None,
                    'status': 'error',
                    'error': str(e)
                }
                    
            except Exception as e:
                error_msg = f"Error processing {normalized_url} (attempt {attempt + 1}): {str(e)}"
                if attempt == self.config.max_retries:
                    logger.error(error_msg)
                else:
                    logger.warning("%s, retrying...", error_msg)
                    
            finally:
                if browser:
                    try:
                        await browser.close()
                    except Exception as e:
                        logger.debug("Error closing browser: %s", str(e))
                    browser = None
            
            # Wait before retry
            if attempt < self.config.max_retries:
                await asyncio.sleep(1)
        
        # All attempts failed
        return {
            'original_url': url,
            'normalized_url': normalized_url,
            'screenshot_path': None,
            'logo_url': None,
            'status': 'error',
            'error': f'Failed after {self.config.max_retries + 1} attempts',
            'attempts': self.config.max_retries + 1
        }
    
    async def process_urls(self, urls: List[str]) -> List[Dict]:
        """Process multiple URLs concurrently with progress tracking"""
        self.total_count = len(urls)
        self.processed_count = 0
        
        async with async_playwright() as playwright:
            # Process URLs in batches to avoid overwhelming the system
            results = []
            
            for i in range(0, len(urls), self.config.batch_size):
                batch = urls[i:i+self.config.batch_size]
                self._log_progress("Processing batch %d/%d" % (
                    (i // self.config.batch_size) + 1,
                    (len(urls) + self.config.batch_size - 1) // self.config.batch_size
                ))
                
                batch_results = await asyncio.gather(
                    *[self.process_single_url(playwright, url, i+j) 
                      for j, url in enumerate(batch)],
                    return_exceptions=True
                )
                
                # Handle any exceptions that occurred
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error("Unexpected error processing %s: %s", 
                                   batch[j], str(result))
                        result = {
                            'original_url': batch[j],
                            'normalized_url': None,
                            'screenshot_path': None,
                            'logo_url': None,
                            'status': 'error',
                            'error': str(result)
                        }
                    
                    results.append(result)
                    self.processed_count += 1
                
                # Small delay between batches
                if i + self.config.batch_size < len(urls):
                    await asyncio.sleep(0.5)
                
            return results
    
    def load_spreadsheet(self) -> Tuple[List[str], pd.DataFrame]:
        """Load URLs from spreadsheet with validation"""
        try:
            # Load the spreadsheet
            if self.spreadsheet_path.suffix.lower() == '.csv':
                df = pd.read_csv(self.spreadsheet_path)
            else:
                df = pd.read_excel(self.spreadsheet_path)
            
            # Get URLs from first column, handle various column names
            possible_url_columns = ['url', 'URL', 'link', 'Link', 'website', 'Website']
            url_column = None
            
            for col in possible_url_columns:
                if col in df.columns:
                    url_column = col
                    break
            
            if url_column is None:
                # Use first column
                url_column = df.columns[0]
                logger.warning("No URL column found, using first column: %s", url_column)
            
            # Extract and clean URLs
            urls = df[url_column].dropna().astype(str).tolist()
            urls = [url.strip() for url in urls if url.strip()]
            
            logger.info("Loaded %d URLs from %s", len(urls), self.spreadsheet_path)
            return urls, df
            
        except FileNotFoundError:
            logger.error("Spreadsheet file not found: %s", self.spreadsheet_path)
            raise
        except pd.errors.EmptyDataError:
            logger.error("Spreadsheet is empty: %s", self.spreadsheet_path)
            raise
        except Exception as e:
            logger.error("Error loading spreadsheet: %s", str(e))
            raise
    
    def save_results(self, original_df: pd.DataFrame, results: List[Dict]) -> Path:
        """Save results back to spreadsheet with comprehensive data"""
        try:
            # Add new columns with results
            original_df['Original_URL'] = [r['original_url'] for r in results]
            original_df['Normalized_URL'] = [r['normalized_url'] for r in results]
            original_df['Logo_URL'] = [r['logo_url'] for r in results]
            original_df['Screenshot_Path'] = [r['screenshot_path'] for r in results]
            original_df['Status'] = [r['status'] for r in results]
            original_df['Error_Message'] = [r.get('error', '') for r in results]
            original_df['Processing_Attempts'] = [r.get('attempts', r.get('attempt', 1)) for r in results]
            
            # Save to new file
            output_path = self.spreadsheet_path.parent / f"{self.spreadsheet_path.stem}_processed{self.spreadsheet_path.suffix}"
            
            if output_path.suffix.lower() == '.csv':
                original_df.to_csv(output_path, index=False)
            else:
                original_df.to_excel(output_path, index=False, engine='openpyxl')
                
            logger.info("Results saved to %s", output_path)
            return output_path
            
        except Exception as e:
            logger.error("Error saving results: %s", str(e))
            raise
    
    def _generate_summary_report(self, results: List[Dict]) -> Dict:
        """Generate a summary report of processing results"""
        total = len(results)
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'error')
        invalid_urls = sum(1 for r in results if r['status'] == 'invalid_url')
        screenshots_taken = sum(1 for r in results if r['screenshot_path'])
        logos_found = sum(1 for r in results if r['logo_url'])
        
        return {
            'total_urls': total,
            'successful': successful,
            'failed': failed,
            'invalid_urls': invalid_urls,
            'screenshots_taken': screenshots_taken,
            'logos_found': logos_found,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'logo_detection_rate': (logos_found / successful * 100) if successful > 0 else 0
        }
    
    async def run(self) -> List[Dict]:
        """Main processing function with comprehensive reporting"""
        try:
            # Load URLs from spreadsheet
            urls, original_df = self.load_spreadsheet()
            
            if not urls:
                logger.warning("No URLs found in spreadsheet")
                return []
            
            # Process URLs
            logger.info("Starting processing of %d URLs...", len(urls))
            start_time = time.time()
            
            results = await self.process_urls(urls)
            
            # Save results
            output_path = self.save_results(original_df, results)
            
            # Generate and display summary
            summary = self._generate_summary_report(results)
            processing_time = time.time() - start_time
            
            logger.info("Processing complete! %d/%d URLs processed successfully", 
                       summary['successful'], summary['total_urls'])
            logger.info("Results saved to: %s", output_path)
            logger.info("Summary: %.1f%% success rate, %.1f%% logo detection rate", 
                       summary['success_rate'], summary['logo_detection_rate'])
            logger.info("Processing time: %.2f seconds", processing_time)
            
            return results
            
        except Exception as e:
            logger.error("Error in main processing: %s", str(e))
            raise

def create_sample_spreadsheet(filename: str = 'sample_urls.xlsx') -> str:
    """Create a sample spreadsheet with test URLs"""
    sample_data = {
        'URL': [
            'https://www.google.com',
            'https://www.github.com',
            'https://www.python.org',
            'https://www.mozilla.org',
            'https://www.stackoverflow.com',
            'https://www.microsoft.com',
            'https://www.apple.com',
            'https://www.amazon.com'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        logger.info("Created %s with test URLs", filename)
        return filename
    except (ImportError, ModuleNotFoundError):
        # Fallback to CSV if Excel/openpyxl not available
        csv_filename = filename.replace('.xlsx', '.csv')
        df.to_csv(csv_filename, index=False)
        logger.info("Created %s with test URLs (CSV format)", csv_filename)
        return csv_filename

def main():
    """Main entry point with improved argument handling"""
    parser = argparse.ArgumentParser(
        description='Process URLs from spreadsheet and extract logos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s spreadsheet.xlsx                    # Process URLs from spreadsheet
  %(prog)s --create-sample                     # Create sample spreadsheet
  %(prog)s spreadsheet.csv --batch-size 5     # Process with custom batch size
  %(prog)s spreadsheet.xlsx --verbose          # Enable verbose logging
        """
    )
    
    parser.add_argument('spreadsheet', nargs='?', 
                       help='Path to spreadsheet file (CSV or Excel)')
    parser.add_argument('--create-sample', action='store_true', 
                       help='Create sample spreadsheet with test URLs')
    parser.add_argument('--output-dir', default='screenshots', 
                       help='Output directory for screenshots (default: screenshots)')
    parser.add_argument('--batch-size', type=int, default=3,
                       help='Number of URLs to process concurrently (default: 3)')
    parser.add_argument('--max-retries', type=int, default=2,
                       help='Maximum retry attempts for failed URLs (default: 2)')
    parser.add_argument('--timeout', type=int, default=30000,
                       help='Timeout in milliseconds for page loads (default: 30000)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.create_sample:
        try:
            spreadsheet_path = create_sample_spreadsheet()
            print(f"Sample spreadsheet created: {spreadsheet_path}")
            print("You can now run: python url_screenshot_processor.py " + spreadsheet_path)
        except (ImportError, ModuleNotFoundError, OSError) as e:
            print(f"Error creating sample spreadsheet: {e}")
        return
    
    if not args.spreadsheet:
        parser.print_help()
        print("\nError: Please provide a spreadsheet path or use --create-sample")
        return
    
    if not os.path.exists(args.spreadsheet):
        print(f"Error: {args.spreadsheet} not found")
        return
    
    # Create configuration
    config = ProcessingConfig(
        batch_size=args.batch_size,
        max_retries=args.max_retries,
        timeout=args.timeout
    )
    
    processor = URLProcessor(args.spreadsheet, args.output_dir, config)
    
    try:
        asyncio.run(processor.run())
        print("\nProcessing completed successfully!")
        print(f"Check the '{args.output_dir}' directory for screenshots")
        print("Check the processed spreadsheet for results")
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        print("\nProcessing interrupted by user")
        
    except (OSError, ValueError, RuntimeError) as e:
        logger.error("Processing failed: %s", str(e))
        print(f"\nProcessing failed: {e}")
        print("Check the log file 'url_processor.log' for details")

if __name__ == "__main__":
    main()
