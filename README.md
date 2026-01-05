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
### 4. Network Setup (Crucial)
If your branches are in different physical locations (different WiFi networks), you must connect them securely. You have two options:

**Option A: Tailscale (Recommended - Free & Easy)**
1.  Install [Tailscale](https://tailscale.com) on the Main PC and sign in.
2.  Install Tailscale on every Branch PC/Phone and sign in with the same account.
3.  Tailscale will give the Main PC a unique IP (e.g., `100.x.y.z`).
4.  Branches can now access the app using: `http://100.x.y.z:8501`.

**Option B: Static IP (Advanced)**
If your Main Branch has a Public Static IP from your ISP (Etisalat/Du):
1.  Log in to your router.
2.  Set up **Port Forwarding** for Port `8501` to your PC's local IP.
3.  Branches access via: `http://YOUR_STATIC_IP:8501`.



🛡️ License
Distributed under the MIT License. You are free to use, modify, and distribute this software.

