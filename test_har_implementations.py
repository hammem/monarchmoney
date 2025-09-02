#!/usr/bin/env python3
"""
Test the new HAR-based implementations
"""
import asyncio
import json
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_investment_performance():
    """Test the new Web_GetPortfolio implementation"""
    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    print("=== Testing get_investment_performance with real API ===")
    try:
        result = await mm.get_investment_performance()
        print("✅ get_investment_performance SUCCESS with real HAR operation!")

        # Extract key metrics
        portfolio = result.get("portfolio", {})
        performance = portfolio.get("performance", {})

        total_value = performance.get("totalValue", 0)
        total_change_percent = performance.get("totalChangePercent", 0)
        total_change_dollars = performance.get("totalChangeDollars", 0)
        one_day_change = performance.get("oneDayChangePercent", 0)

        print(f"   📊 Portfolio Metrics:")
        print(f"      💰 Total Value: ${total_value:,.2f}")
        print(
            f"      📈 Total Return: {total_change_percent:.2f}% (${total_change_dollars:,.2f})"
        )
        print(f"      📅 One Day Change: {one_day_change:.2f}%")

        # Show holdings summary
        holdings = portfolio.get("aggregateHoldings", {}).get("edges", [])
        print(f"      🏷️  Holdings: {len(holdings)} positions")

        return True

    except Exception as e:
        print(f"❌ get_investment_performance FAILED: {e}")
        return False


async def test_preview_rule():
    """Test the new PreviewTransactionRule implementation"""
    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    print("\n=== Testing preview_transaction_rule with real API ===")
    try:
        # Get a category ID for testing
        categories = await mm.get_transaction_categories()
        test_category_id = (
            categories["categories"][0]["id"] if categories.get("categories") else None
        )

        # Create a rule config matching the EXACT HAR structure with all required fields
        rule_config = {
            "merchantCriteriaUseOriginalStatement": False,
            "merchantCriteria": [{"operator": "contains", "value": "test"}],
            "setCategoryAction": test_category_id,
            "applyToExistingTransactions": False,
            "amountCriteria": None,
            "categoryIds": None,
            "accountIds": None,
        }

        result = await mm.preview_transaction_rule(rule_config)
        print("✅ preview_transaction_rule SUCCESS with real HAR operation!")

        # Extract preview data
        preview = result.get("transactionRulePreview", {})
        total_count = preview.get("totalCount", 0)
        results = preview.get("results", [])

        print(f"   🔍 Rule Preview Results:")
        print(f"      📊 Total Matches: {total_count}")
        print(f"      📝 Results Shown: {len(results)}")

        # Show sample matches
        for i, match in enumerate(results[:3]):
            transaction = match.get("transaction", {})
            merchant = transaction.get("merchant", {}).get("name", "Unknown")
            amount = transaction.get("amount", 0)
            print(f"      {i+1}. {merchant}: ${amount:,.2f}")

        return True

    except Exception as e:
        print(f"❌ preview_transaction_rule FAILED: {e}")
        return False


async def test_apply_rules():
    """Test the enhanced apply_rules_to_existing_transactions"""
    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    print("\n=== Testing enhanced apply_rules_to_existing_transactions ===")
    try:
        result = await mm.apply_rules_to_existing_transactions(limit=10)
        print("✅ apply_rules_to_existing_transactions SUCCESS!")

        print(f"   📊 Results: {result}")

        return True

    except Exception as e:
        print(f"❌ apply_rules_to_existing_transactions FAILED: {e}")
        return False


async def main():
    print("Testing HAR-based implementations...\n")

    # Test investment performance
    inv_success = await test_investment_performance()

    # Test rule preview
    rule_success = await test_preview_rule()

    # Test rule application
    apply_success = await test_apply_rules()

    print(f"\n=== Results Summary ===")
    print(f"Investment Performance: {'✅' if inv_success else '❌'}")
    print(f"Rule Preview: {'✅' if rule_success else '❌'}")
    print(f"Apply Rules: {'✅' if apply_success else '❌'}")

    if inv_success and rule_success:
        print("\n🎉 HAR-based implementations are working!")
        print("Both functions now use real MonarchMoney GraphQL operations!")


if __name__ == "__main__":
    asyncio.run(main())
