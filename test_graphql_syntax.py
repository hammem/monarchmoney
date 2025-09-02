#!/usr/bin/env python3

import sys
sys.path.insert(0, "/home/keith/src/monarchmoney")

from gql import gql

def test_queries():
    """Test that our GraphQL queries parse correctly."""
    
    print("=== Testing GetTransactionRules Query ===")
    try:
        query = gql(
            """
            query GetTransactionRules {
                transactionRules {
                    id
                    order
                    ...TransactionRuleFields
                    __typename
                }
            }

            fragment TransactionRuleFields on TransactionRuleV2 {
                merchantCriteriaUseOriginalStatement
                merchantCriteria {
                    operator
                    value
                    __typename
                }
                amountCriteria {
                    operator
                    isExpense
                    value
                    valueRange {
                        lower
                        upper
                        __typename
                    }
                    __typename
                }
                categoryIds
                accountIds
                categories {
                    id
                    name
                    icon
                    __typename
                }
                accounts {
                    id
                    displayName
                    icon
                    logoUrl
                    __typename
                }
                setMerchantAction {
                    id
                    name
                    __typename
                }
                setCategoryAction {
                    id
                    name
                    icon
                    __typename
                }
                addTagsAction {
                    id
                    name
                    color
                    __typename
                }
                linkGoalAction {
                    id
                    name
                    imageStorageProvider
                    imageStorageProviderId
                    __typename
                }
                needsReviewByUserAction {
                    id
                    name
                    __typename
                }
                unassignNeedsReviewByUserAction
                sendNotificationAction
                setHideFromReportsAction
                reviewStatusAction
                recentApplicationCount
                lastAppliedAt
                splitTransactionsAction {
                    amountType
                    splitsInfo {
                        categoryId
                        merchantName
                        amount
                        goalId
                        tags
                        hideFromReports
                        reviewStatus
                        needsReviewByUserId
                        __typename
                    }
                    __typename
                }
                __typename
            }
            """
        )
        print("✓ GetTransactionRules query parsed successfully")
    except Exception as e:
        print(f"✗ GetTransactionRules query parsing failed: {e}")
    
    print("\n=== Testing CreateTransactionRule Mutation ===")
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
        print("✓ CreateTransactionRule mutation parsed successfully")
    except Exception as e:
        print(f"✗ CreateTransactionRule mutation parsing failed: {e}")


if __name__ == "__main__":
    test_queries()