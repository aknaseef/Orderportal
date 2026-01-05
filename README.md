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
git clone [https://github.com/YOUR_USERNAME/Pharmacy-Order-Portal.git](https://github.com/YOUR_USERNAME/Pharmacy-Order-Portal.git)
cd Pharmacy-Order-Portal
pip install -r requirements.txt
{
    "app_name": "My Pharmacy",
    "admin_password": "SECURE_PASSWORD",
    "branches": {
        "Branch 1": "1234",
        "Branch 2": "5678"
    }
}
streamlit run app.py

