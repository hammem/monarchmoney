#!/usr/bin/env python3

import asyncio
import json
import sys
from pprint import pprint

sys.path.insert(0, "/home/keith/src/monarchmoney")

from monarchmoney import MonarchMoney
from gql import gql


async def debug_graphql_operations():
    """Debug GraphQL operations by examining the structure."""
    mm = MonarchMoney()
    
    print("=== Debugging GraphQL Transaction Rules Operations ===")
    
    # Check the create_transaction_rule query structure
    print("\n1. CREATE TRANSACTION RULE QUERY:")
    create_query = gql(
        """
        mutation Common_CreateTransactionRuleMutationV2($input: CreateTransactionRuleInput!) {
            createTransactionRuleV2(input: $input) {
                errors {
                    fieldErrors {
                        field
                        messages
                        __typename
                    }
                    message
                    code
                    __typename
                }
                __typename
            }
        }
        """
    )
    print(f"Query AST: {create_query}")
    
    # Show the input structure we're sending
    print("\n2. SAMPLE INPUT STRUCTURE:")
    sample_input = {
        "merchantCriteriaUseOriginalStatement": False,
        "applyToExistingTransactions": False,
        "merchantCriteria": [{"operator": "contains", "value": "TEST"}],
        "amountCriteria": None,
        "categoryIds": None,
        "accountIds": None,
        "setCategoryAction": "test-category-id",
        "addTagsAction": None,
        "setMerchantAction": None,
        "splitTransactionsAction": None,
    }
    print(json.dumps({"input": sample_input}, indent=2))
    
    # Check the get_transaction_rules query
    print("\n3. GET TRANSACTION RULES QUERY:")
    get_query = gql(
        """
        query GetTransactionRules {
            transactionRules {
                id
                order
                merchantCriteria {
                    operator
                    value
                    __typename
                }
                amountCriteria {
                    operator
                    value
                    __typename
                }
                categoryIds
                accountIds
                setCategoryAction
                addTagsAction
                setMerchantAction
                splitTransactionsAction {
                    splits {
                        id
                        amount
                        categoryId
                        __typename
                    }
                    __typename
                }
                merchantCriteriaUseOriginalStatement
                __typename
            }
        }
        """
    )
    print(f"Query AST: {get_query}")
    
    print("\n4. POSSIBLE ISSUES TO CHECK:")
    print("- Field name mismatches (camelCase vs snake_case)")
    print("- Missing required fields in input")
    print("- Incorrect GraphQL operation names")
    print("- Authentication headers missing")
    print("- Wrong API endpoint being called")
    
    print("\n5. HAR FILE EVIDENCE:")
    print("From HAR analysis, the correct operation should be:")
    print("- Mutation: Common_CreateTransactionRuleMutationV2")
    print("- Input type: CreateTransactionRuleInput")
    print("- Required fields: merchantCriteria, setCategoryAction")
    print("- All other fields should be null, not omitted")


if __name__ == "__main__":
    asyncio.run(debug_graphql_operations())