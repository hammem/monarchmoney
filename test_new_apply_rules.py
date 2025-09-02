#!/usr/bin/env python3
"""
Test the new apply_rules_to_existing_transactions implementation
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_new_apply_rules():
    """Test the new implementation"""
    print("=== Testing New Apply Rules Implementation ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    print("1. Testing apply_rules_to_existing_transactions with limit=3...")
    try:
        result = await mm.apply_rules_to_existing_transactions(limit=3)
        print("   ✅ SUCCESS!")
        print(f"   Result: {result}")

        # Check if it actually worked
        if result.get("applied", 0) > 0:
            print(f"   🎉 Successfully applied {result['applied']} rules!")
        else:
            print("   ⚠️  No rules were applied - might be an issue")

    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("\n2. Testing manual rule update...")
    try:
        # Get a rule to test with
        rules = await mm.get_transaction_rules()
        test_rule = rules.get("transactionRules", [{}])[0]

        if test_rule.get("id"):
            print(f"   Testing with rule: {test_rule.get('id')}")
            result = await mm.update_transaction_rule_retroactive(
                rule_data=test_rule, apply_to_existing_transactions=True
            )
            print("   ✅ Manual rule update SUCCESS!")
        else:
            print("   ⚠️  No rules found to test with")

    except Exception as e:
        print(f"   ❌ Manual rule update failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_new_apply_rules())
