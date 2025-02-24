import asyncio
import calendar
import getpass
import json
import os
import pickle
import time
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Union

import oathtool
from aiohttp import ClientSession, FormData
from aiohttp.client import DEFAULT_TIMEOUT
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode

AUTH_HEADER_KEY = "authorization"
CSRF_KEY = "csrftoken"
DEFAULT_RECORD_LIMIT = 100
ERRORS_KEY = "error_code"
SESSION_DIR = ".mm"
SESSION_FILE = f"{SESSION_DIR}/mm_session.pickle"


class MonarchMoneyEndpoints(object):
    BASE_URL = "https://api.monarchmoney.com"

    @classmethod
    def getLoginEndpoint(cls) -> str:
        return cls.BASE_URL + "/auth/login/"

    @classmethod
    def getGraphQL(cls) -> str:
        return cls.BASE_URL + "/graphql"

    @classmethod
    def getAccountBalanceHistoryUploadEndpoint(cls) -> str:
        return cls.BASE_URL + "/account-balance-history/upload/"


class RequireMFAException(Exception):
    pass


class LoginFailedException(Exception):
    pass


class RequestFailedException(Exception):
    pass


class MonarchMoney(object):
    def __init__(
        self,
        session_file: str = SESSION_FILE,
        timeout: int = 10,
        token: Optional[str] = None,
    ) -> None:
        self._headers = {
            "Accept": "application/json",
            "Client-Platform": "web",
            "Content-Type": "application/json",
            "User-Agent": "MonarchMoneyAPI (https://github.com/hammem/monarchmoney)",
        }
        if token:
            self._headers["Authorization"] = f"Token {token}"

        self._session_file = session_file
        self._token = token
        self._timeout = timeout

    @property
    def timeout(self) -> int:
        """The timeout, in seconds, for GraphQL calls."""
        return self._timeout

    def set_timeout(self, timeout_secs: int) -> None:
        """Sets the default timeout on GraphQL API calls, in seconds."""
        self._timeout = timeout_secs

    @property
    def token(self) -> Optional[str]:
        return self._token

    def set_token(self, token: str) -> None:
        self._token = token

    async def interactive_login(
        self, use_saved_session: bool = True, save_session: bool = True
    ) -> None:
        """Performs an interactive login for iPython and similar environments."""
        email = input("Email: ")
        passwd = getpass.getpass("Password: ")
        try:
            await self.login(email, passwd, use_saved_session, save_session)
        except RequireMFAException:
            await self.multi_factor_authenticate(
                email, passwd, input("Two Factor Code: ")
            )
            if save_session:
                self.save_session(self._session_file)

    async def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        use_saved_session: bool = True,
        save_session: bool = True,
        mfa_secret_key: Optional[str] = None,
    ) -> None:
        """Logs into a Monarch Money account."""
        if use_saved_session and os.path.exists(self._session_file):
            print(f"Using saved session found at {self._session_file}")
            self.load_session(self._session_file)
            return

        if (email is None) or (password is None) or (email == "") or (password == ""):
            raise LoginFailedException(
                "Email and password are required to login when not using a saved session."
            )
        await self._login_user(email, password, mfa_secret_key)
        if save_session:
            self.save_session(self._session_file)

    async def multi_factor_authenticate(
        self, email: str, password: str, code: str
    ) -> None:
        """Performs multi-factor authentication to access a Monarch Money account."""
        await self._multi_factor_authenticate(email, password, code)

    async def get_accounts(self) -> Dict[str, Any]:
        """
        Gets the list of accounts configured in the Monarch Money account.
        """
        query = gql(
            """
          query GetAccounts {
            accounts {
              ...AccountFields
              __typename
            }
            householdPreferences {
              id
              accountGroupOrder
              __typename
            }
          }

          fragment AccountFields on Account {
            id
            displayName
            syncDisabled
            deactivatedAt
            isHidden
            isAsset
            mask
            createdAt
            updatedAt
            displayLastUpdatedAt
            currentBalance
            displayBalance
            includeInNetWorth
            hideFromList
            hideTransactionsFromReports
            includeBalanceInNetWorth
            includeInGoalBalance
            dataProvider
            dataProviderAccountId
            isManual
            transactionsCount
            holdingsCount
            manualInvestmentsTrackingMethod
            order
            logoUrl
            type {
              name
              display
              __typename
            }
            subtype {
              name
              display
              __typename
            }
            credential {
              id
              updateRequired
              disconnectedFromDataProviderAt
              dataProvider
              institution {
                id
                plaidInstitutionId
                name
                status
                __typename
              }
              __typename
            }
            institution {
              id
              name
              primaryColor
              url
              __typename
            }
            __typename
          }
        """
        )
        return await self.gql_call(
            operation="GetAccounts",
            graphql_query=query,
        )

    async def get_account_type_options(self) -> Dict[str, Any]:
        """
        Retrieves a list of available account types and their subtypes.
        """
        query = gql(
            """
            query GetAccountTypeOptions {
                accountTypeOptions {
                    type {
                        name
                        display
                        group
                        possibleSubtypes {
                            display
                            name
                            __typename
                        }
                        __typename
                    }
                    subtype {
                        name
                        display
                        __typename
                    }
                    __typename
                }
            }
        """
        )
        return await self.gql_call(
            operation="GetAccountTypeOptions",
            graphql_query=query,
        )

    async def get_recent_account_balances(
        self, start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves the daily balance for all accounts starting from `start_date`.
        `start_date` is an ISO formatted datestring, e.g. YYYY-MM-DD.
        If `start_date` is None, then the last 31 days are requested.
        """
        if start_date is None:
            start_date = (date.today() - timedelta(days=31)).isoformat()

        query = gql(
            """
            query GetAccountRecentBalances($startDate: Date!) {
                accounts {
                    id
                    recentBalances(startDate: $startDate)
                    __typename
                }
            }
        """
        )
        return await self.gql_call(
            operation="GetAccountRecentBalances",
            graphql_query=query,
            variables={"startDate": start_date},
        )

    async def get_account_snapshots_by_type(self, start_date: str, timeframe: str):
        """
        Retrieves snapshots of the net values of all accounts of a given type, with either a yearly
        monthly granularity.
        `start_date` is an ISO datestring in the format YYYY-MM-DD, e.g. 2024-04-01,
        containing the date to begin the snapshots from
        `timeframe` is one of "year" or "month".

        Note, `month` in the snapshot results is not a full ISO datestring, as it doesn't include the day.
        Instead, it looks like, e.g., 2023-01
        """
        if timeframe not in ("year", "month"):
            raise Exception(f'Unknown timeframe "{timeframe}"')

        query = gql(
            """
            query GetSnapshotsByAccountType($startDate: Date!, $timeframe: Timeframe!) {
                snapshotsByAccountType(startDate: $startDate, timeframe: $timeframe) {
                    accountType
                    month
                    balance
                    __typename
                }
                accountTypes {
                    name
                    group
                    __typename
                }
            }
        """
        )
        return await self.gql_call(
            operation="GetSnapshotsByAccountType",
            graphql_query=query,
            variables={"startDate": start_date, "timeframe": timeframe},
        )

    async def get_aggregate_snapshots(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_type: Optional[str] = None,
    ) -> dict:
        """
        Retrieves the daily net value of all accounts, optionally between `start_date` and `end_date`,
        and optionally only for accounts of type `account_type`.
        Both `start_date` and `end_date` are ISO datestrings, formatted as YYYY-MM-DD
        """
        query = gql(
            """
            query GetAggregateSnapshots($filters: AggregateSnapshotFilters) {
                aggregateSnapshots(filters: $filters) {
                    date
                    balance
                    __typename
                }
            }
        """
        )

        if start_date is None:
            # The mobile app defaults to 150 years ago today
            # The mobile app might have a leap year bug, so instead default to setting day=1
            today = date.today()
            start_date = date(
                year=today.year - 150, month=today.month, day=1
            ).isoformat()

        return await self.gql_call(
            operation="GetAggregateSnapshots",
            graphql_query=query,
            variables={
                "filters": {
                    "startDate": start_date,
                    "endDate": end_date,
                    "accountType": account_type,
                }
            },
        )

    async def create_manual_account(
        self,
        account_type: str,
        account_sub_type: str,
        is_in_net_worth: bool,
        account_name: str,
        account_balance: float = 0,
    ) -> Dict[str, Any]:
        """
        Creates a new manual account

        :param account_type: The string of account group type (i.e. loan, other_liability, other_asset, etc)
        :param account_sub_type: The string sub type of the account (i.e. auto, commercial, mortgage, line_of_credit, etc)
        :param is_in_net_worth: A boolean if the account should be considered in the net worth calculation
        :param account_name: The string of the account name
        :param display_balance: a float of the amount of the account balance when the account is created
        """
        query = gql(
            """
            mutation Web_CreateManualAccount($input: CreateManualAccountMutationInput!) {
                createManualAccount(input: $input) {
                    account {
                        id
                        __typename
                    }
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
        variables = {
            "input": {
                "type": account_type,
                "subtype": account_sub_type,
                "includeInNetWorth": is_in_net_worth,
                "name": account_name,
                "displayBalance": account_balance,
            },
        }

        return await self.gql_call(
            operation="Web_CreateManualAccount",
            graphql_query=query,
            variables=variables,
        )

    #
    async def update_account(
        self,
        account_id: str,
        account_name: Optional[str] = None,
        account_balance: Optional[float] = None,
        account_type: Optional[str] = None,
        account_sub_type: Optional[str] = None,
        include_in_net_worth: Optional[bool] = None,
        hide_from_summary_list: Optional[bool] = None,
        hide_transactions_from_reports: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Updates the details of an account.

        With the exception of the account_balance parameter, the only available parameters currently are those
        that are valid for both synced and manual accounts.

        :param account_id: The string ID of the account to update
        :param account_name: The string of the account name
        :param account_balance: a float of the amount to update the account balance to
        :param account_type: The string of account group type (i.e. loan, other_liability, other_asset, etc)
        :param account_sub_type: The string sub type of the account (i.e. auto, commercial, mortgage, line_of_credit, etc)
        :param include_in_net_worth: A boolean if the account should be considered in the net worth calculation
        :param hide_from_summary_list: A boolean if the account should be hidden in the "Accounts" view
        :param hide_transactions_from_reports: A boolean if the account should be excluded from budgets and reports
        """
        query = gql(
            """
            mutation Common_UpdateAccount($input: UpdateAccountMutationInput!) {
                updateAccount(input: $input) {
                    account {
                        ...AccountFields
                        __typename
                    }
                    errors {
                        ...PayloadErrorFields
                        __typename
                    }
                    __typename
                }
            }

            fragment AccountFields on Account {
                id
                displayName
                syncDisabled
                deactivatedAt
                isHidden
                isAsset
                mask
                createdAt
                updatedAt
                displayLastUpdatedAt
                currentBalance
                displayBalance
                includeInNetWorth
                hideFromList
                hideTransactionsFromReports
                includeBalanceInNetWorth
                includeInGoalBalance
                dataProvider
                dataProviderAccountId
                isManual
                transactionsCount
                holdingsCount
                manualInvestmentsTrackingMethod
                order
                icon
                logoUrl
                deactivatedAt
                type {
                    name
                    display
                    group
                    __typename
                }
                subtype {
                    name
                    display
                    __typename
                }
                credential {
                    id
                    updateRequired
                    disconnectedFromDataProviderAt
                    dataProvider
                    institution {
                        id
                        plaidInstitutionId
                        name
                        status
                        __typename
                    }
                    __typename
                }
                institution {
                    id
                    name
                    primaryColor
                    url
                    __typename
                }
                __typename
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

        variables = {
            "id": str(account_id),
        }

        if account_type is not None:
            variables["type"] = account_type
        if account_sub_type is not None:
            variables["subtype"] = account_sub_type
        if include_in_net_worth is not None:
            variables["includeInNetWorth"] = include_in_net_worth
        if hide_from_summary_list is not None:
            variables["hideFromList"] = hide_from_summary_list
        if hide_transactions_from_reports is not None:
            variables["hideTransactionsFromReports"] = hide_transactions_from_reports
        if account_name is not None:
            variables["name"] = account_name
        if account_balance is not None:
            variables["displayBalance"] = account_balance

        return await self.gql_call(
            operation="Common_UpdateAccount",
            graphql_query=query,
            variables={"input": variables},
        )

    async def delete_account(
        self,
        account_id: str,
    ) -> Dict[str, Any]:
        """
        Deletes an account
        """
        query = gql(
            """
            mutation Common_DeleteAccount($id: UUID!) {
                deleteAccount(id: $id) {
                    deleted
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

        variables = {"id": account_id}

        return await self.gql_call(
            operation="Common_DeleteAccount",
            graphql_query=query,
            variables=variables,
        )

    async def request_accounts_refresh(self, account_ids: List[str]) -> bool:
        """
        Requests Monarch to refresh account balances and transactions with
        source institutions.  Returns True if request was successfully started.

        Otherwise, throws a `RequestFailedException`.
        """
        query = gql(
            """
          mutation Common_ForceRefreshAccountsMutation($input: ForceRefreshAccountsInput!) {
            forceRefreshAccounts(input: $input) {
              success
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

        variables = {
            "input": {
                "accountIds": account_ids,
            },
        }

        response = await self.gql_call(
            operation="Common_ForceRefreshAccountsMutation",
            graphql_query=query,
            variables=variables,
        )

        if not response["forceRefreshAccounts"]["success"]:
            raise RequestFailedException(response["forceRefreshAccounts"]["errors"])

        return True

    async def is_accounts_refresh_complete(
        self, account_ids: Optional[List[str]] = None
    ) -> bool:
        """
        Checks on the status of a prior request to refresh account balances.

        Returns:
          - True if refresh request is completed.
          - False if refresh request still in progress.

        Otherwise, throws a `RequestFailedException`.

        :param account_ids: The list of accounts IDs to check on the status of.
          If set to None, all account IDs will be checked.
        """
        query = gql(
            """
          query ForceRefreshAccountsQuery {
            accounts {
              id
              hasSyncInProgress
              __typename
            }
          }
          """
        )

        response = await self.gql_call(
            operation="ForceRefreshAccountsQuery",
            graphql_query=query,
            variables={},
        )

        if "accounts" not in response:
            raise RequestFailedException("Unable to request status of refresh")

        if account_ids:
            return all(
                [
                    not x["hasSyncInProgress"]
                    for x in response["accounts"]
                    if x["id"] in account_ids
                ]
            )
        else:
            return all([not x["hasSyncInProgress"] for x in response["accounts"]])

    async def request_accounts_refresh_and_wait(
        self,
        account_ids: Optional[List[str]] = None,
        timeout: int = 300,
        delay: int = 10,
    ) -> bool:
        """
        Convenience method for forcing an accounts refresh on Monarch, as well
        as waiting for the refresh to complete.

        Returns True if all accounts are refreshed within the timeout specified, False otherwise.

        :param account_ids: The list of accounts IDs to refresh.
          If set to None, all account IDs will be implicitly fetched.
        :param timeout: The number of seconds to wait for the refresh to complete
        :param delay: The number of seconds to wait for each check on the refresh request
        """
        if account_ids is None:
            account_data = await self.get_accounts()
            account_ids = [x["id"] for x in account_data["accounts"]]
        await self.request_accounts_refresh(account_ids)
        start = time.time()
        refreshed = False
        while not refreshed and (time.time() <= (start + timeout)):
            await asyncio.sleep(delay)
            refreshed = await self.is_accounts_refresh_complete(account_ids)
        return refreshed

    async def get_account_holdings(self, account_id: int) -> Dict[str, Any]:
        """
        Get the holdings information for a brokerage or similar type of account.
        """
        query = gql(
            """
          query Web_GetHoldings($input: PortfolioInput) {
            portfolio(input: $input) {
              aggregateHoldings {
                edges {
                  node {
                    id
                    quantity
                    basis
                    totalValue
                    securityPriceChangeDollars
                    securityPriceChangePercent
                    lastSyncedAt
                    holdings {
                      id
                      type
                      typeDisplay
                      name
                      ticker
                      closingPrice
                      isManual
                      closingPriceUpdatedAt
                      __typename
                    }
                    security {
                      id
                      name
                      type
                      ticker
                      typeDisplay
                      currentPrice
                      currentPriceUpdatedAt
                      closingPrice
                      closingPriceUpdatedAt
                      oneDayChangePercent
                      oneDayChangeDollars
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                __typename
              }
              __typename
            }
          }
        """
        )

        variables = {
            "input": {
                "accountIds": [str(account_id)],
                "endDate": datetime.today().strftime("%Y-%m-%d"),
                "includeHiddenHoldings": True,
                "startDate": datetime.today().strftime("%Y-%m-%d"),
            },
        }

        return await self.gql_call(
            operation="Web_GetHoldings",
            graphql_query=query,
            variables=variables,
        )

    async def get_account_history(self, account_id: int) -> Dict[str, Any]:
        """
        Gets historical account snapshot data for the requested account

        Args:
          account_id: Monarch account ID as an integer

        Returns:
          json object with all historical snapshots of requested account's balances
        """

        query = gql(
            """
            query AccountDetails_getAccount($id: UUID!, $filters: TransactionFilterInput) {
              account(id: $id) {
                id
                ...AccountFields
                ...EditAccountFormFields
                isLiability
                credential {
                  id
                  hasSyncInProgress
                  canBeForceRefreshed
                  disconnectedFromDataProviderAt
                  dataProvider
                  institution {
                    id
                    plaidInstitutionId
                    url
                    ...InstitutionStatusFields
                    __typename
                  }
                  __typename
                }
                institution {
                  id
                  plaidInstitutionId
                  url
                  ...InstitutionStatusFields
                  __typename
                }
                __typename
              }
              transactions: allTransactions(filters: $filters) {
                totalCount
                results(limit: 20) {
                  id
                  ...TransactionsListFields
                  __typename
                }
                __typename
              }
              snapshots: snapshotsForAccount(accountId: $id) {
                date
                signedBalance
                __typename
              }
            }

            fragment AccountFields on Account {
              id
              displayName
              syncDisabled
              deactivatedAt
              isHidden
              isAsset
              mask
              createdAt
              updatedAt
              displayLastUpdatedAt
              currentBalance
              displayBalance
              includeInNetWorth
              hideFromList
              hideTransactionsFromReports
              includeBalanceInNetWorth
              includeInGoalBalance
              dataProvider
              dataProviderAccountId
              isManual
              transactionsCount
              holdingsCount
              manualInvestmentsTrackingMethod
              order
              logoUrl
              type {
                name
                display
                group
                __typename
              }
              subtype {
                name
                display
                __typename
              }
              credential {
                id
                updateRequired
                disconnectedFromDataProviderAt
                dataProvider
                institution {
                  id
                  plaidInstitutionId
                  name
                  status
                  __typename
                }
                __typename
              }
              institution {
                id
                name
                primaryColor
                url
                __typename
              }
              __typename
            }

            fragment EditAccountFormFields on Account {
              id
              displayName
              deactivatedAt
              displayBalance
              includeInNetWorth
              hideFromList
              hideTransactionsFromReports
              dataProvider
              dataProviderAccountId
              isManual
              manualInvestmentsTrackingMethod
              isAsset
              invertSyncedBalance
              canInvertBalance
              type {
                name
                display
                __typename
              }
              subtype {
                name
                display
                __typename
              }
              __typename
            }

            fragment InstitutionStatusFields on Institution {
              id
              hasIssuesReported
              hasIssuesReportedMessage
              plaidStatus
              status
              balanceStatus
              transactionsStatus
              __typename
            }

            fragment TransactionsListFields on Transaction {
              id
              ...TransactionOverviewFields
              __typename
            }

            fragment TransactionOverviewFields on Transaction {
              id
              amount
              pending
              date
              hideFromReports
              plaidName
              notes
              isRecurring
              reviewStatus
              needsReview
              dataProviderDescription
              attachments {
                id
                __typename
              }
              isSplitTransaction
              category {
                id
                name
                group {
                  id
                  type
                  __typename
                }
                __typename
              }
              merchant {
                name
                id
                transactionsCount
                __typename
              }
              tags {
                id
                name
                color
                order
                __typename
              }
              __typename
            }
            """
        )

        variables = {"id": str(account_id)}

        account_details = await self.gql_call(
            operation="AccountDetails_getAccount",
            graphql_query=query,
            variables=variables,
        )

        # Parse JSON
        account_name = account_details["account"]["displayName"]
        account_balance_history = account_details["snapshots"]

        # Append account identification data to account balance history
        for i in account_balance_history:
            i.update(dict(accountId=str(account_id)))
            i.update(dict(accountName=account_name))

        return account_balance_history

    async def get_institutions(self) -> Dict[str, Any]:
        """
        Gets institution data from the account.
        """

        query = gql(
            """
            query Web_GetInstitutionSettings {
              credentials {
                id
                ...CredentialSettingsCardFields
                __typename
              }
              accounts(filters: {includeDeleted: true}) {
                id
                displayName
                subtype {
                  display
                  __typename
                }
                mask
                credential {
                  id
                  __typename
                }
                deletedAt
                __typename
              }
              subscription {
                isOnFreeTrial
                hasPremiumEntitlement
                __typename
              }
            }

            fragment CredentialSettingsCardFields on Credential {
              id
              updateRequired
              disconnectedFromDataProviderAt
              ...InstitutionInfoFields
              institution {
                id
                name
                url
                __typename
              }
              __typename
            }

            fragment InstitutionInfoFields on Credential {
              id
              displayLastUpdatedAt
              dataProvider
              updateRequired
              disconnectedFromDataProviderAt
              ...InstitutionLogoWithStatusFields
              institution {
                id
                name
                hasIssuesReported
                hasIssuesReportedMessage
                __typename
              }
              __typename
            }

            fragment InstitutionLogoWithStatusFields on Credential {
              dataProvider
              updateRequired
              institution {
                hasIssuesReported
                status
                balanceStatus
                transactionsStatus
                __typename
              }
              __typename
            }
        """
        )
        return await self.gql_call(
            operation="Web_GetInstitutionSettings",
            graphql_query=query,
        )

    async def get_budgets(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_legacy_goals: Optional[bool] = False,
        use_v2_goals: Optional[bool] = True,
    ) -> Dict[str, Any]:
        """
        Get your budgets and corresponding actual amounts from the account.

        When no date arguments given:
            | `start_date` will default to last month based on todays date
            | `end_date` will default to next month based on todays date

        :param start_date:
            the earliest date to get budget data, in "yyyy-mm-dd" format (default: last month)
        :param end_date:
            the latest date to get budget data, in "yyyy-mm-dd" format (default: next month)
        :param use_legacy_goals:
            Inoperative (plan to remove)
        :param use_v2_goals:
            Inoperative (paln to remove)
        """
        query = gql(
            """
            query Common_GetJointPlanningData($startDate: Date!, $endDate: Date!) {
              budgetSystem
              budgetData(startMonth: $startDate, endMonth: $endDate) {
                ...BudgetDataFields
                __typename
              }
              categoryGroups {
                ...BudgetCategoryGroupFields
                __typename
              }
              goalsV2 {
                ...BudgetDataGoalsV2Fields
                __typename
              }
            }
            
            fragment BudgetDataMonthlyAmountsFields on BudgetMonthlyAmounts {
              month
              plannedCashFlowAmount
              plannedSetAsideAmount
              actualAmount
              remainingAmount
              previousMonthRolloverAmount
              rolloverType
              cumulativeActualAmount
              rolloverTargetAmount
              __typename
            }
            
            fragment BudgetMonthlyAmountsByCategoryFields on BudgetCategoryMonthlyAmounts {
              category {
                id
                __typename
              }
              monthlyAmounts {
                ...BudgetDataMonthlyAmountsFields
                __typename
              }
              __typename
            }
            
            fragment BudgetMonthlyAmountsByCategoryGroupFields on BudgetCategoryGroupMonthlyAmounts {
              categoryGroup {
                id
                __typename
              }
              monthlyAmounts {
                ...BudgetDataMonthlyAmountsFields
                __typename
              }
              __typename
            }
            
            fragment BudgetMonthlyAmountsForFlexExpenseFields on BudgetFlexMonthlyAmounts {
              budgetVariability
              monthlyAmounts {
                ...BudgetDataMonthlyAmountsFields
                __typename
              }
              __typename
            }
            
            fragment BudgetDataTotalsByMonthFields on BudgetTotals {
              actualAmount
              plannedAmount
              previousMonthRolloverAmount
              remainingAmount
              __typename
            }
            
            fragment BudgetTotalsByMonthFields on BudgetMonthTotals {
              month
              totalIncome {
                ...BudgetDataTotalsByMonthFields
                __typename
              }
              totalExpenses {
                ...BudgetDataTotalsByMonthFields
                __typename
              }
              totalFixedExpenses {
                ...BudgetDataTotalsByMonthFields
                __typename
              }
              totalNonMonthlyExpenses {
                ...BudgetDataTotalsByMonthFields
                __typename
              }
              totalFlexibleExpenses {
                ...BudgetDataTotalsByMonthFields
                __typename
              }
              __typename
            }
            
            fragment BudgetRolloverPeriodFields on BudgetRolloverPeriod {
              id
              startMonth
              endMonth
              startingBalance
              targetAmount
              frequency
              type
              __typename
            }
            
            fragment BudgetCategoryFields on Category {
              id
              name
              icon
              order
              budgetVariability
              excludeFromBudget
              isSystemCategory
              updatedAt
              group {
                id
                type
                budgetVariability
                groupLevelBudgetingEnabled
                __typename
              }
              rolloverPeriod {
                ...BudgetRolloverPeriodFields
                __typename
              }
              __typename
            }
            
            fragment BudgetDataFields on BudgetData {
              monthlyAmountsByCategory {
                ...BudgetMonthlyAmountsByCategoryFields
                __typename
              }
              monthlyAmountsByCategoryGroup {
                ...BudgetMonthlyAmountsByCategoryGroupFields
                __typename
              }
              monthlyAmountsForFlexExpense {
                ...BudgetMonthlyAmountsForFlexExpenseFields
                __typename
              }
              totalsByMonth {
                ...BudgetTotalsByMonthFields
                __typename
              }
              __typename
            }
            
            fragment BudgetCategoryGroupFields on CategoryGroup {
              id
              name
              order
              type
              budgetVariability
              updatedAt
              groupLevelBudgetingEnabled
              categories {
                ...BudgetCategoryFields
                __typename
              }
              rolloverPeriod {
                id
                type
                startMonth
                endMonth
                startingBalance
                frequency
                targetAmount
                __typename
              }
              __typename
            }
            
            fragment BudgetDataGoalsV2Fields on GoalV2 {
              id
              name
              archivedAt
              completedAt
              priority
              imageStorageProvider
              imageStorageProviderId
              plannedContributions(startMonth: $startDate, endMonth: $endDate) {
                id
                month
                amount
                __typename
              }
              monthlyContributionSummaries(startMonth: $startDate, endMonth: $endDate) {
                month
                sum
                __typename
              }
              __typename
            }            
            """
        )

        variables = {
            "startDate": start_date,
            "endDate": end_date,
        }

        if not start_date and not end_date:
            # Default start_date to last month and end_date to next month
            today = datetime.today()

            # Get the first day of last month
            last_month = today.month - 1
            last_month_year = today.year
            first_day_of_last_month = 1
            if last_month < 1:
                last_month_year -= 1
                last_month = 12
            variables["startDate"] = datetime(
                last_month_year, last_month, first_day_of_last_month
            ).strftime("%Y-%m-%d")

            # Get the last day of next month
            next_month = today.month + 1
            next_month_year = today.year
            if next_month > 12:
                next_month_year += 1
                next_month = 1
            last_day_of_next_month = calendar.monthrange(next_month_year, next_month)[1]
            variables["endDate"] = datetime(
                next_month_year, next_month, last_day_of_next_month
            ).strftime("%Y-%m-%d")

        elif bool(start_date) != bool(end_date):
            raise Exception(
                "You must specify both a startDate and endDate, not just one of them."
            )

        return await self.gql_call(
            operation="Common_GetJointPlanningData",
            graphql_query=query,
            variables=variables,
        )

    async def get_subscription_details(self) -> Dict[str, Any]:
        """
        The type of subscription for the Monarch Money account.
        """
        query = gql(
            """
          query GetSubscriptionDetails {
            subscription {
              id
              paymentSource
              referralCode
              isOnFreeTrial
              hasPremiumEntitlement
              __typename
            }
          }
        """
        )
        return await self.gql_call(
            operation="GetSubscriptionDetails",
            graphql_query=query,
        )

    async def get_transactions_summary(self) -> Dict[str, Any]:
        """
        Gets transactions summary from the account.
        """

        query = gql(
            """
            query GetTransactionsPage($filters: TransactionFilterInput) {
              aggregates(filters: $filters) {
                summary {
                  ...TransactionsSummaryFields
                  __typename
                }
                __typename
              }
            }

            fragment TransactionsSummaryFields on TransactionsSummary {
              avg
              count
              max
              maxExpense
              sum
              sumIncome
              sumExpense
              first
              last
              __typename
            }
        """
        )
        return await self.gql_call(
            operation="GetTransactionsPage",
            graphql_query=query,
        )

    async def get_transactions_summary_card(self) -> Dict[str, Any]:
        """
        Gets transactions summary from the account using the transaction summary card operation.
        """

        query = gql(
            """
            query Web_GetTransactionsSummaryCard($filters: TransactionFilterInput!) {
              allTransactions(filters: $filters) {
                totalCount
                __typename
              }
            }
            """
        )

        variables = {
            "filters": {"search": "", "categories": [], "accounts": [], "tags": []}
        }

        return await self.gql_call(
            operation="Web_GetTransactionsSummaryCard",
            graphql_query=query,
            variables=variables,
        )

    async def get_transactions(
        self,
        limit: int = DEFAULT_RECORD_LIMIT,
        offset: Optional[int] = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: str = "",
        category_ids: List[str] = [],
        account_ids: List[str] = [],
        tag_ids: List[str] = [],
        has_attachments: Optional[bool] = None,
        has_notes: Optional[bool] = None,
        hidden_from_reports: Optional[bool] = None,
        is_split: Optional[bool] = None,
        is_recurring: Optional[bool] = None,
        imported_from_mint: Optional[bool] = None,
        synced_from_institution: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Gets transaction data from the account.

        :param limit: the maximum number of transactions to download, defaults to DEFAULT_RECORD_LIMIT.
        :param offset: the number of transactions to skip (offset) before retrieving results.
        :param start_date: the earliest date to get transactions from, in "yyyy-mm-dd" format.
        :param end_date: the latest date to get transactions from, in "yyyy-mm-dd" format.
        :param search: a string to filter transactions. use empty string for all results.
        :param category_ids: a list of category ids to filter.
        :param account_ids: a list of account ids to filter.
        :param tag_ids: a list of tag ids to filter.
        :param has_attachments: a bool to filter for whether the transactions have attachments.
        :param has_notes: a bool to filter for whether the transactions have notes.
        :param hidden_from_reports: a bool to filter for whether the transactions are hidden from reports.
        :param is_split: a bool to filter for whether the transactions are split.
        :param is_recurring: a bool to filter for whether the transactions are recurring.
        :param imported_from_mint: a bool to filter for whether the transactions were imported from mint.
        :param synced_from_institution: a bool to filter for whether the transactions were synced from an institution.
        """

        query = gql(
            """
          query GetTransactionsList($offset: Int, $limit: Int, $filters: TransactionFilterInput, $orderBy: TransactionOrdering) {
            allTransactions(filters: $filters) {
              totalCount
              results(offset: $offset, limit: $limit, orderBy: $orderBy) {
                id
                ...TransactionOverviewFields
                __typename
              }
              __typename
            }
            transactionRules {
              id
              __typename
            }
          }
    
          fragment TransactionOverviewFields on Transaction {
            id
            amount
            pending
            date
            hideFromReports
            plaidName
            notes
            isRecurring
            reviewStatus
            needsReview
            attachments {
              id
              extension
              filename
              originalAssetUrl
              publicId
              sizeBytes
              __typename
            }
            isSplitTransaction
            createdAt
            updatedAt
            category {
              id
              name
              __typename
            }
            merchant {
              name
              id
              transactionsCount
              __typename
            }
            account {
              id
              displayName
              __typename
            }
            tags {
              id
              name
              color
              order
              __typename
            }
            __typename
          }
        """
        )

        variables = {
            "offset": offset,
            "limit": limit,
            "orderBy": "date",
            "filters": {
                "search": search,
                "categories": category_ids,
                "accounts": account_ids,
                "tags": tag_ids,
            },
        }

        # If bool filters are not defined (i.e. None), then it should not apply the filter
        if has_attachments is not None:
            variables["filters"]["hasAttachments"] = has_attachments

        if has_notes is not None:
            variables["filters"]["hasNotes"] = has_notes

        if hidden_from_reports is not None:
            variables["filters"]["hideFromReports"] = hidden_from_reports

        if is_recurring is not None:
            variables["filters"]["isRecurring"] = is_recurring

        if is_split is not None:
            variables["filters"]["isSplit"] = is_split

        if imported_from_mint is not None:
            variables["filters"]["importedFromMint"] = imported_from_mint

        if synced_from_institution is not None:
            variables["filters"]["syncedFromInstitution"] = synced_from_institution

        if start_date and end_date:
            variables["filters"]["startDate"] = start_date
            variables["filters"]["endDate"] = end_date
        elif bool(start_date) != bool(end_date):
            raise Exception(
                "You must specify both a startDate and endDate, not just one of them."
            )

        return await self.gql_call(
            operation="GetTransactionsList", graphql_query=query, variables=variables
        )

    async def create_transaction(
        self,
        date: str,
        account_id: str,
        amount: float,
        merchant_name: str,
        category_id: str,
        notes: str = "",
        update_balance: bool = False,
    ) -> Dict[str, Any]:
        """
        Creates a transaction with the given parameters
        """
        query = gql(
            """
          mutation Common_CreateTransactionMutation($input: CreateTransactionMutationInput!) {
            createTransaction(input: $input) {
              errors {
                ...PayloadErrorFields
                __typename
              }
              transaction {
                id
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

        variables = {
            "input": {
                "date": date,
                "accountId": account_id,
                "amount": round(amount, 2),
                "merchantName": merchant_name,
                "categoryId": category_id,
                "notes": notes,
                "shouldUpdateBalance": update_balance,
            }
        }

        return await self.gql_call(
            operation="Common_CreateTransactionMutation",
            graphql_query=query,
            variables=variables,
        )

    async def delete_transaction(self, transaction_id: str) -> bool:
        """
        Deletes the given transaction.

        :param transaction_id: the ID of the transaction targeted for deletion.
        """
        query = gql(
            """
          mutation Common_DeleteTransactionMutation($input: DeleteTransactionMutationInput!) {
            deleteTransaction(input: $input) {
              deleted
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

        variables = {
            "input": {
                "transactionId": transaction_id,
            },
        }

        response = await self.gql_call(
            operation="Common_DeleteTransactionMutation",
            graphql_query=query,
            variables=variables,
        )

        if not response["deleteTransaction"]["deleted"]:
            raise RequestFailedException(response["deleteTransaction"]["errors"])

        return True

    async def get_transaction_categories(self) -> Dict[str, Any]:
        """
        Gets all the categories configured in the account.
        """
        query = gql(
            """
          query GetCategories {
            categories {
              ...CategoryFields
              __typename
            }
          }

          fragment CategoryFields on Category {
            id
            order
            name
            systemCategory
            isSystemCategory
            isDisabled
            updatedAt
            createdAt
            group {
              id
              name
              type
              __typename
            }
            __typename
          }
        """
        )
        return await self.gql_call(operation="GetCategories", graphql_query=query)

    async def delete_transaction_category(self, category_id: str) -> bool:
        query = gql(
            """
          mutation Web_DeleteCategory($id: UUID!, $moveToCategoryId: UUID) {
            deleteCategory(id: $id, moveToCategoryId: $moveToCategoryId) {
              errors {
                ...PayloadErrorFields
                __typename
              }
              deleted
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

        variables = {
            "id": category_id,
        }

        response = await self.gql_call(
            operation="Web_DeleteCategory", graphql_query=query, variables=variables
        )

        if not response["deleteCategory"]["deleted"]:
            raise RequestFailedException(response["deleteCategory"]["errors"])

        return True

    async def delete_transaction_categories(
        self, category_ids: List[str]
    ) -> List[Union[bool, BaseException]]:
        """
        Deletes a list of transaction categories.
        """
        return await asyncio.gather(
            *[self.delete_transaction_category(id) for id in category_ids],
            return_exceptions=True,
        )

    async def get_transaction_category_groups(self) -> Dict[str, Any]:
        """
        Gets all the category groups configured in the account.
        """
        query = gql(
            """
          query ManageGetCategoryGroups {
              categoryGroups {
                  id
                  name
                  order
                  type
                  updatedAt
                  createdAt
                  __typename
              }
          }
        """
        )
        return await self.gql_call(
            operation="ManageGetCategoryGroups", graphql_query=query
        )

    async def create_transaction_category(
        self,
        group_id: str,
        transaction_category_name: str,
        rollover_start_month: datetime = datetime.today().replace(day=1),
        icon: str = "\U00002753",
        rollover_enabled: bool = False,
        rollover_type: str = "monthly",
    ):
        """
        Creates a new transaction category
        :param group_id: The transaction category group id
        :param transaction_category_name: The name of the transaction category being created
        :param icon: The icon of the transaction category. This accepts the unicode string or emoji.
        :param rollover_start_month: The datetime of the rollover start month
        :param rollover_enabled: A bool whether the transaction category should be rolled over or not
        :param rollover_type: The budget roll over type
        """

        query = gql(
            """
            mutation Web_CreateCategory($input: CreateCategoryInput!) {
                createCategory(input: $input) {
                    errors {
                        ...PayloadErrorFields
                        __typename
                    }
                    category {
                        id
                        ...CategoryFormFields
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
            fragment CategoryFormFields on Category {
                id
                order
                name
                systemCategory
                systemCategoryDisplayName
                budgetVariability
                isSystemCategory
                isDisabled
                group {
                    id
                    type
                    groupLevelBudgetingEnabled
                    __typename
                }
                rolloverPeriod {
                    id
                    startMonth
                    startingBalance
                    __typename
                }
                __typename
            }
            """
        )
        variables = {
            "input": {
                "group": group_id,
                "name": transaction_category_name,
                "icon": icon,
                "rolloverEnabled": rollover_enabled,
                "rolloverType": rollover_type,
                "rolloverStartMonth": rollover_start_month.strftime("%Y-%m-%d"),
            },
        }

        return await self.gql_call(
            operation="Web_CreateCategory",
            graphql_query=query,
            variables=variables,
        )

    async def create_transaction_tag(self, name: str, color: str) -> Dict[str, Any]:
        """
        Creates a new transaction tag.
        :param name: The name of the tag
        :param color: The color of the tag.
          The observed format is six-digit RGB hexadecimal, including the leading number sign.
          Example: color="#19D2A5".
          More information can be found https://en.wikipedia.org/wiki/Web_colors#Hex_triplet.
          Does not appear to be limited to the color selections in the dashboard.
        """
        mutation = gql(
            """
            mutation Common_CreateTransactionTag($input: CreateTransactionTagInput!) {
              createTransactionTag(input: $input) {
                tag {
                  id
                  name
                  color
                  order
                  transactionCount
                  __typename
                }
                errors {
                  message
                  __typename
                }
                __typename
              }
            }
            """
        )
        variables = {"input": {"name": name, "color": color}}

        return await self.gql_call(
            operation="Common_CreateTransactionTag",
            graphql_query=mutation,
            variables=variables,
        )

    async def get_transaction_tags(self) -> Dict[str, Any]:
        """
        Gets all the tags configured in the account.
        """
        query = gql(
            """
          query GetHouseholdTransactionTags($search: String, $limit: Int, $bulkParams: BulkTransactionDataParams) {
            householdTransactionTags(
              search: $search
              limit: $limit
              bulkParams: $bulkParams
            ) {
              id
              name
              color
              order
              transactionCount
              __typename
            }
          }
        """
        )
        return await self.gql_call(
            operation="GetHouseholdTransactionTags", graphql_query=query
        )

    async def set_transaction_tags(
        self,
        transaction_id: str,
        tag_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Sets the tags on a transaction
        :param transaction_id: The transaction id
        :param tag_ids: The list of tag ids to set on the transaction.
          Overwrites existing tags. Empty list removes all tags.
        """

        query = gql(
            """
          mutation Web_SetTransactionTags($input: SetTransactionTagsInput!) {
            setTransactionTags(input: $input) {
              errors {
                ...PayloadErrorFields
                __typename
              }
              transaction {
                id
                tags {
                  id
                  __typename
                }
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

        variables = {
            "input": {"transactionId": transaction_id, "tagIds": tag_ids},
        }

        return await self.gql_call(
            operation="Web_SetTransactionTags",
            graphql_query=query,
            variables=variables,
        )

    async def get_transaction_details(
        self, transaction_id: str, redirect_posted: bool = True
    ) -> Dict[str, Any]:
        """
        Returns detailed information about a transaction.

        :param transaction_id: the transaction to fetch.
        :param redirect_posted: whether to redirect posted transactions. Defaults to True.
        """
        query = gql(
            """
          query GetTransactionDrawer($id: UUID!, $redirectPosted: Boolean) {
            getTransaction(id: $id, redirectPosted: $redirectPosted) {
              id
              amount
              pending
              isRecurring
              date
              originalDate
              hideFromReports
              needsReview
              reviewedAt
              reviewedByUser {
                id
                name
                __typename
              }
              plaidName
              notes
              hasSplitTransactions
              isSplitTransaction
              isManual
              splitTransactions {
                id
                ...TransactionDrawerSplitMessageFields
                __typename
              }
              originalTransaction {
                id
                ...OriginalTransactionFields
                __typename
              }
              attachments {
                id
                publicId
                extension
                sizeBytes
                filename
                originalAssetUrl
                __typename
              }
              account {
                id
                ...TransactionDrawerAccountSectionFields
                __typename
              }
              category {
                id
                __typename
              }
              goal {
                id
                __typename
              }
              merchant {
                id
                name
                transactionCount
                logoUrl
                recurringTransactionStream {
                  id
                  __typename
                }
                __typename
              }
              tags {
                id
                name
                color
                order
                __typename
              }
              needsReviewByUser {
                id
                __typename
              }
              __typename
            }
            myHousehold {
              users {
                id
                name
                __typename
              }
              __typename
            }
          }

          fragment TransactionDrawerSplitMessageFields on Transaction {
            id
            amount
            merchant {
              id
              name
              __typename
            }
            category {
              id
              name
              __typename
            }
            __typename
          }

          fragment OriginalTransactionFields on Transaction {
            id
            date
            amount
            merchant {
              id
              name
              __typename
            }
            __typename
          }

          fragment TransactionDrawerAccountSectionFields on Account {
            id
            displayName
            logoUrl
            id
            mask
            subtype {
              display
              __typename
            }
            __typename
          }
        """
        )

        variables = {
            "id": transaction_id,
            "redirectPosted": redirect_posted,
        }

        return await self.gql_call(
            operation="GetTransactionDrawer", variables=variables, graphql_query=query
        )

    async def get_transaction_splits(self, transaction_id: str) -> Dict[str, Any]:
        """
        Returns the transaction split information for a transaction.

        :param transaction_id: the transaction to query.
        """
        query = gql(
            """
          query TransactionSplitQuery($id: UUID!) {
            getTransaction(id: $id) {
              id
              amount
              category {
                id
                name
                __typename
              }
              merchant {
                id
                name
                __typename
              }
              splitTransactions {
                id
                merchant {
                  id
                  name
                  __typename
                }
                category {
                  id
                  name
                  __typename
                }
                amount
                notes
                __typename
              }
              __typename
            }
          }
        """
        )

        variables = {"id": transaction_id}

        return await self.gql_call(
            operation="TransactionSplitQuery", variables=variables, graphql_query=query
        )

    async def update_transaction_splits(
        self, transaction_id: str, split_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Creates, modifies, or deletes the splits for a given transaction.

        Returns the split information for the update transaction.

        :param transaction_id: the original transaction to modify.
        :param split_data: the splits to create, modify, or delete.
          If empty list or None is given, all splits will be deleted.
          If split_data is given, all existing splits for transaction_id will be replaced with the new splits.
          split_data takes the shape: [{"merchantName": "...", "amount": -12.34, "categoryId": "231"}, split2, split3, ...]
          sum([split.amount for split in split_data]) must equal transaction_id.amount.
        """
        query = gql(
            """
          mutation Common_SplitTransactionMutation($input: UpdateTransactionSplitMutationInput!) {
            updateTransactionSplit(input: $input) {
              errors {
                ...PayloadErrorFields
                __typename
              }
              transaction {
                id
                hasSplitTransactions
                splitTransactions {
                  id
                  merchant {
                    id
                    name
                    __typename
                  }
                  category {
                    id
                    name
                    __typename
                  }
                  amount
                  notes
                  __typename
                }
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

        if split_data is None:
            split_data = []

        variables = {
            "input": {"transactionId": transaction_id, "splitData": split_data}
        }

        return await self.gql_call(
            operation="Common_SplitTransactionMutation",
            variables=variables,
            graphql_query=query,
        )

    async def get_cashflow(
        self,
        limit: int = DEFAULT_RECORD_LIMIT,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gets all the categories configured in the account.
        """
        query = gql(
            """
          query Web_GetCashFlowPage($filters: TransactionFilterInput) {
            byCategory: aggregates(filters: $filters, groupBy: ["category"]) {
              groupBy {
                category {
                  id
                  name
                  group {
                    id
                    type
                    __typename
                  }
                  __typename
                }
                __typename
              }
              summary {
                sum
                __typename
              }
              __typename
            }
            byCategoryGroup: aggregates(filters: $filters, groupBy: ["categoryGroup"]) {
              groupBy {
                categoryGroup {
                  id
                  name
                  type
                  __typename
                }
                __typename
              }
              summary {
                sum
                __typename
              }
              __typename
            }
            byMerchant: aggregates(filters: $filters, groupBy: ["merchant"]) {
              groupBy {
                merchant {
                  id
                  name
                  logoUrl
                  __typename
                }
                __typename
              }
              summary {
                sumIncome
                sumExpense
                __typename
              }
              __typename
            }
            summary: aggregates(filters: $filters, fillEmptyValues: true) {
              summary {
                sumIncome
                sumExpense
                savings
                savingsRate
                __typename
              }
              __typename
            }
          }
        """
        )

        variables = {
            "limit": limit,
            "orderBy": "date",
            "filters": {
                "search": "",
                "categories": [],
                "accounts": [],
                "tags": [],
            },
        }

        if start_date and end_date:
            variables["filters"]["startDate"] = start_date
            variables["filters"]["endDate"] = end_date
        elif (start_date is None) ^ (end_date is None):
            raise Exception(
                "You must specify both a startDate and endDate, not just one of them."
            )
        else:
            variables["filters"]["startDate"] = self._get_start_of_current_month()
            variables["filters"]["endDate"] = self._get_end_of_current_month()

        return await self.gql_call(
            operation="Web_GetCashFlowPage", variables=variables, graphql_query=query
        )

    async def get_cashflow_summary(
        self,
        limit: int = DEFAULT_RECORD_LIMIT,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gets all the categories configured in the account.
        """
        query = gql(
            """
          query Web_GetCashFlowPage($filters: TransactionFilterInput) {
            summary: aggregates(filters: $filters, fillEmptyValues: true) {
              summary {
                sumIncome
                sumExpense
                savings
                savingsRate
                __typename
              }
              __typename
            }
          }
        """
        )

        variables = {
            "limit": limit,
            "orderBy": "date",
            "filters": {
                "search": "",
                "categories": [],
                "accounts": [],
                "tags": [],
            },
        }

        if start_date and end_date:
            variables["filters"]["startDate"] = start_date
            variables["filters"]["endDate"] = end_date
        elif bool(start_date) != bool(end_date):
            raise Exception(
                "You must specify both a startDate and endDate, not just one of them."
            )
        else:
            variables["filters"]["startDate"] = self._get_start_of_current_month()
            variables["filters"]["endDate"] = self._get_end_of_current_month()

        return await self.gql_call(
            operation="Web_GetCashFlowPage", variables=variables, graphql_query=query
        )

    async def update_transaction(
        self,
        transaction_id: str,
        category_id: Optional[str] = None,
        merchant_name: Optional[str] = None,
        goal_id: Optional[str] = None,
        amount: Optional[float] = None,
        date: Optional[str] = None,
        hide_from_reports: Optional[bool] = None,
        needs_review: Optional[bool] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Updates a single existing transaction as identified by the transaction_id
        The only required attribute is transaction_id. Calling this function with
        only the transaction_id will have no effect on the existing transaction data
        but will not cause an error.

        Comments on parameters:
        - transaction_id: Must match an existing transaction_id returned from Monarch
        - category_id: This parameter is only needed when the user wants to change the
            current category. When provided, it must match an existing category_id returned
            from Monarch. An empty string is equivalent to the parameter not being passed.
        - merchant_name: This parameter is only needed when the user wants to change
            the existing merchant name. Empty strings are ignored by the Monarch API
            when passed since a non-empty merchant name is required for all transactions
        - goal_id: This parameter is only needed when the user wants to change
            the existing goal.  When provided, it must match an existing goal_id returned
            from Monarch.  An empty string can be passed to clear out existing goal associations.
        - amount:  This parameter is only needed when the user wants to update
            the existing transaction amount. Empty strings are explicitly ignored by this code
            to avoid errors in the API.
        - date:  This parameter is only needed when the user wants to update
            the existing transaction date. Empty strings are explicitly ignored by this code
            to avoid errors in the API.  Required format is "2023-10-30"
        - hide_from_reports: This parameter is only needed when the user wants to update the
            existing transaction's hide-from-reports value.  If passed, the parameter is cast to
            Booleans to avoid API issues.
        - needs_review: This parameter is only needed when the user wants to update the
            existing transaction's needs-review value.  If passed, the parameter is cast to
            Booleans to avoid API issues.
        - notes: This parameter is only needed when the user wants to change
            the existing note.  An empty string can be passed to clear out existing notes.

        Examples:
        - To update a note: mm.update_transaction(
            transaction_id="160820461792094418",
            notes="my note")

        - To clear a note: mm.update_transaction(
            transaction_id="160820461792094418",
            notes="")

        - To update all items:
            mm.update_transaction(
                transaction_id="160820461792094418",
                category_id="160185840107743863",
                merchant_name="Amazon",
                goal_id="160826408575920275",
                amount=123.45,
                date="2023-11-09",
                hide_from_reports=False,
                needs_review="ThisWillBeCastToTrue",
                notes=f'Updated On: {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}',
            )
        """
        query = gql(
            """
        mutation Web_TransactionDrawerUpdateTransaction($input: UpdateTransactionMutationInput!) {
            updateTransaction(input: $input) {
            transaction {
                id
                amount
                pending
                date
                hideFromReports
                needsReview
                reviewedAt
                reviewedByUser {
                id
                name
                __typename
                }
                plaidName
                notes
                isRecurring
                category {
                id
                __typename
                }
                goal {
                id
                __typename
                }
                merchant {
                id
                name
                __typename
                }
                __typename
            }
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

        variables: dict[str, Any] = {
            "input": {
                "id": transaction_id,
            }
        }

        # Within Monarch, these values cannot be empty. Monarch will simply ignore updates
        # to category and merchant name that are empty strings or None.
        # As such, no need to avoid adding to variables
        variables["input"].update({"category": category_id})
        variables["input"].update({"name": merchant_name})

        # Monarch will not accept nulls for amount and date.
        # Don't update values if an empty string is passed or if parameter is None
        if amount:
            variables["input"].update({"amount": amount})
        if date:
            variables["input"].update({"date": date})

        # Don't update values if the parameter is not passed or explicitly set to None.
        # Passed values must be cast to bool to avoid API errors
        if hide_from_reports is not None:
            variables["input"].update({"hideFromReports": bool(hide_from_reports)})
        if needs_review is not None:
            variables["input"].update({"needsReview": bool(needs_review)})

        # We want an empty string to clear the goal and notes parameters but the values should not
        # be cleared if the parameter isn't passed
        # Don't update values if the parameter is not passed or explicitly set to None.
        if goal_id is not None:
            variables["input"].update({"goalId": goal_id})
        if notes is not None:
            variables["input"].update({"notes": notes})

        return await self.gql_call(
            operation="Web_TransactionDrawerUpdateTransaction",
            variables=variables,
            graphql_query=query,
        )

    async def set_budget_amount(
        self,
        amount: float,
        category_id: Optional[str] = None,
        category_group_id: Optional[str] = None,
        timeframe: str = "month",  # I believe this is the only valid value right now
        start_date: Optional[str] = None,
        apply_to_future: bool = False,
    ) -> Dict[str, Any]:
        """
        Updates the budget amount for the given category.

        :param category_id:
            The ID of the category to set the budget for (cannot be provided w/ category_group_id)
        :param category_group_id:
            The ID of the category group to set the budget for (cannot be provided w/ category_id)
        :param amount:
            The amount to set the budget to. Can be negative (to indicate over-budget). A zero
            value will "unset" or "clear" the budget for the given category.
        :param timeframe:
            The timeframe of the budget. As of writing, it is believed that `month` is the
            only valid value for this parameter.
        :param start_date:
            The beginning of the given timeframe (ex: 2023-12-01). If not specified, then the
            beginning of today's month will be used.
        :param apply_to_future:
            Whether to apply the new budget amount to all proceeding timeframes
        """

        # Will be true if neither of the parameters are set, or both are
        if (category_id is None) is (category_group_id is None):
            raise Exception(
                "You must specify either a category_id OR category_group_id; not both"
            )

        query = gql(
            """
          mutation Common_UpdateBudgetItem($input: UpdateOrCreateBudgetItemMutationInput!) {
            updateOrCreateBudgetItem(input: $input) {
              budgetItem {
                id
                budgetAmount
                __typename
              }
              __typename
            }
          }
        """
        )

        variables = {
            "input": {
                "startDate": start_date,
                "timeframe": timeframe,
                "categoryId": category_id,
                "categoryGroupId": category_group_id,
                "amount": amount,
                "applyToFuture": apply_to_future,
            }
        }

        if start_date is None:
            variables["input"]["startDate"] = self._get_start_of_current_month()

        return await self.gql_call(
            operation="Common_UpdateBudgetItem",
            variables=variables,
            graphql_query=query,
        )

    async def upload_account_balance_history(
        self, account_id: str, csv_content: str
    ) -> None:
        """
        Uploads the account balance history csv for a given account.

        :param account_id: The account ID to apply the history to.
        :param csv_content: CSV representation of the balance history.
        """
        if not account_id or not csv_content:
            raise RequestFailedException("account_id and csv_content cannot be empty")

        filename = "upload.csv"
        form = FormData()
        form.add_field("files", csv_content, filename=filename, content_type="text/csv")
        form.add_field("account_files_mapping", json.dumps({filename: account_id}))

        async with ClientSession(headers=self._headers) as session:
            resp = await session.post(
                MonarchMoneyEndpoints.getAccountBalanceHistoryUploadEndpoint(),
                json=form,
            )
            if resp.status != 200:
                raise RequestFailedException(f"HTTP Code {resp.status}: {resp.reason}")

    async def get_recurring_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetches upcoming recurring transactions from Monarch Money's API.  This includes
        all merchant data, as well as the accounts where the charge will take place.
        """
        query = gql(
            """
            query Web_GetUpcomingRecurringTransactionItems($startDate: Date!, $endDate: Date!, $filters: RecurringTransactionFilter) {
              recurringTransactionItems(
                startDate: $startDate
                endDate: $endDate
                filters: $filters
              ) {
                stream {
                  id
                  frequency
                  amount
                  isApproximate
                  merchant {
                    id
                    name
                    logoUrl
                    __typename
                  }
                  __typename
                }
                date
                isPast
                transactionId
                amount
                amountDiff
                category {
                  id
                  name
                  __typename
                }
                account {
                  id
                  displayName
                  logoUrl
                  __typename
                }
                __typename
              }
            }
        """
        )

        variables = {"startDate": start_date, "endDate": end_date}

        if (start_date is None) ^ (end_date is None):
            raise Exception(
                "You must specify both a start_date and end_date, not just one of them."
            )
        elif start_date is None and end_date is None:
            variables["startDate"] = self._get_start_of_current_month()
            variables["endDate"] = self._get_end_of_current_month()

        return await self.gql_call(
            "Web_GetUpcomingRecurringTransactionItems", query, variables
        )

    def _get_current_date(self) -> str:
        """
        Returns the current date as a string formatted like %Y-%m-%d.
        """
        return datetime.now().strftime("%Y-%m-%d")

    def _get_start_of_current_month(self) -> str:
        """
        Returns the date for the first day of the current month as a string formatted as %Y-%m-%d.
        """
        now = datetime.now()
        start_of_month = now.replace(day=1)
        return start_of_month.strftime("%Y-%m-%d")

    def _get_end_of_current_month(self) -> str:
        """
        Returns the date for the last day of the current month as a string formatted as %Y-%m-%d.
        """
        now = datetime.now()
        _, last_day = calendar.monthrange(now.year, now.month)
        end_of_month = now.replace(day=last_day)
        return end_of_month.strftime("%Y-%m-%d")

    async def gql_call(
        self,
        operation: str,
        graphql_query: DocumentNode,
        variables: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        """
        Makes a GraphQL call to Monarch Money's API.
        """
        return await self._get_graphql_client().execute_async(
            document=graphql_query, operation_name=operation, variable_values=variables
        )

    def save_session(self, filename: Optional[str] = None) -> None:
        """
        Saves the auth token needed to access a Monarch Money account.
        """
        if filename is None:
            filename = self._session_file
        filename = os.path.abspath(filename)

        session_data = {"token": self._token}

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as fh:
            pickle.dump(session_data, fh)

    def load_session(self, filename: Optional[str] = None) -> None:
        """
        Loads pre-existing auth token from a Python pickle file.
        """
        if filename is None:
            filename = self._session_file

        with open(filename, "rb") as fh:
            data = pickle.load(fh)
            self.set_token(data["token"])
            self._headers["Authorization"] = f"Token {self._token}"

    def delete_session(self, filename: Optional[str] = None) -> None:
        """
        Deletes the session file.
        """
        if filename is None:
            filename = self._session_file

        if os.path.exists(filename):
            os.remove(filename)

    async def _login_user(
        self, email: str, password: str, mfa_secret_key: Optional[str]
    ) -> None:
        """
        Performs the initial login to a Monarch Money account.
        """
        data = {
            "password": password,
            "supports_mfa": True,
            "trusted_device": False,
            "username": email,
        }

        if mfa_secret_key:
            data["totp"] = oathtool.generate_otp(mfa_secret_key)

        async with ClientSession(headers=self._headers) as session:
            async with session.post(
                MonarchMoneyEndpoints.getLoginEndpoint(), json=data
            ) as resp:
                if resp.status == 403:
                    raise RequireMFAException("Multi-Factor Auth Required")
                elif resp.status != 200:
                    raise LoginFailedException(
                        f"HTTP Code {resp.status}: {resp.reason}"
                    )

                response = await resp.json()
                self.set_token(response["token"])
                self._headers["Authorization"] = f"Token {self._token}"

    async def _multi_factor_authenticate(
        self, email: str, password: str, code: str
    ) -> None:
        """
        Performs the MFA step of login.
        """
        data = {
            "password": password,
            "supports_mfa": True,
            "totp": code,
            "trusted_device": False,
            "username": email,
        }

        async with ClientSession(headers=self._headers) as session:
            async with session.post(
                MonarchMoneyEndpoints.getLoginEndpoint(), json=data
            ) as resp:
                if resp.status != 200:
                    try:
                        response = await resp.json()
                        if "detail" in response:
                            error_message = response["detail"]
                            raise RequireMFAException(error_message)
                        elif "error_code" in response:
                            error_message = response["error_code"]
                        else:
                            error_message = f"Unrecognized error message: '{response}'"
                        raise LoginFailedException(error_message)
                    except:
                        raise LoginFailedException(
                            f"HTTP Code {resp.status}: {resp.reason}\nRaw response: {resp.text}"
                        )
                response = await resp.json()
                self.set_token(response["token"])
                self._headers["Authorization"] = f"Token {self._token}"

    def _get_graphql_client(self) -> Client:
        """
        Creates a correctly configured GraphQL client for connecting to Monarch Money.
        """
        if self._headers is None:
            raise LoginFailedException(
                "Make sure you call login() first or provide a session token!"
            )
        transport = AIOHTTPTransport(
            url=MonarchMoneyEndpoints.getGraphQL(),
            headers=self._headers,
            timeout=self._timeout,
        )
        return Client(
            transport=transport,
            fetch_schema_from_transport=False,
            execute_timeout=self._timeout,
        )
