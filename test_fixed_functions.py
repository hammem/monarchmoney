#!/usr/bin/env python3
"""
Test the newly fixed functions
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_fixed_functions():
    """Test the newly fixed functions"""
    print("=== Testing Fixed Functions ===")

    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    # Test fixed net worth history
    print("1. Testing fixed get_net_worth_history...")
    try:
        result = await mm.get_net_worth_history("2024-01-01", "2024-12-31")
        print(f"   ✅ SUCCESS! Type: {type(result)}")
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
            if "aggregateSnapshots" in result:
                snapshots = result["aggregateSnapshots"]
                print(f"   Found {len(snapshots)} snapshots")
                if snapshots:
                    print(f"   Sample snapshot: {snapshots[0]}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    # Test if any other functions might work now
    print("\n2. Testing other functions that might be fixable...")

    # Test get_bills using the recurring operations I found
    print("   Testing get_bills equivalent...")
    try:
        # This might work with the recurring operations from the HAR
        result = await mm.get_recurring_transactions()
        print(f"   ✅ get_recurring_transactions works: {type(result)}")
        if isinstance(result, dict):
            print(f"   Keys: {list(result.keys())}")
    except Exception as e:
        print(f"   ❌ get_recurring_transactions failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_fixed_functions())
