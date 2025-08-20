"""
output_manager.py

Provides customizable output options for Director-AI:
1. Excel export using pandas
2. Markdown report generation
3. PDF report generation (via markdown -> PDF)
4. API/Webhook integration for external tools
"""

import pandas as pd
import markdown
import pdfkit
import requests
from typing import List, Dict, Any

class OutputManager:
    @staticmethod
    def export_to_excel(data: List[Dict[str, Any]], filename: str):
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, engine='openpyxl')
        return filename

    @staticmethod
    def generate_markdown_report(data: List[Dict[str, Any]], filename: str):
        md = "# Director-AI Report\n\n"
        for item in data:
            md += f"## {item.get('title', 'Untitled')}\n"
            for k, v in item.items():
                md += f"- **{k}**: {v}\n"
            md += "\n"
        with open(filename, 'w') as f:
            f.write(md)
        return filename

    @staticmethod
    def generate_pdf_from_markdown(md_filename: str, pdf_filename: str):
        with open(md_filename, 'r') as f:
            md_text = f.read()
        html = markdown.markdown(md_text)
        pdfkit.from_string(html, pdf_filename)
        return pdf_filename

    @staticmethod
    def send_to_webhook(data: Dict[str, Any], webhook_url: str):
        response = requests.post(webhook_url, json=data, timeout=10)
        return response.status_code, response.text

# Example usage:
# OutputManager.export_to_excel(results, 'results.xlsx')
# OutputManager.generate_markdown_report(results, 'report.md')
# OutputManager.generate_pdf_from_markdown('report.md', 'report.pdf')
# OutputManager.send_to_webhook(results[0], 'https://webhook.site/your-url')
