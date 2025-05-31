"""Tests for the AccessoryAgentService with Gemini integration."""

import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pandas as pd

from backend.services.accessory_agent_service import AccessoryAgentService


class TestAccessoryAgentService(TestCase):
    """Test cases for AccessoryAgentService with Gemini."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = {
            "Name": [
                "Helmet",
                "Armor",
                "Sword",
                "Golden Helmet",
                "Silver Armor",
                "Iron Sword",
            ],
            "ID": [
                "k_ksset3",
                "xmas_sword",
                "dw1_black",
                "armbeam_white",
                "icesaber",
                "beambackpack",
            ],
        }

        # Create a temporary Excel file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, "test_accessories.xlsx")
        pd.DataFrame(self.test_data).to_excel(self.test_file, index=False)

        # Mock the Gemini API key and model
        self.api_key = "test_api_key"
        os.environ["GETAMPEDVIVE_GEMINI_API_KEY"] = self.api_key

        # Patch the Gemini model
        self.mock_model = MagicMock()
        self.mock_generate_content = MagicMock()
        self.mock_model.generate_content = self.mock_generate_content

        # Initialize the service with patched model
        with patch("google.generativeai.GenerativeModel", return_value=self.mock_model):
            self.service = AccessoryAgentService(api_key=self.api_key)

        # Common mock response for Gemini
        self.mock_response = MagicMock()
        self.mock_response.text = "Helmet"  # Default response

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_load_accessories_success(self):
        """Test loading accessories from a valid Excel file."""
        mapping, names = self.service.load_accessories(self.test_file)

        self.assertEqual(len(mapping), 6)
        self.assertEqual(len(names), 6)
        self.assertEqual(mapping["helmet"], "k_ksset3")
        self.assertEqual(mapping["armor"], "xmas_sword")
        self.assertEqual(mapping["sword"], "dw1_black")
        self.assertEqual(mapping["goldenhelmet"], "armbeam_white")
        self.assertEqual(mapping["silverarmor"], "icesaber")
        self.assertEqual(mapping["ironsword"], "beambackpack")
        self.assertIn("Helmet", names)
        self.assertIn("Armor", names)
        self.assertIn("Sword", names)
        self.assertIn("Golden Helmet", names)
        self.assertIn("Silver Armor", names)
        self.assertIn("Iron Sword", names)

    def test_load_accessories_file_not_found(self):
        """Test loading accessories from a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.service.load_accessories("nonexistent_file.xlsx")

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    @patch.dict(os.environ, {}, clear=True)
    @patch("backend.utils.GETAMPEDVIVE_GEMINI_API_KEY", None)
    def test_init_without_api_key(self, mock_model, mock_configure):
        """Test initialization without API key raises ValueError."""
        # Need to re-import the service to get the mocked constant
        import importlib
        import sys

        if "backend.services.accessory_agent_service" in sys.modules:
            module = "backend.services.accessory_agent_service"
            importlib.reload(sys.modules[module])
        from backend.services.accessory_agent_service import AccessoryAgentService

        with self.assertRaises(ValueError):
            AccessoryAgentService(api_key=None)

    @patch.object(AccessoryAgentService, "_find_best_match_with_gemini")
    def test_get_accessory_ids_single_player(self, mock_find_best):
        """Test getting accessory IDs for a single player with Gemini."""
        mapping = {
            "redcape": "k_ksset3",
            "blueshield": "xmas_sword",
            "greensword": "dw1_black",
            "goldencape": "armbeam_white",
        }
        original_names = ["Red Cape", "Blue Shield", "Green Sword", "Golden Cape"]

        # Set up mock to return exact matches for exact matches
        def mock_find(acc, names):
            acc_lower = acc.lower()
            # For exact matches, return the match directly
            if acc_lower in [n.lower() for n in names]:
                return acc

            return None

        mock_find_best.side_effect = mock_find

        # Test exact match - shouldn't call Gemini
        result = self.service.get_accessory_ids(
            "Player1, Red Cape, Blue Shield", mapping, original_names
        )
        self.assertEqual(result, "Player1,k_ksset3,xmas_sword")
        mock_find_best.assert_not_called()
        mock_find_best.reset_mock()

        # Test case insensitivity - shouldn't call Gemini
        result = self.service.get_accessory_ids(
            "Player1, rEd CaPe, BLUE shield", mapping, original_names
        )
        self.assertEqual(result, "Player1,k_ksset3,xmas_sword")
        mock_find_best.assert_not_called()
        mock_find_best.reset_mock()

        # Test with Gemini matching - should call Gemini for non-exact matches
        result = self.service.get_accessory_ids(
            "Player1, red cape, blue shield", mapping, original_names
        )
        # Verify the result contains the expected IDs (k_ksset3 for Red Cape, xmas_sword for Blue Shield)
        self.assertEqual(result, "Player1,k_ksset3,xmas_sword")

    @patch.object(AccessoryAgentService, "_find_best_match_with_gemini")
    def test_get_accessory_ids_multiple_players(self, mock_find_best):
        """Test getting accessory IDs for multiple players with Gemini."""
        mapping = {
            "redcape": "k_ksset3",
            "blueshield": "xmas_sword",
            "greensword": "dw1_black",
            "goldencape": "armbeam_white",
        }
        original_names = ["Red Cape", "Blue Shield", "Green Sword", "Golden Cape"]

        # Setup mock to return exact matches
        def mock_find(acc, names):
            for name in names:
                if acc.lower() == name.lower():
                    return name
            return None

        mock_find_best.side_effect = mock_find

        input_text = "Player1, Red Cape, Blue Shield\nPlayer2, Green Sword, Red Cape"

        result = self.service.get_accessory_ids(input_text, mapping, original_names)

        # Verify the results
        self.assertIn("Player1,k_ksset3,xmas_sword", result)
        self.assertIn("Player2,dw1_black,k_ksset3", result)

        # Verify the mock was called for non-exact matches
        # No calls since we're using exact matches
        self.assertEqual(mock_find_best.call_count, 0)

    @patch.object(AccessoryAgentService, "_find_best_match_with_gemini")
    def test_get_accessory_ids_no_match(self, mock_find_best):
        """Test getting accessory IDs with no matches."""
        mapping = {"redcape": "k_ksset3", "blueshield": "xmas_sword"}
        original_names = ["Red Cape", "Blue Shield"]

        # Mock Gemini to return None for no matches
        mock_find_best.return_value = None

        result = self.service.get_accessory_ids(
            "Player1, NonExistentItem", mapping, original_names
        )
        self.assertEqual(result, "No valid accessories found")
        mock_find_best.assert_called()

    @patch.object(AccessoryAgentService, "_find_best_match_with_gemini")
    def test_find_best_match_calls_gemini(self, mock_find_best):
        """Test that _find_best_match calls Gemini's helper method."""
        options = ["Red Cape", "Blue Shield"]
        mock_find_best.return_value = "Red Cape"

        result = self.service._find_best_match("red cape", options)

        self.assertEqual(result, "Red Cape")
        mock_find_best.assert_called_once_with("red cape", options)

    @patch("google.generativeai.GenerativeModel")
    def test_find_best_match_with_gemini(self, mock_model):
        """Test the Gemini-based best match finder."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.text = "Red Cape"
        mock_model.return_value.generate_content.return_value = mock_response

        # Create service with mocked model
        service = AccessoryAgentService(api_key="test_key")
        service.model = mock_model.return_value

        options = ["Red Cape", "Blue Shield", "Green Sword"]
        result = service._find_best_match_with_gemini("red cape", options)

        self.assertEqual(result, "Red Cape")
        mock_model.return_value.generate_content.assert_called_once()

    @patch("google.generativeai.GenerativeModel")
    def test_find_best_match_with_gemini_not_found(self, mock_model):
        """Test Gemini returns a name not in our options."""
        # Set up mock response with a name not in our options
        mock_response = MagicMock()
        mock_response.text = "Not In Options"
        mock_model.return_value.generate_content.return_value = mock_response

        # Create service with mocked model
        service = AccessoryAgentService(api_key="test_key")
        service.model = mock_model.return_value

        options = ["Red Cape", "Blue Shield"]
        result = service._find_best_match_with_gemini("unknown item", options)

        self.assertIsNone(result)
