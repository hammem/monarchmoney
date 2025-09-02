#!/usr/bin/env python3
"""
Debug the PreviewTransactionRule schema issue
"""
import asyncio
import json
from pathlib import Path
from monarchmoney import MonarchMoney
from gql import gql


async def debug_preview_rule_schema():
    """Debug the exact GraphQL schema issue"""
    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    print("=== Debugging PreviewTransactionRule Schema ===")

    # Test 1: Try minimal query without the problematic input type
    print("\n1. Testing with minimal query structure...")
    try:
        # Just test if we can make a basic GraphQL call
        basic_query = gql(
            """
            query Test {
                __typename
            }
        """
        )

        result = await mm.gql_call(
            operation="Test", graphql_query=basic_query, variables={}
        )
        print("✅ Basic GraphQL call works")

    except Exception as e:
        print(f"❌ Basic GraphQL failed: {e}")
        return

    # Test 2: Try the exact HAR query structure but with simpler content
    print("\n2. Testing exact HAR query structure...")
    try:
        # Use exact query from HAR but minimal variables
        har_query = gql(
            """
            query PreviewTransactionRule($rule: TransactionRulePreviewInput!, $offset: Int) {
              transactionRulePreview(input: $rule) {
                totalCount
                __typename
              }
            }
        """
        )

        # Get a real category ID
        categories = await mm.get_transaction_categories()
        test_category_id = (
            categories["categories"][0]["id"]
            if categories.get("categories")
            else "test"
        )

        # Use exact HAR variable structure
        variables = {
            "rule": {
                "merchantCriteriaUseOriginalStatement": False,
                "merchantCriteria": [{"operator": "contains", "value": "test"}],
                "setCategoryAction": test_category_id,
                "applyToExistingTransactions": False,
            },
            "offset": None,
        }

        print(f"Variables: {json.dumps(variables, indent=2)}")

        result = await mm.gql_call(
            operation="PreviewTransactionRule",
            graphql_query=har_query,
            variables=variables,
        )
        print("✅ HAR query structure works!")
        print(f"Result: {result}")

    except Exception as e:
        print(f"❌ HAR query failed: {e}")

        # Test 3: Maybe the type name is wrong? Try variations
        print("\n3. Testing type name variations...")

        for type_name in [
            "TransactionRuleInput",
            "RulePreviewInput",
            "TransactionRulePreview",
        ]:
            try:
                test_query = gql(
                    f"""
                    query TestType($rule: {type_name}!) {{
                        __typename
                    }}
                """
                )
                print(f"✅ Type {type_name} parsed successfully")
                break
            except Exception as e2:
                print(f"❌ Type {type_name} failed: {e2}")


async def main():
    await debug_preview_rule_schema()


if __name__ == "__main__":
    asyncio.run(main())
