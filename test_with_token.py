#!/usr/bin/env python3
"""
Test functions using a manually provided token
"""
import asyncio
import sys
from monarchmoney import MonarchMoney


async def test_with_manual_token():
    """Test using a manually provided token"""
    print("=== Testing with Manual Token ===")
    print("To get a token:")
    print("1. Login to https://app.monarchmoney.com in your browser")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Network tab")
    print("4. Make any request (refresh page)")
    print("5. Look for 'authorization' header in requests")
    print("6. Copy the token (after 'Token ')")
    print()

    token = input("Paste your token here (or press Enter to skip): ").strip()

    if not token:
        print("No token provided, skipping manual test")
        return None

    # Create MonarchMoney instance with token
    mm = MonarchMoney(token=token)

    # Test session
    session_info = mm.get_session_info()
    print(f"Session info: {session_info}")

    if not session_info.get("valid"):
        print("❌ Token appears to be invalid")
        return None

    print("✅ Token is valid!")
    return mm


async def test_broken_functions(mm):
    """Test the specific functions that were reported as broken"""
    print("\n=== Testing Broken Helper Functions ===")

    # Test basic API first
    try:
        accounts = await mm.get_accounts()
        print(f"✓ Basic API works: Found {len(accounts.get('accounts', []))} accounts")

        categories = await mm.get_transaction_categories()
        print(
            f"✓ Categories work: Found {len(categories.get('categories', []))} categories"
        )
    except Exception as e:
        print(f"✗ Basic API failed: {e}")
        return

    # Test create_amount_rule
    try:
        print("\n1. Testing create_amount_rule...")
        result = await mm.create_amount_rule(
            amount=115.32,
            operator="eq",
            is_expense=False,
            category_name="Food & Dining",
            apply_to_existing=False,
        )
        print(f"   ✓ create_amount_rule SUCCESS")

    except Exception as e:
        print(f"   ✗ create_amount_rule FAILED: {e}")

    # Test create_combined_rule
    try:
        print("\n2. Testing create_combined_rule...")
        result = await mm.create_combined_rule(
            merchant_contains="Test Merchant",
            amount=200,
            amount_operator="gt",
            category_name="Food & Dining",
            apply_to_existing=False,
        )
        print(f"   ✓ create_combined_rule SUCCESS")

    except Exception as e:
        print(f"   ✗ create_combined_rule FAILED: {e}")

    # Test create_tax_deductible_rule
    try:
        print("\n3. Testing create_tax_deductible_rule...")
        result = await mm.create_tax_deductible_rule(
            merchant_contains="Test Business", apply_to_existing=False
        )
        print(f"   ✓ create_tax_deductible_rule SUCCESS")

    except Exception as e:
        print(f"   ✗ create_tax_deductible_rule FAILED: {e}")

    # Test apply_rules_to_existing_transactions
    try:
        print("\n4. Testing apply_rules_to_existing_transactions...")
        result = await mm.apply_rules_to_existing_transactions()
        print(f"   ✓ apply_rules_to_existing_transactions SUCCESS")

    except Exception as e:
        print(f"   ✗ apply_rules_to_existing_transactions FAILED: {e}")
        print(f"       This is likely a fake GraphQL operation")


async def main():
    """Main test runner"""
    print("Testing broken functions with manual token...\n")

    mm = await test_with_manual_token()
    if mm:
        await test_broken_functions(mm)
    else:
        print("\n❌ No valid session available")
        print("\nAlternatively, you can:")
        print("1. Use the browser to login to MonarchMoney")
        print("2. Export a session token")
        print("3. Run this test with that token")


if __name__ == "__main__":
    asyncio.run(main())
