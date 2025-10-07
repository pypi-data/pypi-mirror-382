import json
import os
import unittest
from unittest.mock import MagicMock, patch

from zededa_edgeai_sdk.client import ZededaEdgeAIClient, logout
from zededa_edgeai_sdk.zededa_edgeai_sdk import ZededaEdgeAISDK


class TestEdgeAISDK(unittest.TestCase):
    def setUp(self):
        self.env_backup = os.environ.copy()
        for key in [
            "EDGEAI_CURRENT_CATALOG",
            "EDGEAI_ACCESS_TOKEN",
            "MLFLOW_TRACKING_TOKEN",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "MLFLOW_S3_ENDPOINT_URL",
            "MLFLOW_TRACKING_URI",
            "MINIO_BUCKET",
            "EDGEAI_BACKEND_URL",
        ]:
            os.environ.pop(key, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_backup)

    @patch("zededa_edgeai_sdk.services.http.requests.request")
    def test_login_with_credentials_sets_environment(self, mock_request):
        login_payload = {
            "access_token": "token-123",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_info": {},
        }

        login_response = MagicMock()
        login_response.status_code = 200
        login_response.json.return_value = login_payload
        login_response.headers = {"Content-Type": "application/json"}
        login_response.text = json.dumps(login_payload)
        login_response.reason = "OK"

        # Add user-info response for catalog selection
        user_info_payload = {
            "available_catalogs": ["development"],
            "all_catalogs": ["development"],
            "permissions": {
                "catalogs": [
                    {
                        "ids": ["development"],
                        "permissions": ["models:read"],
                    }
                ]
            },
        }
        user_info_response = MagicMock()
        user_info_response.status_code = 200
        user_info_response.json.return_value = user_info_payload
        user_info_response.headers = {"Content-Type": "application/json"}
        user_info_response.text = json.dumps(user_info_payload)
        user_info_response.reason = "OK"

        # Add scoped token response
        scoped_payload = {"access_token": "scoped-token-dev"}
        scoped_response = MagicMock()
        scoped_response.status_code = 200
        scoped_response.json.return_value = scoped_payload
        scoped_response.headers = {"Content-Type": "application/json"}
        scoped_response.text = json.dumps(scoped_payload)
        scoped_response.reason = "OK"

        minio_payload = {
            "access_key": "ak",
            "secret_key": "sk",
            "endpoint_url": "https://minio",
            "bucket": "bucket",
            "mlflow_tracking_uri": "https://mlflow",
        }

        minio_response = MagicMock()
        minio_response.status_code = 200
        minio_response.json.return_value = minio_payload
        minio_response.headers = {"Content-Type": "application/json"}
        minio_response.text = json.dumps(minio_payload)
        minio_response.reason = "OK"

        mock_request.side_effect = [login_response, user_info_response, scoped_response, minio_response]

        client = ZededaEdgeAIClient(service_url="https://backend")
        credentials = client.login(
            "development",
            email="user@example.com",
            password="password123",
        )

        # Check that sensitive data is sanitized in the return value
        self.assertEqual(credentials["backend_jwt"], "scoped...-dev")  # Long token gets first 6 and last 4 chars
        self.assertEqual(credentials["catalog_id"], "development")
        self.assertIn("environment", credentials)

        # But environment variables should still have the actual values
        self.assertEqual(os.environ["MLFLOW_TRACKING_TOKEN"], "scoped-token-dev")
        self.assertEqual(os.environ["EDGEAI_CURRENT_CATALOG"], "development")

        self.assertEqual(mock_request.call_count, 4)
        first_call = mock_request.call_args_list[0]
        self.assertEqual(first_call.args[0], "POST")
        self.assertEqual(first_call.args[1], "https://backend/api/v1/auth/login")
        self.assertEqual(
            first_call.kwargs["json"],
            {
                "email": "user@example.com",
                "password": "password123",
                "catalog_id": "development",
            },
        )

    @patch("builtins.input")
    @patch("zededa_edgeai_sdk.services.http.requests.request")
    def test_login_with_credentials_without_catalog_auto_selects_single(self, mock_request, mock_input):
        login_payload = {"access_token": "token-123", "token_type": "bearer", "expires_in": 3600}
        login_response = MagicMock(status_code=200, reason="OK")
        login_response.json.return_value = login_payload
        login_response.headers = {"Content-Type": "application/json"}
        login_response.text = json.dumps(login_payload)

        user_info_payload = {
            "available_catalogs": ["dev"],
            "all_catalogs": ["dev"],
            "permissions": {
                "catalogs": [
                    {
                        "ids": ["dev"],
                        "permissions": ["models:read"],
                    }
                ]
            },
        }
        catalogs_response = MagicMock(status_code=200, reason="OK")
        catalogs_response.json.return_value = user_info_payload
        catalogs_response.headers = {"Content-Type": "application/json"}
        catalogs_response.text = json.dumps(user_info_payload)

        scoped_payload = {"access_token": "scoped-token"}
        scoped_response = MagicMock(status_code=200, reason="OK")
        scoped_response.json.return_value = scoped_payload
        scoped_response.headers = {"Content-Type": "application/json"}
        scoped_response.text = json.dumps(scoped_payload)

        minio_payload = {
            "access_key": "ak",
            "secret_key": "sk",
            "endpoint_url": "https://minio",
            "bucket": "bucket",
            "mlflow_tracking_uri": "https://mlflow",
        }
        minio_response = MagicMock(status_code=200, reason="OK")
        minio_response.json.return_value = minio_payload
        minio_response.headers = {"Content-Type": "application/json"}
        minio_response.text = json.dumps(minio_payload)

        mock_request.side_effect = [login_response, catalogs_response, scoped_response, minio_response]

        client = ZededaEdgeAIClient(service_url="https://backend")
        credentials = client.login(
            None,
            email="user@example.com",
            password="password123",
        )

        self.assertEqual(credentials["catalog_id"], "dev")
        self.assertEqual(os.environ["EDGEAI_CURRENT_CATALOG"], "dev")
        self.assertEqual(os.environ["MLFLOW_TRACKING_TOKEN"], "scoped-token")
        mock_input.assert_not_called()
        self.assertEqual(mock_request.call_count, 4)
        first_call = mock_request.call_args_list[0]
        self.assertNotIn("catalog_id", first_call.kwargs["json"])

    @patch("builtins.input", side_effect=["2"])
    @patch("zededa_edgeai_sdk.services.http.requests.request")
    def test_login_with_credentials_prompts_for_catalog_selection(self, mock_request, mock_input):
        login_payload = {"access_token": "token-123", "token_type": "bearer", "expires_in": 3600}
        login_response = MagicMock(status_code=200, reason="OK")
        login_response.json.return_value = login_payload
        login_response.headers = {"Content-Type": "application/json"}
        login_response.text = json.dumps(login_payload)

        user_info_payload = {
            "available_catalogs": ["dev", "prod"],
            "all_catalogs": ["dev", "prod"],
            "permissions": {
                "catalogs": [
                    {
                        "ids": ["dev", "prod"],
                        "permissions": ["models:write"],
                    }
                ]
            },
        }
        catalogs_response = MagicMock(status_code=200, reason="OK")
        catalogs_response.json.return_value = user_info_payload
        catalogs_response.headers = {"Content-Type": "application/json"}
        catalogs_response.text = json.dumps(user_info_payload)

        scoped_payload = {"access_token": "scoped-token"}
        scoped_response = MagicMock(status_code=200, reason="OK")
        scoped_response.json.return_value = scoped_payload
        scoped_response.headers = {"Content-Type": "application/json"}
        scoped_response.text = json.dumps(scoped_payload)

        minio_payload = {
            "access_key": "ak",
            "secret_key": "sk",
            "endpoint_url": "https://minio",
            "bucket": "bucket",
            "mlflow_tracking_uri": "https://mlflow",
        }
        minio_response = MagicMock(status_code=200, reason="OK")
        minio_response.json.return_value = minio_payload
        minio_response.headers = {"Content-Type": "application/json"}
        minio_response.text = json.dumps(minio_payload)

        mock_request.side_effect = [login_response, catalogs_response, scoped_response, minio_response]

        client = ZededaEdgeAIClient(service_url="https://backend")
        credentials = client.login(
            None,
            email="user@example.com",
            password="password123",
        )

        self.assertEqual(credentials["catalog_id"], "prod")
        self.assertEqual(os.environ["EDGEAI_CURRENT_CATALOG"], "prod")
        mock_input.assert_called_once()
        self.assertEqual(mock_request.call_count, 4)

    def test_browser_login_auto_selects_single_catalog(self):
        sdk = ZededaEdgeAISDK("https://backend", ui_url="https://ui")

        with patch.object(sdk, "oauth_login", return_value="general-token") as mocked_oauth:
            with patch.object(
                sdk,
                "_get_catalogs",
                return_value={
                    "available_catalogs": [{"catalog_id": "dev", "description": "Dev"}],
                    "all_catalogs": [{"catalog_id": "dev", "description": "Dev"}]
                },
            ):
                with patch.object(
                    sdk,
                    "_get_catalog_scoped_token",
                    return_value={"access_token": "scoped-token"},
                ) as mocked_scoped:
                    with patch.object(
                        sdk,
                        "_get_minio_credentials",
                        return_value={
                            "backend_jwt": "scoped-token",
                            "aws_access_key_id": "ak",
                            "aws_secret_access_key": "sk",
                            "endpoint_url": "https://minio",
                            "bucket": "bucket",
                            "mlflow_tracking_uri": "https://mlflow",
                        },
                    ) as mocked_minio:
                        credentials = sdk.login_with_browser(None)

        mocked_oauth.assert_called_once_with(None)
        mocked_scoped.assert_called_once_with("general-token", "dev")
        mocked_minio.assert_called_once_with("scoped-token", "dev")
        self.assertEqual(credentials["catalog_id"], "dev")

    def test_browser_login_prompts_for_catalog_selection(self):
        sdk = ZededaEdgeAISDK("https://backend", ui_url="https://ui")

        catalogs = [
            {"catalog_id": "dev", "description": "Development"},
            {"catalog_id": "prod", "description": "Production"},
        ]

        with patch.object(sdk, "oauth_login", return_value="general-token") as mocked_oauth:
            with patch.object(sdk, "_get_catalogs", return_value={
                "available_catalogs": catalogs,
                "all_catalogs": catalogs
            }) as mocked_catalogs:
                with patch.object(
                    sdk,
                    "_get_catalog_scoped_token",
                    return_value={
                        "access_token": "scoped-token",
                    },
                ) as mocked_scoped:
                    with patch.object(
                        sdk,
                        "_get_minio_credentials",
                        return_value={
                            "backend_jwt": "scoped-token",
                            "aws_access_key_id": "ak",
                            "aws_secret_access_key": "sk",
                            "endpoint_url": "https://minio",
                            "bucket": "bucket",
                            "mlflow_tracking_uri": "https://mlflow",
                        },
                    ) as mocked_minio:
                        with patch("builtins.input", side_effect=["2"]):
                            credentials = sdk.login_with_browser(None)

        mocked_oauth.assert_called_once_with(None)
        mocked_catalogs.assert_called_once_with("general-token")
        mocked_scoped.assert_called_once_with("general-token", "prod")
        mocked_minio.assert_called_once_with("scoped-token", "prod")
        self.assertEqual(credentials["catalog_id"], "prod")

    def test_logout_clears_environment(self):
        os.environ["MLFLOW_TRACKING_TOKEN"] = "abc"
        os.environ["EDGEAI_CURRENT_CATALOG"] = "dev"
        os.environ["EDGEAI_ACCESS_TOKEN"] = "token"
        os.environ["EDGEAI_BACKEND_URL"] = "https://backend"

        from zededa_edgeai_sdk.commands import logout as logout_module

        with patch.object(
            logout_module,
            "_perform_backend_logout",
            return_value={
                "attempted": True,
                "success": True,
                "status_code": 204,
                "message": "Backend logout succeeded",
            },
        ) as mock_backend_logout:
            result = logout()

        self.assertNotIn("MLFLOW_TRACKING_TOKEN", os.environ)
        self.assertNotIn("EDGEAI_CURRENT_CATALOG", os.environ)
        self.assertNotIn("EDGEAI_ACCESS_TOKEN", os.environ)
        self.assertNotIn("EDGEAI_BACKEND_URL", os.environ)

        mock_backend_logout.assert_called_once()
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["backend"]["success"])

    def test_logout_backend_failure_returns_partial(self):
        os.environ["EDGEAI_ACCESS_TOKEN"] = "token"
        os.environ["EDGEAI_BACKEND_URL"] = "https://backend"

        from zededa_edgeai_sdk.commands import logout as logout_module

        with patch.object(
            logout_module,
            "_perform_backend_logout",
            return_value={
                "attempted": True,
                "success": False,
                "status_code": None,
                "message": "Backend logout request failed: boom",
            },
        ) as mock_backend_logout:
            result = logout()

        self.assertEqual(result["status"], "partial")
        backend = result["backend"]
        self.assertTrue(backend["attempted"])
        self.assertFalse(backend["success"])
        self.assertIn("failed", backend["message"])

        self.assertNotIn("EDGEAI_ACCESS_TOKEN", os.environ)
        self.assertNotIn("EDGEAI_BACKEND_URL", os.environ)

        mock_backend_logout.assert_called_once()

    def test_logout_without_token_skips_backend(self):
        from zededa_edgeai_sdk.commands import logout as logout_module

        with patch.object(
            logout_module,
            "_perform_backend_logout",
        ) as mock_backend_logout:
            result = logout()

        self.assertEqual(result["status"], "success")
        backend = result["backend"]
        self.assertFalse(backend["attempted"])
        mock_backend_logout.assert_not_called()

    def test_login_requires_email_and_password(self):
        client = ZededaEdgeAIClient(service_url="https://backend")
        result = client.login("development", email="user@example.com")
        self.assertEqual(result, {})

    @patch("zededa_edgeai_sdk.commands.catalogs.execute_catalog_switch")
    def test_client_switch_catalog_success(self, mock_execute):
        """Test ZededaEdgeAIClient.switch_catalog method."""
        mock_execute.return_value = {
            "catalog_id": "production",
            "environment": {"EDGEAI_CURRENT_CATALOG": "production"}
        }
        
        client = ZededaEdgeAIClient(service_url="https://backend")
        
        with patch('builtins.print'):  # Suppress print output in tests
            result = client.switch_catalog("production")
        
        mock_execute.assert_called_once_with(
            "production",
            service_url="https://backend",
            debug=False,
            sdk=client._sdk,
        )
        self.assertEqual(result["catalog_id"], "production")

    @patch("zededa_edgeai_sdk.commands.catalogs.execute_catalog_switch")
    def test_client_switch_catalog_authentication_error(self, mock_execute):
        """Test ZededaEdgeAIClient.switch_catalog with authentication error."""
        from zededa_edgeai_sdk.exceptions import AuthenticationError
        mock_execute.side_effect = AuthenticationError("Not logged in")
        
        client = ZededaEdgeAIClient(service_url="https://backend")
        
        with patch('builtins.print'):  # Suppress print output in tests
            result = client.switch_catalog("production")
        
        self.assertEqual(result, {})

    @patch("zededa_edgeai_sdk.client.ZededaEdgeAIClient")
    def test_module_level_switch_catalog(self, mock_client_class):
        """Test module-level switch_catalog function."""
        from zededa_edgeai_sdk.client import switch_catalog
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.switch_catalog.return_value = {"catalog_id": "test"}
        
        result = switch_catalog("test", service_url="https://custom.com", debug=True)
        
        mock_client_class.assert_called_once_with(service_url="https://custom.com", debug=True)
        mock_client.switch_catalog.assert_called_once_with("test")
        self.assertEqual(result, {"catalog_id": "test"})

    @patch("zededa_edgeai_sdk.commands.catalogs.execute_catalog_list")
    def test_client_list_catalogs_success(self, mock_execute):
        """Test ZededaEdgeAIClient.list_catalogs method."""
        mock_execute.return_value = {
            "available_catalogs": ["dev", "prod"],
            "current_catalog": "dev",
            "total_count": 2
        }
        
        client = ZededaEdgeAIClient(service_url="https://backend")
        result = client.list_catalogs(formatted=False)
        
        mock_execute.assert_called_once_with(
            service_url="https://backend",
            debug=False,
            sdk=client._sdk,
        )
        self.assertEqual(result["available_catalogs"], ["dev", "prod"])

    @patch("zededa_edgeai_sdk.commands.catalogs.execute_catalog_list")
    def test_client_list_catalogs_authentication_error(self, mock_execute):
        """Test ZededaEdgeAIClient.list_catalogs with authentication error."""
        from zededa_edgeai_sdk.exceptions import AuthenticationError
        mock_execute.side_effect = AuthenticationError("Not logged in")
        
        client = ZededaEdgeAIClient(service_url="https://backend")
        
        with patch('builtins.print'):  # Suppress print output in tests
            result = client.list_catalogs(formatted=False)
        
        self.assertEqual(result, {})

    @patch("zededa_edgeai_sdk.client.ZededaEdgeAIClient")
    def test_module_level_list_catalogs(self, mock_client_class):
        """Test module-level list_catalogs function."""
        from zededa_edgeai_sdk.client import list_catalogs
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.list_catalogs.return_value = {"available_catalogs": ["test"]}
        
        result = list_catalogs(service_url="https://custom.com", debug=True, formatted=False)
        
        mock_client_class.assert_called_once_with(service_url="https://custom.com", debug=True)
        mock_client.list_catalogs.assert_called_once_with(formatted=False)
        self.assertEqual(result, {"available_catalogs": ["test"]})

    @patch("zededa_edgeai_sdk.commands.catalogs.execute_catalog_list")
    def test_client_list_catalogs_formatted_output(self, mock_execute):
        """Test ZededaEdgeAIClient.list_catalogs with formatted output."""
        mock_execute.return_value = {
            "available_catalogs": ["demo1", "demo2", "development", "production", "staging"],
            "current_catalog": "demo2",
            "user_info": {
                "user_id": "alice",
                "email": "alice@company.com",
                "name": "Alice Johnson",
                "organization_role": "superadmin"
            },
            "total_count": 5
        }
        
        client = ZededaEdgeAIClient(service_url="https://backend")
        
        # Capture printed output
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = client.list_catalogs(formatted=True)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # Verify the result is None when formatted=True
        self.assertIsNone(result)
        
        # Verify the formatted output contains expected elements
        self.assertIn("Available Catalogs:", output)
        self.assertIn("==================", output)
        self.assertIn("1. demo1", output)
        self.assertIn("2. demo2 (current)", output)
        self.assertIn("3. development", output)
        self.assertIn("4. production", output)
        self.assertIn("5. staging", output)
        self.assertIn("Total: 5 catalogs", output)
        self.assertIn("Current catalog: demo2", output)
        self.assertIn("User: alice@company.com", output)


if __name__ == "__main__":
    unittest.main()
