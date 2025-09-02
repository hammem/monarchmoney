#!/usr/bin/env python3
"""
Authentication script for MonarchMoney
"""
import asyncio
import getpass
from monarchmoney import MonarchMoney
from monarchmoney.monarchmoney import RequireMFAException


async def authenticate():
    """Authenticate with MonarchMoney"""
    mm = MonarchMoney()

    print("=== MonarchMoney Authentication ===")

    # Get credentials
    email = input("Email: ")
    password = getpass.getpass("Password: ")

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

        # Get MFA code
        mfa_code = input("Enter MFA code: ").strip()
        if not mfa_code:
            print("❌ MFA code required")
            return False

        try:
            print("Verifying MFA code...")
            await mm.multi_factor_authenticate(email, password, mfa_code)

            # Check session after MFA
            session_info = mm.get_session_info()
            if session_info.get("valid"):
                print("✅ MFA successful - session saved")
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


if __name__ == "__main__":
    success = asyncio.run(authenticate())
    if success:
        print("\n🎉 Authentication successful! You can now run comprehensive_test.py")
    else:
        print("\n❌ Authentication failed. Please try again.")
