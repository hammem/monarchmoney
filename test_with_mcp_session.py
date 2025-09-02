#!/usr/bin/env python3
"""
Test broken functions using the existing MCP session file
"""
import asyncio
import os
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_with_mcp_session():
    """Test using the existing MCP session file"""
    print("=== Testing with MCP Session File ===")

    session_file = Path.home() / ".monarchmoney_session"

    if not session_file.exists():
        print(f"❌ No MCP session file found at {session_file}")
        print("   Run the monarch-money-mcp server first to create a session")
        return None

    print(f"✅ Found session file: {session_file}")

    # Create MonarchMoney instance and load session
    mm = MonarchMoney()

    try:
        mm.load_session(str(session_file))
        print("✅ Session loaded successfully")

        # Test if session is valid
        accounts = await mm.get_accounts()
        print(
            f"✅ Session is valid - found {len(accounts.get('accounts', []))} accounts"
        )

        return mm

    except Exception as e:
        print(f"❌ Failed to load or validate session: {e}")
        return None


async def test_broken_functions(mm):
    """Test the specific functions that were reported as broken"""
    print("\n=== Testing Reported Broken Functions ===")

    # Test basic API first to confirm everything works
    try:
        categories = await mm.get_transaction_categories()
        print(
            f"✅ Basic API confirmed: Found {len(categories.get('categories', []))} categories"
        )
    except Exception as e:
        print(f"❌ Basic API failed: {e}")
        return

    # Get a sample category for testing
    sample_category = None
    if categories.get("categories"):
        sample_category = categories["categories"][0]["name"]
        print(f"Using sample category: {sample_category}")

    # Test create_amount_rule
    print("\n1. Testing create_amount_rule...")
    try:
        result = await mm.create_amount_rule(
            amount=115.32,
            operator="eq",
            is_expense=False,
            category_name=sample_category if sample_category else "Food & Dining",
            apply_to_existing=False,
        )
        print(f"   ✅ create_amount_rule SUCCESS")

    except Exception as e:
        print(f"   ❌ create_amount_rule FAILED: {e}")

    # Test create_combined_rule
    print("\n2. Testing create_combined_rule...")
    try:
        result = await mm.create_combined_rule(
            merchant_contains="API Test Merchant",
            amount=200,
            amount_operator="gt",
            category_name=sample_category if sample_category else "Food & Dining",
            apply_to_existing=False,
        )
        print(f"   ✅ create_combined_rule SUCCESS")

    except Exception as e:
        print(f"   ❌ create_combined_rule FAILED: {e}")

    # Test create_tax_deductible_rule
    print("\n3. Testing create_tax_deductible_rule...")
    try:
        result = await mm.create_tax_deductible_rule(
            merchant_contains="API Test Business Expense", apply_to_existing=False
        )
        print(f"   ✅ create_tax_deductible_rule SUCCESS")

    except Exception as e:
        print(f"   ❌ create_tax_deductible_rule FAILED: {e}")

    # Test apply_rules_to_existing_transactions (likely broken)
    print("\n4. Testing apply_rules_to_existing_transactions...")
    try:
        result = await mm.apply_rules_to_existing_transactions()
        print(f"   ✅ apply_rules_to_existing_transactions SUCCESS: {result}")

    except Exception as e:
        print(f"   ❌ apply_rules_to_existing_transactions FAILED: {e}")
        if "Something went wrong while processing" in str(e):
            print(f"       ^ This looks like a fake GraphQL operation")

    # Test some other potentially problematic functions
    print("\n5. Testing other advanced functions...")

    try:
        print("   - Testing get_investment_performance...")
        result = await mm.get_investment_performance()
        print(f"     ✅ get_investment_performance works")
    except Exception as e:
        print(f"     ❌ get_investment_performance failed: {e}")
        if "Something went wrong while processing" in str(e):
            print(f"         ^ Likely another fake GraphQL operation")


async def main():
    """Main test runner"""
    print("Testing broken functions with MCP session...\n")

    mm = await test_with_mcp_session()
    if not mm:
        return

    await test_broken_functions(mm)

    print("\n=== Summary ===")
    print("This test will show us:")
    print("✅ Which functions actually work (probably most of them)")
    print("❌ Which functions are truly broken (likely fake GraphQL operations)")
    print("🔧 What needs to be fixed vs removed")


if __name__ == "__main__":
    asyncio.run(main())
