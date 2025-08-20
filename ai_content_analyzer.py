"""
ai_content_analyzer.py

Provides AI-powered content analysis and tagging for Director-AI.
Uses OpenAI API to extract categories, use cases, platforms, and descriptions from web page content or OpenAPI metadata.
"""

import openai
from typing import Dict, Any, Optional

class AIContentAnalyzer:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key

    def analyze_content(self, text: str) -> Dict[str, Any]:
        """
        Use OpenAI to extract categories, use cases, platforms, and descriptions from text.
        """
        prompt = (
            """
            Analyze the following content and extract:
            - Categories
            - Use Cases
            - Platforms
            - Description
            Return results as a JSON object with keys: categories, use_cases, platforms, description.
            Content:
            """ + text
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            result_text = response.choices[0].message['content']
            import json
            return json.loads(result_text)
        except Exception as e:
            return {"error": str(e)}

# Example usage:
# analyzer = AIContentAnalyzer(openai_api_key="your_key")
# result = analyzer.analyze_content("Sample website or API description text...")
# print(result)
