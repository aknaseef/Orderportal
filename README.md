# 🏥 Pharmacy Order Portal

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**A lightweight, self-hosted inventory management system for independent pharmacy chains.**

## 📚 Documentation
* **[📖 User Manual](USER_MANUAL.md)** – Instructions for Pharmacists & Admins on how to use the app daily.
* **[⚙️ IT Setup Guide](#configuration)** – For IT Admins installing the software.

---

## 🚀 Quick Start (For IT Admins)

### 1. Installation
To set this up on a Windows Server or PC:
```bash
git clone https://github.com/aknaseef/Orderportal.git
cd Orderportal
pip install -r requirements.txt
```




2. Configuration
The system uses a config.json file to manage passwords.
1. Locate config_template.json in the folder.
2. Make a copy and rename it to config.json.
3. Open it and set your secure passwords:
```
   {
    "app_name": "My Pharmacy",
    "admin_password": "SECURE_PASSWORD",
    "branches": {
        "Branch 1": "1234",
        "Branch 2": "5678"
    }

```

3. Run the App
Double-click the Start_Portal.bat file, or run this command:
```
streamlit run app.py

```



🛡️ License
Distributed under the MIT License. You are free to use, modify, and distribute this software.

