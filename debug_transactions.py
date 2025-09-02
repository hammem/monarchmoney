#!/usr/bin/env python3
"""
Debug transactions retrieval to see if we can get the 18,881 transactions
"""
import asyncio
from pathlib import Path
from monarchmoney import MonarchMoney


async def debug_transactions():
    """Debug transaction retrieval"""
    print("=== Debugging Transaction Retrieval ===")

    # Load session
    session_file = Path.home() / ".monarchmoney_session"
    mm = MonarchMoney()
    mm.load_session(str(session_file))

    # Test different ways to get transactions
    print("1. Testing get_transactions()...")
    try:
        result1 = await mm.get_transactions()
        transactions = result1.get("transactions", [])
        print(f"   Default: {len(transactions)} transactions")

        # Try with a large limit
        result2 = await mm.get_transactions(limit=5000)
        transactions2 = result2.get("transactions", [])
        print(f"   With limit=5000: {len(transactions2)} transactions")

        # Try with no limit specified but check total
        if "totalCount" in result1:
            print(f"   Total available: {result1['totalCount']}")
        elif "meta" in result1 and "total" in result1["meta"]:
            print(f"   Total available: {result1['meta']['total']}")

        # Check structure
        print(f"   Full result keys: {list(result1.keys())}")

        if transactions2:
            sample_tx = transactions2[0]
            print(
                f"   Sample transaction: {sample_tx.get('merchant', {}).get('name', 'No merchant')} - ${abs(sample_tx.get('amount', 0)):.2f}"
            )

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test get_transactions_summary
    print("\n2. Testing get_transactions_summary()...")
    try:
        summary = await mm.get_transactions_summary()
        print(f"   Summary keys: {list(summary.keys())}")
        if "transactionCount" in summary:
            print(f"   Transaction count from summary: {summary['transactionCount']}")
        elif "total" in summary:
            print(f"   Total from summary: {summary['total']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test using filters
    print("\n3. Testing get_transactions() with filters...")
    try:
        # Try with date range to get more transactions
        result3 = await mm.get_transactions(
            limit=1000, start_date="2020-01-01", end_date="2024-12-31"
        )
        transactions3 = result3.get("transactions", [])
        print(f"   With date range: {len(transactions3)} transactions")

        if transactions3:
            # Show date range of retrieved transactions
            dates = [tx.get("date") for tx in transactions3 if tx.get("date")]
            if dates:
                print(f"   Date range: {min(dates)} to {max(dates)}")

    except Exception as e:
        print(f"   ❌ Failed: {e}")


if __name__ == "__main__":
    asyncio.run(debug_transactions())
