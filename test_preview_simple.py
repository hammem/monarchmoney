#!/usr/bin/env python3
"""
Simple test of just the preview function
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_preview_simple():
    """Test just the preview function"""
    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    print("=== Testing preview_transaction_rule alone ===")

    # Get categories first
    categories = await mm.get_transaction_categories()
    test_category_id = (
        categories["categories"][0]["id"] if categories.get("categories") else None
    )
    print(f"✅ Got categories, using: {test_category_id}")

    # Simple rule config
    rule_config = {
        "merchantCriteria": [{"operator": "contains", "value": "test"}],
        "setCategoryAction": test_category_id,
        "applyToExistingTransactions": False,
    }

    try:
        result = await mm.preview_transaction_rule(rule_config)
        print("✅ preview_transaction_rule SUCCESS!")
        print(f"   📊 Found {result['transactionRulePreview']['totalCount']} matches")

    except Exception as e:
        print(f"❌ preview_transaction_rule FAILED: {e}")


if __name__ == "__main__":
    asyncio.run(test_preview_simple())
