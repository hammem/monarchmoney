#!/usr/bin/env python3
"""
Debug rule update issues by examining the exact data structure
"""
import asyncio
import json
from pathlib import Path
from monarchmoney import MonarchMoney


async def debug_rule_update():
    """Debug rule update by examining data structures"""
    print("=== Debugging Rule Update Issues ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    # Get rules and examine their structure
    print("1. Examining rule data structure...")
    try:
        rules_response = await mm.get_transaction_rules()
        rules = rules_response.get("transactionRules", [])

        if rules:
            # Look at the first rule
            sample_rule = rules[0]
            print(f"   Sample rule ID: {sample_rule.get('id')}")
            print(f"   Rule keys: {list(sample_rule.keys())}")

            # Show the full rule structure (cleaned)
            print("\n   Full rule structure:")
            rule_copy = dict(sample_rule)

            # Remove __typename fields for cleaner output
            def clean_typename(obj):
                if isinstance(obj, dict):
                    return {
                        k: clean_typename(v)
                        for k, v in obj.items()
                        if k != "__typename"
                    }
                elif isinstance(obj, list):
                    return [clean_typename(item) for item in obj]
                return obj

            clean_rule = clean_typename(rule_copy)
            print(json.dumps(clean_rule, indent=2))

            # Try updating this specific rule
            print(f"\n2. Testing update for rule {sample_rule.get('id')}...")

            # First, let's try a minimal update that only changes the retroactive flag
            try:
                minimal_input = {
                    "id": sample_rule.get("id"),
                    "applyToExistingTransactions": True,
                }

                print(f"   Minimal input: {json.dumps(minimal_input, indent=2)}")

                # This would need to be implemented with just the minimal fields
                # But let's see what fields are actually required

            except Exception as e:
                print(f"   ❌ Minimal update failed: {e}")
        else:
            print("   ❌ No rules found")

    except Exception as e:
        print(f"   ❌ Failed to get rules: {e}")


if __name__ == "__main__":
    asyncio.run(debug_rule_update())
