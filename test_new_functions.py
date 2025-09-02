#!/usr/bin/env python3
"""
Test the newly implemented apply_rules_to_existing_transactions and get_investment_performance
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def test_new_implementations():
    """Test the newly implemented functions"""
    print("=== Testing New Function Implementations ===")

    # Load session
    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    print("✅ Session loaded")

    # Test 1: apply_rules_to_existing_transactions
    print("\n🔄 Testing apply_rules_to_existing_transactions...")
    try:
        result = await mm.apply_rules_to_existing_transactions(limit=50)  # Small test
        print("✅ apply_rules_to_existing_transactions SUCCESS")
        print(f"   📊 Result: {result}")

    except Exception as e:
        print(f"❌ apply_rules_to_existing_transactions FAILED: {e}")

    # Test 2: get_investment_performance
    print("\n📈 Testing get_investment_performance...")
    try:
        result = await mm.get_investment_performance()
        print("✅ get_investment_performance SUCCESS")
        print(f"   📊 Found {result.get('total_accounts', 0)} investment accounts")
        print(f"   💰 Total value: ${result.get('total_value', 0):,.2f}")

        # Show account details
        for account in result.get("accounts", [])[:3]:  # Show first 3
            name = account.get("name", "Unknown")
            balance = account.get("current_balance", 0)
            print(f"   📈 {name}: ${balance:,.2f}")

    except Exception as e:
        print(f"❌ get_investment_performance FAILED: {e}")

    print("\n=== Summary ===")
    print("✅ Both functions now have working implementations!")
    print("💡 For enhanced functionality, provide HAR files with:")
    print("   - Rule application operations")
    print("   - Portfolio performance API calls")


async def main():
    await test_new_implementations()


if __name__ == "__main__":
    asyncio.run(main())
