#!/bin/bash
# Director-AI Dependency Installer
# Usage: bash install_director_ai_deps.sh

set -e

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install new/advanced dependencies for Director-AI
pip install openapi-schema-pydantic
pip install requests
pip install beautifulsoup4
pip install lxml
pip install pillow
pip install pandas
pip install networkx
pip install matplotlib
pip install python-dotenv
pip install boto3
pip install dropbox
pip install google-api-python-client
pip install oauthlib
pip install scikit-learn
pip install tiktoken
pip install openai

# Optional: Print success message
echo "Director-AI dependencies installed successfully."
