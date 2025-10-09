Upstox Auto Login
A Python package to programmatically automate the Upstox API v2 login flow using Selenium and TOTP. This tool handles the entire OAuth2 process, from browser automation to exchanging the authorization code for a final access_token.

⚠️ Important Security Disclaimer
This package requires you to store sensitive credentials (API keys, PIN, TOTP secret) either directly in your code or in environment variables. Storing such information in plaintext is a significant security risk. Please ensure you understand the implications and secure your credentials appropriately. It is highly recommended to use environment variables or a secure secret management system instead of hardcoding credentials in your scripts. This package is intended for personal use in secure environments.

How It Works
The login process for Upstox API v2 requires manual intervention to enter a User ID, TOTP, and PIN. This package automates these steps:

Browser Automation: It launches a headless instance of Google Chrome using Selenium.

Navigation: It navigates to the Upstox login authorization dialog.

Credential Entry: It programmatically enters your User ID, generates a Time-based One-Time Password (TOTP), and enters your PIN.

Authorization Code: After successful authentication, Upstox redirects to your specified redirect_url with an authorization code. The package captures this code.

Token Exchange: It then makes a secure backend request to the Upstox token endpoint, exchanging the authorization code for a final access_token.

Cleanup: The browser instance is closed, and the access_token is returned.

Prerequisites
Before using this package, you will need:

Python 3.7+

Google Chrome: The browser must be installed on the system where the script is running.

Upstox Developer Account:

An application created on the Upstox Developer Console.

Your API_KEY and SECRET_KEY.

The redirect_url for your application must be configured. A common value for local development is https://127.0.0.1:5000/.

Installation
Install the package directly from PyPI:

pip install upstox-auto-login

This will also install the necessary dependencies, including selenium and pyotp.

Configuration and Usage
The auto_login function requires your personal Upstox credentials.

Function Parameters
Parameter

Type

Description

API_KEY

str

Your application's API Key from the Upstox Developer Console.

SECRET_KEY

str

Your application's Secret Key from the Upstox Developer Console.

USER_ID

str

Your 10-digit mobile number associated with your Upstox account.

PIN

str

Your 6-digit PIN used for logging into Upstox.

TOTP_SECRET

str

The secret key from your authenticator app (e.g., Google Authenticator) used to generate TOTPs.

redirect_url

str

(Optional) The redirect URI configured in your Upstox app. Defaults to https://127.0.0.1:5000/. Must match your app settings exactly.

Example
Here is a complete example of how to use the package.

import os
from upstox_auto_login import auto_login
import logging

# It's recommended to use environment variables for security
# For example:
# API_KEY = os.getenv("UPSTOX_API_KEY")
# SECRET_KEY = os.getenv("UPSTOX_SECRET_KEY")
# USER_ID = os.getenv("UPSTOX_USER_ID")
# PIN = os.getenv("UPSTOX_PIN")
# TOTP_SECRET = os.getenv("UPSTOX_TOTP_SECRET")

# Configure logging to see progress and errors
logging.basicConfig(level=logging.INFO)

try:
    # Call the auto_login function with your credentials
    access_token = auto_login(
        API_KEY="your_api_key",
        SECRET_KEY="your_secret_key",
        USER_ID="your_10_digit_mobile_number",
        PIN="your_6_digit_pin",
        TOTP_SECRET="your_totp_secret_key_from_authenticator"
    )

    if access_token:
        print(f"\nSuccessfully obtained access token!")
        print(f"Access Token: {access_token}")
        # You can now use this token with the Upstox API client
    else:
        print("\nFailed to obtain access token. Check logs for details.")

except Exception as e:
    print(f"An unexpected error occurred: {e}")


Error Handling
The function is wrapped in a try...except block. If any step of the login process fails (e.g., incorrect credentials, page not loading, network issues), it will log the error and return None.

Contributing
Contributions are welcome! If you find a bug, have a feature request, or want to improve the documentation, please feel free to open an issue or submit a pull request on the project's GitHub repository.

License
This project is licensed under the MIT License. See the LICENSE file for more details.