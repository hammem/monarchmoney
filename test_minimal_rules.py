#!/usr/bin/env python3

import asyncio
import json
import sys
import pytest

sys.path.insert(0, "/home/keith/src/monarchmoney")

from monarchmoney import MonarchMoney
from gql import gql


@pytest.mark.asyncio
async def test_minimal():
    """Test the absolute minimal transaction rules query."""
    mm = MonarchMoney()

    print("=== Login ===")
    try:
        await mm.interactive_login()
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return

    print("\n=== Test Working API Calls First ===")
    try:
        accounts = await mm.get_accounts()
        print(f"✓ get_accounts works: {len(accounts.get('accounts', []))} accounts")
    except Exception as e:
        print(f"✗ get_accounts failed: {e}")
        return

    print("\n=== Test Minimal Transaction Rules Query ===")
    try:
        # Simplest possible transaction rules query
        query = gql(
            """
            query GetTransactionRules {
                transactionRules {
                    id
                    __typename
                }
            }
        """
        )

        result = await mm.gql_call(
            operation="GetTransactionRules", graphql_query=query, variables={}
        )
        print(f"✓ Minimal rules query works: {result}")

    except Exception as e:
        print(f"✗ Minimal rules query failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_minimal())
