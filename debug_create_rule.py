#!/usr/bin/env python3
"""
Debug the create_transaction_rule issue specifically
"""
import asyncio
import json
from pathlib import Path
from monarchmoney import MonarchMoney
from gql import gql


async def debug_create_rule():
    """Debug what's wrong with create_transaction_rule"""
    print("=== Loading MCP Session ===")

    mm = MonarchMoney()
    session_file = Path.home() / ".monarchmoney_session"
    mm.load_session(str(session_file))

    # Verify session works
    accounts = await mm.get_accounts()
    print(f"✅ Session valid - {len(accounts.get('accounts', []))} accounts")

    # Test 1: Try the exact HAR query structure
    print("\n=== Test 1: Exact HAR Query ===")
    try:
        query = gql(
            """
            mutation Common_CreateTransactionRuleMutationV2($input: CreateTransactionRuleInput!) {
                createTransactionRuleV2(input: $input) {
                    errors {
                        ...PayloadErrorFields
                        __typename
                    }
                    __typename
                }
            }

            fragment PayloadErrorFields on PayloadError {
                fieldErrors {
                    field
                    messages
                    __typename
                }
                message
                code
                __typename
            }
        """
        )

        # Use exact variables from HAR
        variables = {
            "input": {
                "categoryIds": None,
                "accountIds": None,
                "merchantCriteria": [
                    {"operator": "contains", "value": "API Debug Test"}
                ],
                "amountCriteria": None,
                "merchantCriteriaUseOriginalStatement": False,
                "addTagsAction": None,
                "splitTransactionsAction": None,
                "applyToExistingTransactions": False,
                "setCategoryAction": None,
            }
        }

        print("Calling GraphQL directly...")
        result = await mm.gql_call(
            operation="Common_CreateTransactionRuleMutationV2",
            graphql_query=query,
            variables=variables,
        )

        print(f"✅ Direct GraphQL call SUCCESS: {result}")

    except Exception as e:
        print(f"❌ Direct GraphQL call FAILED: {e}")

        # Test 2: Try minimal query to isolate issue
        print("\n=== Test 2: Minimal Query ===")
        try:
            minimal_query = gql(
                """
                mutation TestCreate($input: CreateTransactionRuleInput!) {
                    createTransactionRuleV2(input: $input) {
                        __typename
                    }
                }
            """
            )

            result = await mm.gql_call(
                operation="TestCreate",
                graphql_query=minimal_query,
                variables=variables,
            )
            print(f"✅ Minimal query SUCCESS: {result}")

        except Exception as e2:
            print(f"❌ Minimal query FAILED: {e2}")

            # Test 3: Check if input type is wrong
            print("\n=== Test 3: Try different input type ===")
            try:
                alt_query = gql(
                    """
                    mutation TestCreate2($input: CreateTransactionRuleInputV2!) {
                        createTransactionRuleV2(input: $input) {
                            __typename
                        }
                    }
                """
                )

                result = await mm.gql_call(
                    operation="TestCreate2",
                    graphql_query=alt_query,
                    variables=variables,
                )
                print(f"✅ Alternative input type SUCCESS: {result}")

            except Exception as e3:
                print(f"❌ Alternative input type FAILED: {e3}")

                print("\n=== Diagnosis ===")
                print("Issue appears to be:")
                print("1. GraphQL input type name might be wrong")
                print("2. Required fields might be missing")
                print("3. Field names might have changed")


if __name__ == "__main__":
    asyncio.run(debug_create_rule())
