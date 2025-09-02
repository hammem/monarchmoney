#!/usr/bin/env python3
"""
Simple interactive login for MonarchMoney
"""
import asyncio
import os
from monarchmoney import MonarchMoney


async def simple_login():
    """Simple interactive login"""
    mm = MonarchMoney()

    # Get credentials from environment
    email = os.getenv("MONARCH_EMAIL", "keith@hadm.net")
    password = os.getenv("MONARCH_PASSWORD", "yfb9rku9JVU.fyq2khp")

    print("=== MonarchMoney Interactive Login ===")
    print(f"Using email: {email}")

    try:
        # Use interactive login which handles MFA automatically
        await mm.interactive_login(email, password)

        # Test the session
        session_info = mm.get_session_info()
        if session_info.get("valid"):
            print("✅ Login successful!")
            print(f"Session info: {session_info}")

            # Test basic API call
            accounts = await mm.get_accounts()
            print(f"✅ Found {len(accounts.get('accounts', []))} accounts")
            return True
        else:
            print("❌ Session invalid after login")
            return False

    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(simple_login())
    if success:
        print(
            "\n🎉 Login successful! Session saved. You can now run comprehensive_test.py"
        )
    else:
        print("\n❌ Login failed.")
