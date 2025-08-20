"""
cli_dashboard.py

Provides a simple CLI dashboard for Director-AI.
Displays crawl progress, screenshot stats, directory completeness, and analytics in the terminal.
"""

import pandas as pd
import os

def show_cli_dashboard(results_file: str = 'sample_urls_processed.xlsx'):
    if not os.path.exists(results_file):
        print(f"Results file not found: {results_file}")
        return
    df = pd.read_excel(results_file)
    total_urls = len(df)
    screenshots_taken = df['Screenshot_Path'].notnull().sum() if 'Screenshot_Path' in df.columns else 0
    logos_found = df['Logo_URL'].notnull().sum() if 'Logo_URL' in df.columns else 0
    success_rate = (df['Status'] == 'success').mean() * 100 if 'Status' in df.columns else 0
    print("\n=== Director-AI CLI Dashboard ===")
    print(f"Total URLs: {total_urls}")
    print(f"Screenshots Taken: {screenshots_taken}")
    print(f"Logos Found: {logos_found}")
    print(f"Success Rate: {success_rate:.1f}%")
    print("===============================\n")

# Example usage:
# show_cli_dashboard('sample_urls_processed.xlsx')
