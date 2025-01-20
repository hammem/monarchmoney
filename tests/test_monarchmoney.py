import os
import pickle
import unittest
from unittest.mock import patch

import json
from gql import Client
from monarchmoney import MonarchMoney
from monarchmoney.monarchmoney import LoginFailedException


class TestMonarchMoney(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """
        Set up any necessary data or variables for the tests here.
        This method will be called before each test method is executed.
        """
        with open("temp_session.pickle", "wb") as fh:
            session_data = {
                "cookies": {"test_cookie": "test_value"},
                "token": "test_token",
            }
            pickle.dump(session_data, fh)
        self.monarch_money = MonarchMoney()
        self.monarch_money.load_session("temp_session.pickle")

    @patch.object(Client, "execute_async")
    async def test_get_accounts(self, mock_execute_async):
        """
        Test the get_accounts method.
        """
        mock_execute_async.return_value = TestMonarchMoney.loadTestData(
            filename="get_accounts.json",
        )
        result = await self.monarch_money.get_accounts()
        mock_execute_async.assert_called_once()
        self.assertIsNotNone(result, "Expected result to not be None")
        self.assertEqual(len(result["accounts"]), 7, "Expected 7 accounts")
        self.assertEqual(
            result["accounts"][0]["displayName"],
            "Brokerage",
            "Expected displayName to be Brokerage",
        )
        self.assertEqual(
            result["accounts"][1]["currentBalance"],
            1000.02,
            "Expected currentBalance to be 1000.02",
        )
        self.assertFalse(
            result["accounts"][2]["isAsset"],
            "Expected isAsset to be False",
        )
        self.assertEqual(
            result["accounts"][3]["subtype"]["display"],
            "Roth IRA",
            "Expected subtype display to be 'Roth IRA'",
        )
        self.assertFalse(
            result["accounts"][4]["isManual"],
            "Expected isManual to be False",
        )
        self.assertEqual(
            result["accounts"][5]["institution"]["name"],
            "Rando Employer Investments",
            "Expected institution name to be 'Rando Employer Investments'",
        )
        self.assertEqual(
            result["accounts"][6]["id"],
            "90000000030",
            "Expected id to be '90000000030'",
        )
        self.assertEqual(
            result["accounts"][6]["type"]["name"],
            "loan",
            "Expected type name to be 'loan'",
        )

    @patch.object(Client, "execute_async")
    async def test_get_transactions_summary(self, mock_execute_async):
        """
        Test the get_transactions_summary method.
        """
        mock_execute_async.return_value = TestMonarchMoney.loadTestData(
            filename="get_transactions_summary.json",
        )
        result = await self.monarch_money.get_transactions_summary()
        mock_execute_async.assert_called_once()
        self.assertIsNotNone(result, "Expected result to not be None")
        self.assertEqual(
            result["aggregates"][0]["summary"]["sumIncome"],
            50000,
            "Expected sumIncome to be 50000",
        )

    @patch.object(Client, "execute_async")
    async def test_delete_account(self, mock_execute_async):
        """
        Test the delete_account method.
        """

        mock_execute_async.return_value = {
            "deleteAccount": {
                "deleted": True,
                "errors": None,
                "__typename": "DeleteAccountMutation",
            }
        }

        result = await self.monarch_money.delete_account("170123456789012345")

        mock_execute_async.assert_called_once()

        kwargs = mock_execute_async.call_args.kwargs
        self.assertEqual(kwargs["operation_name"], "Common_DeleteAccount")
        self.assertEqual(kwargs["variable_values"], {"id": "170123456789012345"})

        self.assertIsNotNone(result, "Expected result to not be None")
        self.assertEqual(result["deleteAccount"]["deleted"], True)
        self.assertEqual(result["deleteAccount"]["errors"], None)

    @patch.object(Client, "execute_async")
    async def test_get_account_type_options(self, mock_execute_async):
        """
        Test the get_account_type_options method.
        """
        # Mock the execute_async method to return a test result
        mock_execute_async.return_value = TestMonarchMoney.loadTestData(
            filename="get_account_type_options.json",
        )

        # Call the get_account_type_options method
        result = await self.monarch_money.get_account_type_options()

        # Assert that the execute_async method was called once
        mock_execute_async.assert_called_once()

        # Assert that the result is not None
        self.assertIsNotNone(result, "Expected result to not be None")

        # Assert that the result matches the expected output
        self.assertEqual(
            len(result["accountTypeOptions"]), 10, "Expected 10 account type options"
        )
        self.assertEqual(
            result["accountTypeOptions"][0]["type"]["name"],
            "depository",
            "Expected first account type option name to be 'depository'",
        )
        self.assertEqual(
            result["accountTypeOptions"][1]["type"]["name"],
            "brokerage",
            "Expected second account type option name to be 'brokerage'",
        )
        self.assertEqual(
            result["accountTypeOptions"][2]["type"]["name"],
            "real_estate",
            "Expected third account type option name to be 'real_estate'",
        )

    @patch.object(Client, "execute_async")
    async def test_get_merchants(self, mock_execute_async):
        """
        Test the get_merchants method.
        """
        # Mock the execute_async method to return test data
        mock_execute_async.return_value = TestMonarchMoney.loadTestData(
            filename="get_merchants.json",
        )

        # Call the get_merchants method
        result = await self.monarch_money.get_merchants()

        # Assert execute_async was called once
        mock_execute_async.assert_called_once()

        # Verify result is not None
        self.assertIsNotNone(result, "Expected result to not be None")

        # Verify merchants data structure
        self.assertIn("merchants", result, "Expected merchants key in response")
        self.assertEqual(
            len(result["merchants"]), 3, "Expected 3 merchants"
        )
        self.assertEqual(
            result["merchants"][0]["name"],
            "Amazon",
            "Expected first merchant name to be 'Amazon'"
        )
        self.assertEqual(
            result["merchants"][1]["name"],
            "Target",
            "Expected second merchant name to be 'Target'"
        )

    @patch.object(Client, "execute_async")
    async def test_get_categories(self, mock_execute_async):
        """
        Test the get_categories method.
        """
        # Mock the execute_async method to return a test result
        mock_execute_async.return_value = TestMonarchMoney.loadTestData(
            filename="get_categories.json",
        )

        # Call the get_categories method
        result = await self.monarch_money.get_categories()

        # Assert that the execute_async method was called once
        mock_execute_async.assert_called_once()

        # Assert that the result is not None
        self.assertIsNotNone(result, "Expected result to not be None")

        # Assert that the result matches the expected output
        self.assertEqual(
            len(result["categories"]), 5, "Expected 5 categories"
        )
        self.assertEqual(
            result["categories"][0]["name"],
            "Groceries",
            "Expected first category name to be 'Groceries'",
        )
        self.assertEqual(
            result["categories"][1]["name"],
            "Utilities",
            "Expected second category name to be 'Utilities'",
        )
        self.assertEqual(
            result["categories"][2]["name"],
            "Rent",
            "Expected third category name to be 'Rent'",
        )
        self.assertEqual(
            result["categories"][3]["name"],
            "Entertainment",
            "Expected fourth category name to be 'Entertainment'",
        )
        self.assertEqual(
            result["categories"][4]["name"],
            "Transportation",
            "Expected fifth category name to be 'Transportation'",
        )
        self.assertEqual(
            result["accountTypeOptions"][1]["type"]["name"],
            "brokerage",
            "Expected second account type option name to be 'brokerage'",
        )
        self.assertEqual(
            result["accountTypeOptions"][2]["type"]["name"],
            "real_estate",
            "Expected third account type option name to be 'real_estate'",
        )

    @patch.object(Client, "execute_async")
    async def test_get_account_holdings(self, mock_execute_async):
        """
        Test the get_account_holdings method.
        """
        # Mock the execute_async method to return a test result
        mock_execute_async.return_value = TestMonarchMoney.loadTestData(
            filename="get_account_holdings.json",
        )

        # Call the get_account_holdings method
        result = await self.monarch_money.get_account_holdings(account_id=1234)

        # Assert that the execute_async method was called once
        mock_execute_async.assert_called_once()

        # Assert that the result is not None
        self.assertIsNotNone(result, "Expected result to not be None")

        # Assert that the result matches the expected output
        self.assertEqual(
            len(result["portfolio"]["aggregateHoldings"]["edges"]),
            3,
            "Expected 3 holdings",
        )
        self.assertEqual(
            result["portfolio"]["aggregateHoldings"]["edges"][0]["node"]["quantity"],
            101,
            "Expected first holding to be 101 in quantity",
        )
        self.assertEqual(
            result["portfolio"]["aggregateHoldings"]["edges"][1]["node"]["totalValue"],
            10000,
            "Expected second holding to be 10000 in total value",
        )
        self.assertEqual(
            result["portfolio"]["aggregateHoldings"]["edges"][2]["node"]["holdings"][0][
                "name"
            ],
            "U S Dollar",
            "Expected third holding name to be 'U S Dollar'",
        )

    async def test_login(self):
        """
        Test the login method with empty values for email and password.
        """
        with self.assertRaises(LoginFailedException):
            await self.monarch_money.login(use_saved_session=False)
        with self.assertRaises(LoginFailedException):
            await self.monarch_money.login(
                email="", password="", use_saved_session=False
            )

    @patch("builtins.input", return_value="")
    @patch("getpass.getpass", return_value="")
    async def test_interactive_login(self, _input_mock, _getpass_mock):
        """
        Test the interactive_login method with empty values for email and password.
        """
        with self.assertRaises(LoginFailedException):
            await self.monarch_money.interactive_login(use_saved_session=False)

    @classmethod
    def loadTestData(cls, filename) -> dict:
        filename = f"{os.path.dirname(os.path.realpath(__file__))}/{filename}"
        with open(filename, "r") as file:
            return json.load(file)

    def tearDown(self):
        """
        Tear down any necessary data or variables for the tests here.
        This method will be called after each test method is executed.
        """
        self.monarch_money.delete_session("temp_session.pickle")


if __name__ == "__main__":
    unittest.main()
