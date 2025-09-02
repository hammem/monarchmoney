#!/usr/bin/env python3
"""
Authentication script for MonarchMoney using environment variables and TOTP
"""
import asyncio
import os
from pathlib import Path
import oathtool
from monarchmoney import MonarchMoney
from monarchmoney.monarchmoney import RequireMFAException


def load_env():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    else:
        print(
            "❌ .env file not found. Copy .env.example to .env and fill in your credentials."
        )
        return False
    return True


def generate_totp(secret):
    """Generate TOTP code from secret"""
    try:
        # Generate TOTP code (oathtool generates TOTP by default)
        totp_code = oathtool.generate_otp(secret)
        return totp_code
    except Exception as e:
        print(f"❌ Failed to generate TOTP: {e}")
        return None


async def authenticate():
    """Authenticate with MonarchMoney using environment variables"""
    if not load_env():
        return False

    # Get credentials from environment
    email = os.getenv("MONARCH_EMAIL")
    password = os.getenv("MONARCH_PASSWORD")
    mfa_secret = os.getenv("MONARCH_MFA_SECRET")

    if not email or not password:
        print("❌ MONARCH_EMAIL and MONARCH_PASSWORD must be set in .env file")
        return False

    mm = MonarchMoney()

    print("=== MonarchMoney Authentication ===")
    print(f"Email: {email}")

    try:
        print("Logging in...")
        await mm.login(email, password)
        print("✅ Login successful!")

        # Check session
        session_info = mm.get_session_info()
        if session_info.get("valid"):
            print("✅ Authentication complete - session saved")
            return True

    except RequireMFAException:
        print("🔐 Multi-factor authentication required")

        if not mfa_secret:
            print("❌ MONARCH_MFA_SECRET not set in .env file")
            print("   Add your TOTP secret key to the .env file")
            return False

        # Generate TOTP code
        mfa_code = generate_totp(mfa_secret)
        if not mfa_code:
            return False

        print(f"Generated MFA code: {mfa_code}")

        try:
            print("Verifying MFA code...")
            await mm.multi_factor_authenticate(email, password, mfa_code)

            # Check session after MFA
            session_info = mm.get_session_info()
            if session_info.get("valid"):
                print("✅ MFA successful - session saved")
                print(f"Session info: {session_info}")
                return True
            else:
                print("❌ MFA verification failed")
                return False

        except Exception as e:
            print(f"❌ MFA failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

    return False


async def test_auth():
    """Test authentication and basic API call"""
    success = await authenticate()
    if not success:
        return False

    # Test basic API call
    mm = MonarchMoney()
    try:
        print("\n=== Testing API Access ===")
        accounts = await mm.get_accounts()
        print(f"✅ Found {len(accounts.get('accounts', []))} accounts")

        categories = await mm.get_transaction_categories()
        print(f"✅ Found {len(categories.get('categories', []))} categories")

        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_auth())
    if success:
        print(
            "\n🎉 Authentication and API test successful! You can now run comprehensive_test.py"
        )
    else:
        print("\n❌ Authentication failed. Check your .env file and try again.")
