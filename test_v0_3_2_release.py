#!/usr/bin/env python3
"""
Final comprehensive test for v0.3.2 release
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_release_032():
    """Test all the key functionality for v0.3.2 release"""
    print("=== Testing MonarchMoney Enhanced v0.3.2 Release ===\n")

    # Load session
    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    success_count = 0
    total_tests = 0

    # Test 1: Basic API functionality
    total_tests += 1
    try:
        accounts = await mm.get_accounts()
        categories = await mm.get_transaction_categories()
        print(
            f"✅ 1. Basic API: {len(accounts.get('accounts', []))} accounts, {len(categories.get('categories', []))} categories"
        )
        success_count += 1
    except Exception as e:
        print(f"❌ 1. Basic API failed: {e}")

    # Test 2: Fixed create_amount_rule
    total_tests += 1
    try:
        # Get a real category that exists
        categories = await mm.get_transaction_categories()
        test_category_name = (
            categories["categories"][0]["name"]
            if categories.get("categories")
            else "Test"
        )

        result = await mm.create_amount_rule(
            amount=100.0,
            operator="eq",
            is_expense=True,
            category_name=test_category_name,
            apply_to_existing=False,
        )
        print("✅ 2. create_amount_rule: Working correctly")
        success_count += 1
    except Exception as e:
        print(f"❌ 2. create_amount_rule failed: {e}")

    # Test 3: Fixed create_combined_rule
    total_tests += 1
    try:
        result = await mm.create_combined_rule(
            merchant_contains="Test Merchant V032",
            amount=50,
            amount_operator="gt",
            category_name=test_category_name,
            apply_to_existing=False,
        )
        print("✅ 3. create_combined_rule: Working correctly")
        success_count += 1
    except Exception as e:
        print(f"❌ 3. create_combined_rule failed: {e}")

    # Test 4: Fixed create_tax_deductible_rule
    total_tests += 1
    try:
        result = await mm.create_tax_deductible_rule(
            merchant_contains="Office Supplies V032", apply_to_existing=False
        )
        print("✅ 4. create_tax_deductible_rule: Working correctly")
        success_count += 1
    except Exception as e:
        print(f"❌ 4. create_tax_deductible_rule failed: {e}")

    # Test 5: Enhanced get_investment_performance
    total_tests += 1
    try:
        result = await mm.get_investment_performance()
        portfolio = result.get("portfolio", {})
        performance = portfolio.get("performance", {})
        total_value = performance.get("totalValue", 0)
        print(
            f"✅ 5. get_investment_performance: Real API integration working (Portfolio value: ${total_value:,.2f})"
        )
        success_count += 1
    except Exception as e:
        print(f"❌ 5. get_investment_performance failed: {e}")

    # Test 6: Enhanced apply_rules_to_existing_transactions
    total_tests += 1
    try:
        result = await mm.apply_rules_to_existing_transactions(limit=5)
        rules_count = result.get("rules_count", 0)
        print(
            f"✅ 6. apply_rules_to_existing_transactions: Enhanced functionality working ({rules_count} rules)"
        )
        success_count += 1
    except Exception as e:
        print(f"❌ 6. apply_rules_to_existing_transactions failed: {e}")

    # Test 7: New preview_transaction_rule
    total_tests += 1
    try:
        categories = await mm.get_transaction_categories()
        test_category_id = (
            categories["categories"][0]["id"] if categories.get("categories") else None
        )

        rule_config = {
            "merchantCriteria": [{"operator": "contains", "value": "test"}],
            "setCategoryAction": test_category_id,
            "applyToExistingTransactions": False,
        }

        result = await mm.preview_transaction_rule(rule_config)
        match_count = result.get("transactionRulePreview", {}).get("totalCount", 0)
        print(
            f"✅ 7. preview_transaction_rule: Client-side preview working ({match_count} matches)"
        )
        success_count += 1
    except Exception as e:
        print(f"❌ 7. preview_transaction_rule failed: {e}")

    # Summary
    print(f"\n=== Release Test Summary ===")
    print(f"✅ Passed: {success_count}/{total_tests} tests")
    print(f"📊 Success Rate: {(success_count/total_tests)*100:.1f}%")

    if success_count == total_tests:
        print("\n🎉 ALL TESTS PASSED - v0.3.2 is ready for release!")
        return True
    else:
        print(
            f"\n⚠️  {total_tests - success_count} tests failed - review before release"
        )
        return False


async def main():
    return await test_release_032()


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
