#!/usr/bin/env python3

import asyncio
import json
import sys

sys.path.insert(0, "/home/keith/src/monarchmoney")

from monarchmoney import MonarchMoney


async def test_basic():
    """Basic test to check if API access is working."""
    mm = MonarchMoney()
    
    print("=== Testing Basic API Access ===")
    
    # Try interactive login
    try:
        await mm.interactive_login()
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return
    
    # Test basic API call - get accounts (should always work)
    print("\n=== Testing get_accounts ===")
    try:
        accounts = await mm.get_accounts()
        print(f"✓ Retrieved {len(accounts.get('accounts', []))} accounts")
    except Exception as e:
        print(f"✗ get_accounts failed: {e}")
        return
    
    # Test get_transaction_rules (our problem area)
    print("\n=== Testing get_transaction_rules ===")
    try:
        rules = await mm.get_transaction_rules()
        print(f"✓ Retrieved {len(rules.get('transactionRules', []))} rules")
        print(f"Raw response: {json.dumps(rules, indent=2)[:500]}...")
    except Exception as e:
        print(f"✗ get_transaction_rules failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_basic())