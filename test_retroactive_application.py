#!/usr/bin/env python3
"""
Test if retroactive rule application actually works in the API
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_retroactive_application():
    """Test if retroactive rule application actually works"""
    print("=== Testing Retroactive Rule Application ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    # Get some recent transactions to see what we have
    print("1. Checking recent transactions...")
    try:
        transactions = await mm.get_transactions(limit=20)
        recent_transactions = transactions.get("transactions", [])
        print(f"   Found {len(recent_transactions)} recent transactions")

        # Show a few examples
        for i, tx in enumerate(recent_transactions[:5]):
            merchant = tx.get("merchant", {}).get("name", "Unknown")
            amount = tx.get("amount", 0)
            category = tx.get("category", {}).get("name", "Uncategorized")
            print(f"   {i+1}. {merchant}: ${abs(amount):.2f} -> {category}")

    except Exception as e:
        print(f"   ❌ Failed to get transactions: {e}")
        return

    # Pick a merchant that appears in recent transactions
    if recent_transactions:
        test_merchant = recent_transactions[0].get("merchant", {}).get("name", "Test")
        test_amount = abs(recent_transactions[0].get("amount", 100))
        print(
            f"\n2. Will create rule for merchant '{test_merchant}' with amount > ${test_amount-50:.2f}"
        )
    else:
        test_merchant = "TestMerchant"
        test_amount = 50

    # Get categories
    categories = await mm.get_transaction_categories()
    test_category = (
        categories["categories"][0]["name"]
        if categories.get("categories")
        else "Food & Dining"
    )
    print(f"   Will categorize as: {test_category}")

    # Create rule WITHOUT retroactive application first
    print(f"\n3. Creating rule WITHOUT retroactive application...")
    try:
        result1 = await mm.create_combined_rule(
            merchant_contains=test_merchant,
            amount=test_amount - 50,
            amount_operator="gt",
            category_name=test_category,
            apply_to_existing=False,  # NOT retroactive
        )
        print("   ✅ Rule created without retroactive application")

        # Now create the same rule WITH retroactive application
        print(f"\n4. Creating rule WITH retroactive application...")
        result2 = await mm.create_combined_rule(
            merchant_contains=test_merchant
            + "2",  # Slightly different to avoid duplicate
            amount=test_amount - 50,
            amount_operator="gt",
            category_name=test_category,
            apply_to_existing=True,  # WITH retroactive
        )
        print("   ✅ Rule created WITH retroactive application")

        # Check if transactions were actually updated
        print(f"\n5. Checking if transactions were retroactively updated...")
        updated_transactions = await mm.get_transactions(limit=20)

        # Look for changes in categorization
        changes_found = 0
        for tx in updated_transactions.get("transactions", []):
            merchant = tx.get("merchant", {}).get("name", "")
            amount = abs(tx.get("amount", 0))
            category = tx.get("category", {}).get("name", "")

            if (
                test_merchant.lower() in merchant.lower()
                and amount > test_amount - 50
                and category == test_category
            ):
                changes_found += 1

        print(
            f"   Found {changes_found} transactions that match and have been categorized"
        )

        if changes_found > 0:
            print("   ✅ Retroactive application appears to WORK!")
        else:
            print("   ❌ Retroactive application does NOT seem to work")

    except Exception as e:
        print(f"   ❌ Failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_retroactive_application())
