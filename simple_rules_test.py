#!/usr/bin/env python3

import asyncio
import sys
import json

sys.path.insert(0, "/home/keith/src/monarchmoney")

from monarchmoney import MonarchMoney


async def main():
    """Simple test that you can run manually with your credentials."""

    # You'll need to provide your email and password here
    EMAIL = input("Enter your MonarchMoney email: ")
    PASSWORD = input("Enter your MonarchMoney password: ")

    mm = MonarchMoney()

    try:
        print("Logging in...")
        await mm.login(EMAIL, PASSWORD)
        print("✓ Login successful")
    except Exception as e:
        if "RequireMFAException" in str(type(e)):
            mfa_code = input("Enter MFA code: ")
            await mm.multi_factor_authenticate(EMAIL, PASSWORD, mfa_code)
            print("✓ MFA login successful")
        else:
            print(f"✗ Login failed: {e}")
            return

    # Test 1: Get existing rules
    print("\n=== Test 1: Get existing rules ===")
    try:
        rules = await mm.get_transaction_rules()
        print(f"✓ Retrieved {len(rules.get('transactionRules', []))} existing rules")

        # Show the exact API response structure
        print("Full API response structure:")
        print(
            json.dumps(rules, indent=2)[:1000] + "..."
            if len(json.dumps(rules, indent=2)) > 1000
            else json.dumps(rules, indent=2)
        )

    except Exception as e:
        print(f"✗ get_transaction_rules failed: {e}")
        import traceback

        traceback.print_exc()

    # Test 2: Get categories
    print("\n=== Test 2: Get categories for testing ===")
    try:
        categories = await mm.get_transaction_categories()
        print(f"✓ Retrieved {len(categories.get('categories', []))} categories")

        # Find any category for testing
        test_category_id = None
        if categories.get("categories"):
            test_category_id = categories["categories"][0]["id"]
            test_category_name = categories["categories"][0]["name"]
            print(f"Using test category: {test_category_name} (ID: {test_category_id})")

    except Exception as e:
        print(f"✗ get_transaction_categories failed: {e}")
        import traceback

        traceback.print_exc()
        return

    if not test_category_id:
        print("No categories available for testing")
        return

    # Test 3: Try to create a rule with minimal parameters
    print("\n=== Test 3: Create minimal rule ===")
    try:
        result = await mm.create_transaction_rule(
            merchant_criteria=[
                {"operator": "contains", "value": "CLAUDE_TEST_MINIMAL"}
            ],
            set_category_action=test_category_id,
        )
        print("✓ Minimal rule creation:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"✗ create_transaction_rule minimal failed: {e}")
        import traceback

        traceback.print_exc()

    # Test 4: Try the helper method
    print("\n=== Test 4: Create categorization rule ===")
    try:
        result = await mm.create_categorization_rule(
            merchant_contains="CLAUDE_TEST_HELPER", category_name=test_category_name
        )
        print("✓ Categorization rule creation:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"✗ create_categorization_rule failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n=== Debugging complete ===")
    print(
        "Please check the output above for any API errors or unexpected response structures."
    )


if __name__ == "__main__":
    asyncio.run(main())
