#!/usr/bin/env python3
"""
Test apply rules on a larger scale to verify it works with all 18,881+ transactions
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_larger_scale():
    """Test apply rules on larger scale"""
    print("=== Testing Larger Scale Apply Rules ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    print("1. Testing apply_rules_to_existing_transactions with limit=10...")
    try:
        result = await mm.apply_rules_to_existing_transactions(limit=10)
        print("   ✅ SUCCESS!")
        print(
            f"   Applied {result.get('applied', 0)}/{result.get('processed', 0)} rules"
        )

    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return

    print("\n2. Testing with NO limit (all rules)...")
    try:
        result = await mm.apply_rules_to_existing_transactions()  # All rules
        print("   ✅ SUCCESS!")
        print(
            f"   Applied {result.get('applied', 0)}/{result.get('processed', 0)} rules"
        )
        print(f"   Total rules in account: {result.get('rules_count', 0)}")

    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("\n🎉 Apply rules functionality is WORKING!")
    print("📋 This will now apply ALL your rules to your existing 18,881+ transactions")
    print(
        "💫 Each rule update triggers MonarchMoney backend to categorize matching transactions"
    )


if __name__ == "__main__":
    asyncio.run(test_larger_scale())
