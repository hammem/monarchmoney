#!/usr/bin/env python3
"""
Debug the get_accounts failure
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def debug_get_accounts():
    """Debug get_accounts issue"""
    print("=== Debugging get_accounts Issue ===")

    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    print("1. Testing get_accounts...")
    try:
        result = await mm.get_accounts()
        print(f"   ✅ SUCCESS: {type(result)}")
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
            if "accounts" in result:
                print(f"   Found {len(result['accounts'])} accounts")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("2. Testing get_recent_account_balances...")
    try:
        result = await mm.get_recent_account_balances()
        print(f"   ✅ SUCCESS: {type(result)}")
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")


if __name__ == "__main__":
    asyncio.run(debug_get_accounts())
