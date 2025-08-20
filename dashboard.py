"""
dashboard.py

Provides a simple, intuitive web-based dashboard for Director-AI using Flask.
Displays crawl progress, screenshot stats, directory completeness, and analytics.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Example: Load processed results if available
    results_file = 'sample_urls_processed.xlsx'
    stats = {}
    if os.path.exists(results_file):
        df = pd.read_excel(results_file)
        stats = {
            'total_urls': len(df),
            'screenshots_taken': df['Screenshot_Path'].notnull().sum() if 'Screenshot_Path' in df.columns else 0,
            'logos_found': df['Logo_URL'].notnull().sum() if 'Logo_URL' in df.columns else 0,
            'success_rate': (df['Status'] == 'success').mean() * 100 if 'Status' in df.columns else 0
        }
    return render_template('dashboard.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    results_file = 'sample_urls_processed.xlsx'
    stats = {}
    if os.path.exists(results_file):
        df = pd.read_excel(results_file)
        stats = {
            'total_urls': len(df),
            'screenshots_taken': df['Screenshot_Path'].notnull().sum() if 'Screenshot_Path' in df.columns else 0,
            'logos_found': df['Logo_URL'].notnull().sum() if 'Logo_URL' in df.columns else 0,
            'success_rate': (df['Status'] == 'success').mean() * 100 if 'Status' in df.columns else 0
        }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=False)
