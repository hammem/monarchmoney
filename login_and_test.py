#!/usr/bin/env python3

import asyncio
import sys
import json

sys.path.insert(0, "/home/keith/src/monarchmoney")

from monarchmoney import MonarchMoney


async def login_and_test():
    """Login and test transaction rules functionality."""
    mm = MonarchMoney()

    print("=== Interactive Login ===")
    try:
        await mm.interactive_login()
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return

    print("\n=== Testing get_transaction_rules ===")
    try:
        rules = await mm.get_transaction_rules()
        rule_count = len(rules.get("transactionRules", []))
        print(f"✓ Successfully retrieved {rule_count} rules")

        if rule_count > 0:
            print("Sample rule structure:")
            sample_rule = rules["transactionRules"][0]
            print(
                json.dumps(
                    {
                        "id": sample_rule.get("id"),
                        "order": sample_rule.get("order"),
                        "merchantCriteria": sample_rule.get("merchantCriteria"),
                        "setCategoryAction": sample_rule.get("setCategoryAction"),
                    },
                    indent=2,
                )
            )

    except Exception as e:
        print(f"✗ get_transaction_rules failed: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n=== Testing get_transaction_categories ===")
    try:
        categories = await mm.get_transaction_categories()
        cat_count = len(categories.get("categories", []))
        print(f"✓ Successfully retrieved {cat_count} categories")

        # Find a test category
        test_category = None
        for cat in categories.get("categories", []):
            if cat.get("name") in ["Shopping", "Utilities", "Gas & Electric"]:
                test_category = cat
                break

        if test_category:
            print(
                f"Using test category: {test_category['name']} (ID: {test_category['id']})"
            )
        else:
            print("No suitable test category found")
            return

    except Exception as e:
        print(f"✗ get_transaction_categories failed: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n=== Testing create_categorization_rule ===")
    try:
        result = await mm.create_categorization_rule(
            merchant_contains="CLAUDE_DEBUG_TEST",
            category_name=test_category["name"],
            apply_to_existing=False,
        )
        print(f"✓ Categorization rule created: {json.dumps(result, indent=2)}")

        # Check for errors
        if result.get("createTransactionRuleV2", {}).get("errors"):
            errors = result["createTransactionRuleV2"]["errors"]
            print(f"⚠️ API returned errors: {json.dumps(errors, indent=2)}")

    except Exception as e:
        print(f"✗ create_categorization_rule failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n=== Checking for test rules to clean up ===")
    try:
        final_rules = await mm.get_transaction_rules()
        for rule in final_rules.get("transactionRules", []):
            merchant_criteria = rule.get("merchantCriteria", [])
            for criteria in merchant_criteria:
                if "CLAUDE_DEBUG_TEST" in criteria.get("value", ""):
                    print(f"Found test rule {rule['id']} - cleaning up...")
                    deleted = await mm.delete_transaction_rule(rule["id"])
                    print(f"Delete result: {deleted}")

    except Exception as e:
        print(f"✗ Cleanup failed: {e}")


if __name__ == "__main__":
    asyncio.run(login_and_test())
