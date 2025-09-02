#!/usr/bin/env python3
"""
Comprehensive test script for all MonarchMoney operations.
This will test each function systematically with a working account.
"""
import asyncio
import sys
from monarchmoney import MonarchMoney


async def test_basic_operations():
    """Test basic API operations that should work"""
    mm = MonarchMoney()

    try:
        print("=== Testing Basic Operations ===")

        # Test authentication (non-async method)
        print("1. Testing session info...")
        session_info = mm.get_session_info()
        print(f"   ✅ Session info: {session_info}")

        # Test categories
        print("2. Testing categories...")
        categories = await mm.get_transaction_categories()
        print(f"   ✅ Found {len(categories.get('categories', []))} categories")

        # Test accounts
        print("3. Testing accounts...")
        accounts = await mm.get_accounts()
        print(f"   ✅ Found {len(accounts.get('accounts', []))} accounts")

        # Test transactions (limit to recent)
        print("4. Testing transactions...")
        transactions = await mm.get_transactions(limit=5)
        print(
            f"   ✅ Found {len(transactions.get('transactions', []))} recent transactions"
        )

        return True

    except Exception as e:
        print(f"   ❌ Basic operations failed: {e}")
        return False


async def test_working_rule_functions():
    """Test the rule functions that we know work"""
    mm = MonarchMoney()

    try:
        print("\n=== Testing Working Rule Functions ===")

        # Test basic categorization rule (known to work)
        print("1. Testing create_categorization_rule...")
        result = await mm.create_categorization_rule(
            merchant="Test Merchant for API Test", category_name="Food & Dining"
        )
        print(f"   ✅ Created categorization rule")

        # Test direct create_transaction_rule (known to work)
        print("2. Testing direct create_transaction_rule...")
        result = await mm.create_transaction_rule(
            merchant_criteria=[{"operator": "contains", "value": "API Test Direct"}],
            apply_to_existing_transactions=False,
        )
        print(f"   ✅ Created direct transaction rule")

        return True

    except Exception as e:
        print(f"   ❌ Working rule functions failed: {e}")
        return False


async def test_broken_helper_functions():
    """Test the helper functions that are currently broken"""
    mm = MonarchMoney()

    print("\n=== Testing Broken Helper Functions ===")

    # Test create_amount_rule
    try:
        print("1. Testing create_amount_rule...")
        result = await mm.create_amount_rule(
            amount=115.32,
            operator="eq",
            is_expense=False,
            category_name="Food & Dining",
            apply_to_existing=False,
        )
        print(f"   ✅ create_amount_rule works!")

    except Exception as e:
        print(f"   ❌ create_amount_rule failed: {e}")

    # Test create_combined_rule
    try:
        print("2. Testing create_combined_rule...")
        result = await mm.create_combined_rule(
            merchant_contains="Airbnb",
            amount=200,
            amount_operator="gt",
            category_name="Travel",
            apply_to_existing=False,
        )
        print(f"   ✅ create_combined_rule works!")

    except Exception as e:
        print(f"   ❌ create_combined_rule failed: {e}")

    # Test create_tax_deductible_rule
    try:
        print("3. Testing create_tax_deductible_rule...")
        result = await mm.create_tax_deductible_rule(
            merchant_contains="Office Supplies", apply_to_existing=False
        )
        print(f"   ✅ create_tax_deductible_rule works!")

    except Exception as e:
        print(f"   ❌ create_tax_deductible_rule failed: {e}")

    # Test apply_rules_to_existing_transactions
    try:
        print("4. Testing apply_rules_to_existing_transactions...")
        result = await mm.apply_rules_to_existing_transactions()
        print(f"   ✅ apply_rules_to_existing_transactions works!")

    except Exception as e:
        print(f"   ❌ apply_rules_to_existing_transactions failed: {e}")


async def analyze_broken_functions():
    """Analyze what's actually wrong with the broken functions"""
    mm = MonarchMoney()

    print("\n=== Analyzing Broken Function Issues ===")

    # Let's trace through create_amount_rule step by step
    try:
        print("1. Tracing create_amount_rule execution...")

        # Step 1: Get categories
        print("   - Getting categories...")
        categories = await mm.get_transaction_categories()
        food_category_id = None
        for cat in categories.get("categories", []):
            if cat.get("name", "").lower() == "food & dining":
                food_category_id = cat.get("id")
                break

        if food_category_id:
            print(f"   - Found Food & Dining category: {food_category_id}")
        else:
            print("   - Food & Dining category not found, using first available...")
            food_category_id = (
                categories["categories"][0]["id"]
                if categories.get("categories")
                else None
            )

        if not food_category_id:
            print("   ❌ No categories available!")
            return

        # Step 2: Call create_transaction_rule directly with the same params
        print("   - Calling create_transaction_rule directly...")
        amount_criteria = {
            "operator": "eq",
            "isExpense": False,
            "value": 115.32,
        }

        result = await mm.create_transaction_rule(
            amount_criteria=amount_criteria,
            set_category_action=food_category_id,
            apply_to_existing_transactions=False,
        )
        print(f"   ✅ Direct call worked! The helper functions should work too.")

    except Exception as e:
        print(f"   ❌ Direct call failed: {e}")
        print(f"      This suggests the issue is in create_transaction_rule itself")


async def main():
    """Run all tests systematically"""
    print("Starting comprehensive MonarchMoney API test...")

    # Test 1: Basic operations
    basic_success = await test_basic_operations()
    if not basic_success:
        print("❌ Basic operations failed - cannot continue")
        return

    # Test 2: Working rule functions
    working_success = await test_working_rule_functions()
    if not working_success:
        print("❌ Even known-working functions failed - check authentication")
        return

    # Test 3: Broken helper functions
    await test_broken_helper_functions()

    # Test 4: Analyze what's actually broken
    await analyze_broken_functions()

    print("\n=== Test Summary ===")
    print("This script will help identify:")
    print("1. Whether basic authentication and API access works")
    print("2. Whether known-good functions still work")
    print("3. Specific error messages from broken functions")
    print("4. Whether the issue is in helpers or in create_transaction_rule")


if __name__ == "__main__":
    asyncio.run(main())
