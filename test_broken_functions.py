#!/usr/bin/env python3
"""
Test the specific broken functions with working authentication
"""
import asyncio
import os
import sys
import json
import getpass
import oathtool
from monarchmoney import MonarchMoney
from monarchmoney.monarchmoney import RequireMFAException


async def login_with_creds():
    """Login using credentials from environment"""
    mm = MonarchMoney()

    email = os.getenv("MONARCH_EMAIL", "keith@hadm.net")
    password = os.getenv("MONARCH_PASSWORD", "yfb9rku9JVU.fyq2khp")
    mfa_secret = os.getenv("MONARCH_MFA_SECRET", "VMM2SWKO32KLP7HK6BFJ5LQTIWADMTBM")

    print(f"=== Login Attempt for {email} ===")

    try:
        await mm.login(email, password)
        print("✓ Initial login successful")
    except RequireMFAException:
        print("🔐 MFA required, generating code...")
        mfa_code = oathtool.generate_otp(mfa_secret)
        print(f"Generated MFA code: {mfa_code}")

        try:
            await mm.multi_factor_authenticate(email, password, mfa_code)
            print("✓ MFA authentication successful")
        except Exception as e:
            print(f"✗ MFA failed: {e}")

            # Try interactive login as fallback
            print("Falling back to interactive login...")
            try:
                await mm.interactive_login(email, password)
                print("✓ Interactive login successful")
            except Exception as e2:
                print(f"✗ Interactive login also failed: {e2}")
                return None
    except Exception as e:
        print(f"✗ Login failed: {e}")

        # Try interactive login as fallback
        print("Trying interactive login...")
        try:
            await mm.interactive_login(email, password)
            print("✓ Interactive login successful")
        except Exception as e2:
            print(f"✗ Interactive login also failed: {e2}")
            return None

    # Verify session
    session_info = mm.get_session_info()
    print(f"Session info: {session_info}")

    if session_info.get("valid"):
        print("✓ Session is valid")
        return mm
    else:
        print("✗ Session is invalid")
        return None


async def test_basic_api(mm):
    """Test basic API functions that should work"""
    print("\n=== Testing Basic API Functions ===")

    try:
        # Test accounts
        accounts = await mm.get_accounts()
        print(f"✓ get_accounts: Found {len(accounts.get('accounts', []))} accounts")

        # Test categories
        categories = await mm.get_transaction_categories()
        print(
            f"✓ get_transaction_categories: Found {len(categories.get('categories', []))} categories"
        )

        # Test transactions
        transactions = await mm.get_transactions(limit=5)
        print(
            f"✓ get_transactions: Found {len(transactions.get('transactions', []))} recent transactions"
        )

        return True
    except Exception as e:
        print(f"✗ Basic API test failed: {e}")
        return False


async def test_broken_functions(mm):
    """Test the specific functions that were reported as broken"""
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
        print(f"   ✓ create_amount_rule SUCCESS: {result}")

    except Exception as e:
        print(f"   ✗ create_amount_rule FAILED: {e}")

    # Test create_combined_rule
    try:
        print("2. Testing create_combined_rule...")
        result = await mm.create_combined_rule(
            merchant_contains="Airbnb Test",
            amount=200,
            amount_operator="gt",
            category_name="Travel",
            apply_to_existing=False,
        )
        print(f"   ✓ create_combined_rule SUCCESS: {result}")

    except Exception as e:
        print(f"   ✗ create_combined_rule FAILED: {e}")

    # Test create_tax_deductible_rule
    try:
        print("3. Testing create_tax_deductible_rule...")
        result = await mm.create_tax_deductible_rule(
            merchant_contains="Office Supplies Test", apply_to_existing=False
        )
        print(f"   ✓ create_tax_deductible_rule SUCCESS: {result}")

    except Exception as e:
        print(f"   ✗ create_tax_deductible_rule FAILED: {e}")

    # Test apply_rules_to_existing_transactions
    try:
        print("4. Testing apply_rules_to_existing_transactions...")
        result = await mm.apply_rules_to_existing_transactions()
        print(f"   ✓ apply_rules_to_existing_transactions SUCCESS: {result}")

    except Exception as e:
        print(f"   ✗ apply_rules_to_existing_transactions FAILED: {e}")


async def main():
    """Main test runner"""
    print("Starting comprehensive broken functions test...\n")

    # Step 1: Login
    mm = await login_with_creds()
    if not mm:
        print("❌ Could not establish authenticated session")
        return

    # Step 2: Test basic API
    basic_success = await test_basic_api(mm)
    if not basic_success:
        print("❌ Basic API functions failed - cannot continue")
        return

    # Step 3: Test broken functions
    await test_broken_functions(mm)

    print("\n=== Test Complete ===")
    print("This will show us exactly which functions work vs are actually broken")


if __name__ == "__main__":
    asyncio.run(main())
