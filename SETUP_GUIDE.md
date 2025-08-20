# Director-AI: Detailed Step-by-Step Setup Guide

This guide will help you set up Director-AI from scratch, ensuring all dependencies and features work smoothly for any user.

---

## 1. Prerequisites
- Python 3.7 or higher installed (recommend Python 3.11)
- Git (optional, for cloning the repository)
- Internet connection for package installation

---

## 2. Clone or Download the Project
- If using Git:
  ```bash
  git clone <your-repo-url>
  cd URL\ Screenshot\ Processor
  ```
- Or download and unzip the project folder.

---

## 3. Create a Virtual Environment
- In the project directory:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- This isolates your dependencies and avoids conflicts.

---

## 4. Upgrade pip
- Ensure you have the latest pip:
  ```bash
  pip install --upgrade pip
  ```

---

## 5. Install All Dependencies
- Install all required packages:
  ```bash
  pip install -r requirements.txt
  ```
- If you encounter missing packages, install them individually:
  ```bash
  pip install <package-name>
  ```

---

## 6. Install Playwright Browsers (Optional, for screenshot features)
- If you use Playwright for web automation:
  ```bash
  playwright install
  ```

---

## 7. Configure API Keys and Credentials
- For OpenAI, Google Drive, or other integrations, set up your API keys.
- Place credentials (e.g., `service_account.json` for Google Drive) in the project directory.
- You may use a `.env` file for sensitive keys:
  ```env
  OPENAI_API_KEY=your_openai_key
  GOOGLE_SERVICE_ACCOUNT=service_account.json
  ```

---

## 8. Run the Main Script
- Start Director-AI:
  ```bash
  python director_ai.py
  ```
- If you want to use the web dashboard:
  ```bash
  python dashboard.py
  ```
- For CLI dashboard:
  ```bash
  python -c "from cli_dashboard import show_cli_dashboard; show_cli_dashboard('sample_urls_processed.xlsx')"
  ```

---

## 9. Troubleshooting
- If you see `ModuleNotFoundError`, activate your virtual environment and install the missing package:
  ```bash
  source venv/bin/activate
  pip install <missing-package>
  ```
- If you see browser errors, run:
  ```bash
  playwright install
  ```
- For permission or credential errors, check your API keys and file paths.

---

## 10. Updating and Extending
- To update packages:
  ```bash
  pip install --upgrade -r requirements.txt
  ```
- To add plugins, place `.py` files in the `plugins/` directory.
- To customize outputs, edit `output_manager.py`.

---

## 11. Getting Help
- Check the README.md for feature documentation.
- Review log files (e.g., `url_processor.log`) for error details.
- Ask for help or open issues in your project repository.

---

**Director-AI is now ready for use!**
