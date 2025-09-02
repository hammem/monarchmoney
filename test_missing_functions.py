#!/usr/bin/env python3
"""
Test the missing functions that were removed to see which ones actually work
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_missing_functions():
    """Test the functions we removed to see which work"""
    print("=== Testing Previously Removed Functions ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    # Test get_recent_account_balances (this was in original repo)
    print("1. Testing get_recent_account_balances...")
    try:
        result = await mm.get_recent_account_balances()
        print(f"   ✅ SUCCESS! Found data: {type(result)}")
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
            if "accounts" in result:
                print(f"   Accounts: {len(result['accounts'])}")
        return result
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    # Test without parameters to see if that works
    print("2. Testing get_recent_account_balances with specific account...")
    try:
        # Get an account ID first
        accounts = await mm.get_accounts()
        if accounts.get("accounts"):
            account_id = accounts["accounts"][0]["id"]
            print(f"   Using account ID: {account_id}")

            # This might be the issue - maybe it expects account IDs?
            result = await mm.get_recent_account_balances([account_id])
            print(f"   ✅ SUCCESS with account ID! Found data: {type(result)}")
            return result
    except Exception as e:
        print(f"   ❌ FAILED with account ID: {e}")

    # Test other functions to see what errors we get
    print("3. Testing get_net_worth_history...")
    try:
        result = await mm.get_net_worth_history("2024-01-01", "2024-12-31")
        print(f"   ✅ SUCCESS! {type(result)}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("4. Testing get_bills...")
    try:
        result = await mm.get_bills()
        print(f"   ✅ SUCCESS! {type(result)}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("5. Testing get_settings...")
    try:
        result = await mm.get_settings()
        print(f"   ✅ SUCCESS! {type(result)}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")


if __name__ == "__main__":
    asyncio.run(test_missing_functions())
