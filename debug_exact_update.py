#!/usr/bin/env python3
"""
Debug the exact update structure being sent vs expected
"""
import asyncio
import json
from pathlib import Path
from monarchmoney import MonarchMoney


async def debug_exact_update():
    """Debug by printing exactly what we're sending vs what works"""
    print("=== Debugging Exact Update Structure ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    # Get rules
    rules_response = await mm.get_transaction_rules()
    rules = rules_response.get("transactionRules", [])

    if rules:
        # Find the specific rule from your screenshot: rule for "numberbarn"
        target_rule = None
        for rule in rules:
            merchant_criteria = rule.get("merchantCriteria", [])
            for criteria in merchant_criteria:
                if "numberbarn" in criteria.get("value", "").lower():
                    target_rule = rule
                    break
            if target_rule:
                break

        if not target_rule:
            # Just use first rule
            target_rule = rules[0]

        print(f"Using rule ID: {target_rule.get('id')}")

        # Show what I'm building
        rule_input = {
            "id": target_rule.get("id"),
            "merchantCriteriaUseOriginalStatement": target_rule.get(
                "merchantCriteriaUseOriginalStatement", False
            ),
            "merchantCriteria": target_rule.get("merchantCriteria", []),
            "amountCriteria": target_rule.get("amountCriteria"),
            "categoryIds": target_rule.get("categoryIds"),
            "accountIds": target_rule.get("accountIds"),
            "reviewStatusAction": target_rule.get("reviewStatusAction"),
            "splitTransactionsAction": target_rule.get("splitTransactionsAction"),
            "applyToExistingTransactions": True,
        }

        # Handle setCategoryAction
        set_category_action = target_rule.get("setCategoryAction")
        if set_category_action:
            if isinstance(set_category_action, dict) and "id" in set_category_action:
                rule_input["setCategoryAction"] = set_category_action["id"]
            else:
                rule_input["setCategoryAction"] = set_category_action
        else:
            rule_input["setCategoryAction"] = None

        print("\nMy constructed input:")
        print(json.dumps(rule_input, indent=2))

        # Compare with working HAR example
        print("\n" + "=" * 50)
        print("Working HAR example:")
        working_example = {
            "id": "220723814124920059",
            "merchantCriteriaUseOriginalStatement": False,
            "merchantCriteria": [{"operator": "contains", "value": "numberbarn"}],
            "amountCriteria": None,
            "categoryIds": None,
            "accountIds": None,
            "setCategoryAction": "220719326595030610",
            "reviewStatusAction": None,
            "splitTransactionsAction": None,
            "applyToExistingTransactions": True,
        }
        print(json.dumps(working_example, indent=2))

        # Try the actual update with debug output
        print(f"\n" + "=" * 50)
        print("Testing actual update...")
        try:
            result = await mm.update_transaction_rule_retroactive(
                rule_data=target_rule, apply_to_existing_transactions=True
            )
            print("✅ Update succeeded!")
            print(f"Result: {result}")
        except Exception as e:
            print(f"❌ Update failed: {e}")

            # Try to show GraphQL query being constructed
            print("\nLet me check the GraphQL construction...")

    else:
        print("No rules found")


if __name__ == "__main__":
    asyncio.run(debug_exact_update())
