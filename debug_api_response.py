#!/usr/bin/env python3

import asyncio
import json
import sys
from typing import Dict, Any

sys.path.insert(0, "/home/keith/src/monarchmoney")

from monarchmoney import MonarchMoney


class DebugMonarchMoney(MonarchMoney):
    """Debug version that logs all GraphQL responses."""

    async def gql_call(
        self,
        operation: str,
        graphql_query,
        variables: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        """Debug version that logs all requests and responses."""
        print(f"\n=== GraphQL Call: {operation} ===")
        print(f"Variables: {json.dumps(variables, indent=2)}")

        try:
            result = await super().gql_call(operation, graphql_query, variables)
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        except Exception as e:
            print(f"Exception: {e}")
            print(f"Exception type: {type(e)}")
            import traceback

            traceback.print_exc()
            raise


async def test_debug():
    """Test with full debugging output."""
    mm = DebugMonarchMoney()

    print("=== Login ===")
    try:
        await mm.interactive_login()
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return

    print("\n=== Get Categories (for testing) ===")
    try:
        categories = await mm.get_transaction_categories()
        if categories.get("categories"):
            test_category = categories["categories"][0]
            print(
                f"Using test category: {test_category['name']} (ID: {test_category['id']})"
            )
        else:
            print("No categories found")
            return
    except Exception as e:
        print(f"✗ get_transaction_categories failed: {e}")
        return

    print("\n=== Test Create Transaction Rule ===")
    try:
        result = await mm.create_transaction_rule(
            merchant_criteria=[{"operator": "contains", "value": "DEBUG_TEST_2025"}],
            set_category_action=test_category["id"],
            apply_to_existing_transactions=False,
        )
        print("✓ create_transaction_rule completed")

    except Exception as e:
        print(f"✗ create_transaction_rule failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n=== Test Create Categorization Rule ===")
    try:
        result = await mm.create_categorization_rule(
            merchant_contains="DEBUG_HELPER_2025",
            category_name=test_category["name"],
            apply_to_existing=False,
        )
        print("✓ create_categorization_rule completed")

    except Exception as e:
        print(f"✗ create_categorization_rule failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_debug())
