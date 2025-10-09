# Upstox Auto Login

A Python package to automate Upstox login using Selenium and TOTP.

## Installation

```bash
pip install upstox-auto-login


Usages

from upstox_auto_login import auto_login

token = auto_login(
    API_KEY="your_api_key",
    SECRET_KEY="your_secret_key",
    USER_ID="your_user_id",
    PIN="your_pin",
    TOTP_SECRET="your_totp_secret"
)

print(token)
