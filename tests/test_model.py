import unittest
from datetime import datetime, date
from decimal import Decimal
from monarchmoney.models import (
    Account, AccountType, AccountSubtype, Institution, Credential,
    HouseholdPreferences, GetAccountsResponse, AccountTypeOption,
    GetAccountTypeOptionsResponse, AccountSnapshot, GetAccountSnapshotsResponse,
    AggregateSnapshot, GetAggregateSnapshotsResponse, Subscription,
    GetSubscriptionDetailsResponse, TransactionsSummary, GetTransactionsSummaryResponse,
    Tag, Category, Merchant, Transaction, GetTransactionsResponse,
    CategoryGroup, GetTransactionCategoryGroupsResponse, GetTransactionTagsResponse,
    SplitTransaction, GetTransactionDetailsResponse, CashFlowSummary,
    GetCashFlowResponse, RecurringTransactionStream, RecurringTransactionItem,
    GetRecurringTransactionsResponse, RecentAccountBalance,
    GetRecentAccountBalancesResponse, AccountSnapshotByType, AccountType,
    GetAccountSnapshotsByTypeResponse, AggregateHolding, Holding, Security,
    GetAccountHoldingsResponse, AccountHistorySnapshot, GetAccountHistoryResponse,
    InstitutionStatus, GetInstitutionsResponse, BudgetAmount, CategoryBudget,
    CategoryGroupBudget, FlexExpenseBudget, TotalsByMonth, BudgetCategory,
    Goal, GoalMonthlyContribution, GoalPlannedContribution, GoalV2,
    GetBudgetsResponse, TransactionCategory, GetTransactionCategoriesResponse,
    MerchantInfo, CategoryInfo, SplitTransaction as TransactionSplit,
    TransactionWithSplits, GetTransactionSplitsResponse
)

class TestModels(unittest.TestCase):
    def test_account(self):
        account = Account(
            id="123",
            display_name="Checking",
            sync_disabled=False,
            deactivated_at=None,
            is_hidden=False,
            is_asset=True,
            mask="1234",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            display_last_updated_at=datetime.now(),
            current_balance=1000.0,
            display_balance=1000.0,
            include_in_net_worth=True,
            hide_from_list=False,
            hide_transactions_from_reports=False,
            include_balance_in_net_worth=True,
            include_in_goal_balance=True,
            data_provider="plaid",
            data_provider_account_id="plaid123",
            is_manual=False,
            transactions_count=10,
            holdings_count=0,
            manual_investments_tracking_method=None,
            order=1,
            logo_url="https://example.com/logo.png",
            type=AccountType(name="checking", display="Checking"),
            subtype=AccountSubtype(name="personal", display="Personal"),
            credential=None,
            institution=None
        )
        self.assertEqual(account.id, "123")
        self.assertEqual(account.display_name, "Checking")
        self.assertEqual(account.current_balance, 1000.0)

    def test_get_accounts_response(self):
        response = GetAccountsResponse(
            accounts=[
                Account(
                    id="123",
                    display_name="Checking",
                    sync_disabled=False,
                    deactivated_at=None,
                    is_hidden=False,
                    is_asset=True,
                    mask="1234",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    display_last_updated_at=datetime.now(),
                    current_balance=1000.0,
                    display_balance=1000.0,
                    include_in_net_worth=True,
                    hide_from_list=False,
                    hide_transactions_from_reports=False,
                    include_balance_in_net_worth=True,
                    include_in_goal_balance=True,
                    data_provider="plaid",
                    data_provider_account_id="plaid123",
                    is_manual=False,
                    transactions_count=10,
                    holdings_count=0,
                    manual_investments_tracking_method=None,
                    order=1,
                    logo_url="https://example.com/logo.png",
                    type=AccountType(name="checking", display="Checking"),
                    subtype=AccountSubtype(name="personal", display="Personal"),
                    credential=None,
                    institution=None
                )
            ],
            household_preferences=HouseholdPreferences(
                id="456",
                account_group_order=["123"]
            )
        )
        self.assertEqual(len(response.accounts), 1)
        self.assertEqual(response.accounts[0].id, "123")
        self.assertEqual(response.household_preferences.id, "456")

    def test_get_account_type_options_response(self):
        response = GetAccountTypeOptionsResponse(
            account_type_options=[
                AccountTypeOption(
                    type=AccountType(name="checking", display="Checking"),
                    subtype=AccountSubtype(name="personal", display="Personal")
                )
            ]
        )
        self.assertEqual(len(response.account_type_options), 1)
        self.assertEqual(response.account_type_options[0].type.name, "checking")

    def test_get_account_snapshots_response(self):
        response = GetAccountSnapshotsResponse(
            snapshots=[
                AccountSnapshot(date=date(2023, 1, 1), signed_balance=1000.0),
                AccountSnapshot(date=date(2023, 1, 2), signed_balance=1100.0)
            ]
        )
        self.assertEqual(len(response.snapshots), 2)
        self.assertEqual(response.snapshots[0].signed_balance, 1000.0)

    def test_get_aggregate_snapshots_response(self):
        response = GetAggregateSnapshotsResponse(
            aggregate_snapshots=[
                AggregateSnapshot(date=date(2023, 1, 1), balance=10000.0),
                AggregateSnapshot(date=date(2023, 1, 2), balance=10100.0)
            ]
        )
        self.assertEqual(len(response.aggregate_snapshots), 2)
        self.assertEqual(response.aggregate_snapshots[0].balance, 10000.0)

    def test_get_subscription_details_response(self):
        response = GetSubscriptionDetailsResponse(
            subscription=Subscription(
                id="789",
                payment_source="credit_card",
                referral_code="REF123",
                is_on_free_trial=False,
                has_premium_entitlement=True
            )
        )
        self.assertEqual(response.subscription.id, "789")
        self.assertTrue(response.subscription.has_premium_entitlement)

    def test_get_transactions_summary_response(self):
        response = GetTransactionsSummaryResponse(
            summary=TransactionsSummary(
                avg=100.0,
                count=10,
                max=500.0,
                max_expense=300.0,
                sum=1000.0,
                sum_income=1500.0,
                sum_expense=500.0,
                first=datetime(2023, 1, 1),
                last=datetime(2023, 1, 31)
            )
        )
        self.assertEqual(response.summary.count, 10)
        self.assertEqual(response.summary.sum_income, 1500.0)

    def test_get_transactions_response(self):
        response = GetTransactionsResponse(
            total_count=1,
            results=[
                Transaction(
                    id="t123",
                    amount=-50.0,
                    pending=False,
                    date=date(2023, 1, 15),
                    hide_from_reports=False,
                    plaid_name="ACME Store",
                    notes="Groceries",
                    is_recurring=False,
                    review_status=None,
                    needs_review=False,
                    attachments=[],
                    is_split_transaction=False,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    category=Category(id="c1", name="Groceries", group={"id": "g1", "name": "Essentials"}),
                    merchant=Merchant(name="ACME Store", id="m1", transactions_count=5),
                    account=Account(
                        id="a1",
                        display_name="Checking",
                        sync_disabled=False,
                        deactivated_at=None,
                        is_hidden=False,
                        is_asset=True,
                        mask="1234",
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        display_last_updated_at=datetime.now(),
                        current_balance=1000.0,
                        display_balance=1000.0,
                        include_in_net_worth=True,
                        hide_from_list=False,
                        hide_transactions_from_reports=False,
                        include_balance_in_net_worth=True,
                        include_in_goal_balance=True,
                        data_provider="plaid",
                        data_provider_account_id="plaid123",
                        is_manual=False,
                        transactions_count=10,
                        holdings_count=0,
                        manual_investments_tracking_method=None,
                        order=1,
                        logo_url="https://example.com/logo.png",
                        type=AccountType(name="checking", display="Checking"),
                        subtype=AccountSubtype(name="personal", display="Personal"),
                        credential=None,
                        institution=None
                    ),
                    tags=[]
                )
            ],
            transaction_rules=[]
        )
        self.assertEqual(response.total_count, 1)
        self.assertEqual(response.results[0].amount, -50.0)
        self.assertEqual(response.results[0].merchant.name, "ACME Store")

    def test_get_transaction_category_groups_response(self):
        response = GetTransactionCategoryGroupsResponse(
            category_groups=[
                CategoryGroup(
                    id="g1",
                    name="Essentials",
                    type="expense",
                    order=1,
                    updated_at=datetime.now(),
                    created_at=datetime.now()
                )
            ]
        )
        self.assertEqual(len(response.category_groups), 1)
        self.assertEqual(response.category_groups[0].name, "Essentials")

    def test_get_transaction_tags_response(self):
        response = GetTransactionTagsResponse(
            tags=[
                Tag(id="t1", name="Vacation", color="#FF0000", order=1)
            ]
        )
        self.assertEqual(len(response.tags), 1)
        self.assertEqual(response.tags[0].name, "Vacation")

    def test_get_transaction_details_response(self):
        response = GetTransactionDetailsResponse(
            transaction=Transaction(
                id="t123",
                amount=-50.0,
                pending=False,
                date=date(2023, 1, 15),
                hide_from_reports=False,
                plaid_name="ACME Store",
                notes="Groceries",
                is_recurring=False,
                review_status=None,
                needs_review=False,
                attachments=[],
                is_split_transaction=False,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                category=Category(id="c1", name="Groceries", group={"id": "g1", "name": "Essentials"}),
                merchant=Merchant(name="ACME Store", id="m1", transactions_count=5),
                account=Account(
                    id="a1",
                    display_name="Checking",
                    sync_disabled=False,
                    deactivated_at=None,
                    is_hidden=False,
                    is_asset=True,
                    mask="1234",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    display_last_updated_at=datetime.now(),
                    current_balance=1000.0,
                    display_balance=1000.0,
                    include_in_net_worth=True,
                    hide_from_list=False,
                    hide_transactions_from_reports=False,
                    include_balance_in_net_worth=True,
                    include_in_goal_balance=True,
                    data_provider="plaid",
                    data_provider_account_id="plaid123",
                    is_manual=False,
                    transactions_count=10,
                    holdings_count=0,
                    manual_investments_tracking_method=None,
                    order=1,
                    logo_url="https://example.com/logo.png",
                    type=AccountType(name="checking", display="Checking"),
                    subtype=AccountSubtype(name="personal", display="Personal"),
                    credential=None,
                    institution=None
                ),
                tags=[]
            )
        )
        self.assertEqual(response.transaction.id, "t123")
        self.assertEqual(response.transaction.amount, -50.0)

    def test_get_cashflow_response(self):
        response = GetCashFlowResponse(
            by_category=[],
            by_category_group=[],
            by_merchant=[],
            summary=CashFlowSummary(
                sum_income=5000.0,
                sum_expense=3000.0,
                savings=2000.0,
                savings_rate=0.4
            )
        )
        self.assertEqual(response.summary.sum_income, 5000.0)
        self.assertEqual(response.summary.savings_rate, 0.4)

    def test_get_recurring_transactions_response(self):
        response = GetRecurringTransactionsResponse(
            recurring_transaction_items=[
                RecurringTransactionItem(
                    stream=RecurringTransactionStream(
                        id="rs1",
                        frequency="monthly",
                        amount=100.0,
                        is_approximate=False,
                        merchant=Merchant(name="Netflix", id="m2", transactions_count=12)
                    ),
                    date=date(2023, 2, 1),
                    is_past=False,
                    transaction_id=None,
                    amount=100.0,
                    amount_diff=0.0,
                    category=Category(id="c2", name="Streaming", group={"id": "g2", "name": "Entertainment"}),
                    account=Account(
                        id="a1",
                        display_name="Checking",
                        sync_disabled=False,
                        deactivated_at=None,
                        is_hidden=False,
                        is_asset=True,
                        mask="1234",
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        display_last_updated_at=datetime.now(),
                        current_balance=1000.0,
                        display_balance=1000.0,
                        include_in_net_worth=True,
                        hide_from_list=False,
                        hide_transactions_from_reports=False,
                        include_balance_in_net_worth=True,
                        include_in_goal_balance=True,
                        data_provider="plaid",
                        data_provider_account_id="plaid123",
                        is_manual=False,
                        transactions_count=10,
                        holdings_count=0,
                        manual_investments_tracking_method=None,
                        order=1,
                        logo_url="https://example.com/logo.png",
                        type=AccountType(name="checking", display="Checking"),
                        subtype=AccountSubtype(name="personal", display="Personal"),
                        credential=None,
                        institution=None
                    )
                )
            ]
        )
        self.assertEqual(len(response.recurring_transaction_items), 1)
        self.assertEqual(response.recurring_transaction_items[0].stream.frequency, "monthly")
        self.assertEqual(response.recurring_transaction_items[0].amount, 100.0)

    def test_get_recent_account_balances_response(self):
        response = GetRecentAccountBalancesResponse(
            accounts=[
                RecentAccountBalance(
                    id="acc1",
                    recent_balances=[1000.0, 1100.0, 1200.0]
                ),
                RecentAccountBalance(
                    id="acc2",
                    recent_balances=[2000.0, 2100.0, 2200.0]
                )
            ]
        )
        self.assertEqual(len(response.accounts), 2)
        self.assertEqual(response.accounts[0].id, "acc1")
        self.assertEqual(len(response.accounts[0].recent_balances), 3)
        self.assertEqual(response.accounts[0].recent_balances[0], 1000.0)
        self.assertEqual(response.accounts[1].id, "acc2")
        self.assertEqual(response.accounts[1].recent_balances[-1], 2200.0)

    def test_get_account_snapshots_by_type_response(self):
        response = GetAccountSnapshotsByTypeResponse(
            snapshots_by_account_type=[
                AccountSnapshotByType(account_type="checking", month="2023-05", balance=1000.0)
            ],
            account_types=[
                AccountType(name="checking", group="assets")
            ]
        )
        self.assertEqual(len(response.snapshots_by_account_type), 1)
        self.assertEqual(response.snapshots_by_account_type[0].account_type, "checking")
        self.assertEqual(len(response.account_types), 1)
        self.assertEqual(response.account_types[0].name, "checking")

    def test_get_account_holdings_response(self):
        response = GetAccountHoldingsResponse(
            aggregate_holdings=[
                AggregateHolding(
                    id="ah1",
                    quantity=10.0,
                    basis=1000.0,
                    total_value=1100.0,
                    security_price_change_dollars=100.0,
                    security_price_change_percent=0.1,
                    last_synced_at=datetime.now(),
                    holdings=[
                        Holding(
                            id="h1",
                            type="stock",
                            type_display="Stock",
                            name="ACME Corp",
                            ticker="ACME",
                            closing_price=110.0,
                            is_manual=False,
                            closing_price_updated_at=datetime.now()
                        )
                    ],
                    security=Security(
                        id="s1",
                        name="ACME Corp",
                        type="stock",
                        ticker="ACME",
                        type_display="Stock",
                        current_price=110.0,
                        current_price_updated_at=datetime.now(),
                        closing_price=109.0,
                        closing_price_updated_at=datetime.now(),
                        one_day_change_percent=0.01,
                        one_day_change_dollars=1.0
                    )
                )
            ]
        )
        self.assertEqual(len(response.aggregate_holdings), 1)
        self.assertEqual(response.aggregate_holdings[0].quantity, 10.0)
        self.assertEqual(response.aggregate_holdings[0].holdings[0].name, "ACME Corp")
        self.assertEqual(response.aggregate_holdings[0].security.ticker, "ACME")

    def test_get_account_history_response(self):
        response = GetAccountHistoryResponse(
            account_balance_history=[
                AccountHistorySnapshot(
                    date=date(2023, 1, 1),
                    signed_balance=1000.0,
                    account_id="acc1",
                    account_name="Checking"
                ),
                AccountHistorySnapshot(
                    date=date(2023, 1, 2),
                    signed_balance=1100.0,
                    account_id="acc1",
                    account_name="Checking"
                )
            ]
        )
        self.assertEqual(len(response.account_balance_history), 2)
        self.assertEqual(response.account_balance_history[0].signed_balance, 1000.0)
        self.assertEqual(response.account_balance_history[1].account_name, "Checking")

    def test_get_institutions_response(self):
        response = GetInstitutionsResponse(
            credentials=[
                Credential(
                    id="cred1",
                    display_last_updated_at=datetime.now(),
                    data_provider="plaid",
                    update_required=False,
                    disconnected_from_data_provider_at=None,
                    institution=Institution(
                        id="inst1",
                        name="Bank of America",
                        url="https://www.bankofamerica.com",
                        status=InstitutionStatus(
                            has_issues_reported=False,
                            has_issues_reported_message=None,
                            plaid_status="HEALTHY",
                            status="ACTIVE",
                            balance_status="UPDATED",
                            transactions_status="UPDATED"
                        )
                    )
                )
            ],
            accounts=[],
            subscription={}
        )
        self.assertEqual(len(response.credentials), 1)
        self.assertEqual(response.credentials[0].institution.name, "Bank of America")
        self.assertEqual(response.credentials[0].institution.status.plaid_status, "HEALTHY")

    def test_get_budgets_response(self):
        response = GetBudgetsResponse(
            budget_data={},
            category_groups=[
                CategoryGroup(
                    id="cg1",
                    name="Food",
                    order=1,
                    group_level_budgeting_enabled=True,
                    budget_variability="fixed",
                    rollover_period=None,
                    categories=[
                        BudgetCategory(
                            id="c1",
                            name="Groceries",
                            order=1,
                            budget_variability="fixed",
                            rollover_period=None
                        )
                    ],
                    type="expense"
                )
            ],
            goals=None,
            goal_monthly_contributions=None,
            goal_planned_contributions=None,
            goals_v2=None,
            budget_system="default"
        )
        self.assertEqual(len(response.category_groups), 1)
        self.assertEqual(response.category_groups[0].name, "Food")
        self.assertEqual(len(response.category_groups[0].categories), 1)
        self.assertEqual(response.category_groups[0].categories[0].name, "Groceries")

    def test_get_transaction_categories_response(self):
        response = GetTransactionCategoriesResponse(
            categories=[
                TransactionCategory(
                    id="cat1",
                    order=1,
                    name="Groceries",
                    system_category=True,
                    is_system_category=True,
                    is_disabled=False,
                    updated_at=datetime.now(),
                    created_at=datetime.now(),
                    group=CategoryGroup(
                        id="group1",
                        name="Food & Dining",
                        type="expense"
                    )
                ),
                TransactionCategory(
                    id="cat2",
                    order=2,
                    name="Salary",
                    system_category=True,
                    is_system_category=True,
                    is_disabled=False,
                    updated_at=datetime.now(),
                    created_at=datetime.now(),
                    group=CategoryGroup(
                        id="group2",
                        name="Income",
                        type="income"
                    )
                )
            ]
        )
        self.assertEqual(len(response.categories), 2)
        self.assertEqual(response.categories[0].name, "Groceries")
        self.assertEqual(response.categories[0].group.name, "Food & Dining")
        self.assertEqual(response.categories[1].name, "Salary")
        self.assertEqual(response.categories[1].group.type, "income")

    def test_get_transaction_splits_response(self):
        response = GetTransactionSplitsResponse(
            transaction=TransactionWithSplits(
                id="trans1",
                amount=Decimal("100.00"),
                category=CategoryInfo(id="cat1", name="Groceries"),
                merchant=MerchantInfo(id="merch1", name="Supermarket"),
                split_transactions=[
                    TransactionSplit(
                        id="split1",
                        merchant=MerchantInfo(id="merch1", name="Supermarket"),
                        category=CategoryInfo(id="cat2", name="Food"),
                        amount=Decimal("60.00"),
                        notes="Foodstuff"
                    ),
                    TransactionSplit(
                        id="split2",
                        merchant=MerchantInfo(id="merch1", name="Supermarket"),
                        category=CategoryInfo(id="cat3", name="Household"),
                        amount=Decimal("40.00"),
                        notes="Cleaning supplies"
                    )
                ]
            )
        )

        self.assertEqual(response.transaction.id, "trans1")
        self.assertEqual(response.transaction.amount, Decimal("100.00"))
        self.assertEqual(response.transaction.category.name, "Groceries")
        self.assertEqual(response.transaction.merchant.name, "Supermarket")
        self.assertEqual(len(response.transaction.split_transactions), 2)
        self.assertEqual(response.transaction.split_transactions[0].amount, Decimal("60.00"))
        self.assertEqual(response.transaction.split_transactions[0].category.name, "Food")
        self.assertEqual(response.transaction.split_transactions[1].amount, Decimal("40.00"))
        self.assertEqual(response.transaction.split_transactions[1].category.name, "Household")

if __name__ == '__main__':
    unittest.main()