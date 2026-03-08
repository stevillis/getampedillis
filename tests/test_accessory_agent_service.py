"""Tests for the AccessoryAgentService with Supabase embeddings + RAG."""

import os
from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestAccessoryAgentService(TestCase):
    """Test cases for AccessoryAgentService with Supabase + Gemini."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        os.environ["GETAMPEDVIVE_GEMINI_API_KEY"] = self.api_key

        self.mock_model = MagicMock()
        self.mock_supabase = MagicMock()

        with (
            patch(
                "google.generativeai.GenerativeModel",
                return_value=self.mock_model,
            ),
            patch(
                "backend.services.accessory_agent_service.create_client",
                return_value=self.mock_supabase,
            ),
        ):
            from backend.services.accessory_agent_service import AccessoryAgentService

            self.service = AccessoryAgentService(
                api_key=self.api_key,
                supabase_url="https://test.supabase.co",
                supabase_key="test_supabase_key",
            )

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    @patch.dict(os.environ, {}, clear=True)
    @patch("backend.utils.GETAMPEDVIVE_GEMINI_API_KEY", None)
    def test_init_without_api_key(self, mock_model, mock_configure):
        """Test initialization without API key raises ValueError."""
        import importlib
        import sys

        if "backend.services.accessory_agent_service" in sys.modules:
            module = "backend.services.accessory_agent_service"
            importlib.reload(sys.modules[module])
        from backend.services.accessory_agent_service import AccessoryAgentService

        with self.assertRaises(ValueError):
            AccessoryAgentService(
                api_key=None,
                supabase_url="https://test.supabase.co",
                supabase_key="test_key",
            )

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_init_without_supabase(self, mock_model, mock_configure):
        """Test initialization without Supabase credentials raises ValueError."""
        from backend.services.accessory_agent_service import AccessoryAgentService

        with (
            patch("backend.services.accessory_agent_service.SUPABASE_URL", None),
            patch("backend.services.accessory_agent_service.SUPABASE_KEY", None),
            self.assertRaises(ValueError),
        ):
            AccessoryAgentService(
                api_key="test_key",
                supabase_url=None,
                supabase_key=None,
            )

    @patch("google.generativeai.embed_content")
    def test_find_accessory_id_high_confidence(self, mock_embed):
        """Test that high confidence matches are returned directly."""
        mock_embed.return_value = {"embedding": [0.1] * 768}

        mock_rpc_response = MagicMock()
        mock_rpc_response.data = [
            {
                "accessory_id": "k_ksset3",
                "accessory_name": "Long Boots",
                "similarity": 0.95,
            }
        ]
        self.mock_supabase.rpc.return_value.execute.return_value = mock_rpc_response

        result = self.service._find_accessory_id("Long Boots")

        self.assertEqual(result, "k_ksset3")
        # Gemini generate_content should NOT be called for high confidence
        self.mock_model.generate_content.assert_not_called()

    @patch("google.generativeai.embed_content")
    def test_find_accessory_id_ambiguous_uses_gemini(self, mock_embed):
        """Test that ambiguous matches delegate to Gemini for disambiguation."""
        mock_embed.return_value = {"embedding": [0.1] * 768}

        mock_rpc_response = MagicMock()
        mock_rpc_response.data = [
            {
                "accessory_id": "id_boots_long",
                "accessory_name": "Long Boots",
                "similarity": 0.85,
            },
            {
                "accessory_id": "id_boots_short",
                "accessory_name": "Short Boots",
                "similarity": 0.82,
            },
        ]
        self.mock_supabase.rpc.return_value.execute.return_value = mock_rpc_response

        # Gemini picks the correct one
        mock_response = MagicMock()
        mock_response.text = "Long Boots"
        self.mock_model.generate_content.return_value = mock_response

        result = self.service._find_accessory_id("Lng Boots")

        self.assertEqual(result, "id_boots_long")
        self.mock_model.generate_content.assert_called_once()

    @patch("google.generativeai.embed_content")
    def test_find_accessory_id_no_match(self, mock_embed):
        """Test that no match returns None."""
        mock_embed.return_value = {"embedding": [0.1] * 768}

        mock_rpc_response = MagicMock()
        mock_rpc_response.data = []
        self.mock_supabase.rpc.return_value.execute.return_value = mock_rpc_response

        result = self.service._find_accessory_id("Completely Unknown Item")

        self.assertIsNone(result)

    @patch("google.generativeai.embed_content")
    def test_find_accessory_id_gemini_fallback_to_top(self, mock_embed):
        """Test that when Gemini can't pick, fallback to top similarity match."""
        mock_embed.return_value = {"embedding": [0.1] * 768}

        mock_rpc_response = MagicMock()
        mock_rpc_response.data = [
            {
                "accessory_id": "id_cape_red",
                "accessory_name": "Red Cape",
                "similarity": 0.88,
            },
            {
                "accessory_id": "id_cape_blue",
                "accessory_name": "Blue Cape",
                "similarity": 0.85,
            },
        ]
        self.mock_supabase.rpc.return_value.execute.return_value = mock_rpc_response

        # Gemini returns something not in our list
        mock_response = MagicMock()
        mock_response.text = "NOT_FOUND"
        self.mock_model.generate_content.return_value = mock_response

        result = self.service._find_accessory_id("Crimson Cape")

        # Should fallback to top match
        self.assertEqual(result, "id_cape_red")

    @patch.object(
        __import__(
            "backend.services.accessory_agent_service",
            fromlist=["AccessoryAgentService"],
        ).AccessoryAgentService,
        "_find_accessory_id",
    )
    def test_get_accessory_ids_single_player(self, mock_find):
        """Test getting accessory IDs for a single player."""
        mock_find.side_effect = lambda name: {
            "Red Cape": "k_ksset3",
            "Blue Shield": "xmas_sword",
        }.get(name)

        result = self.service.get_accessory_ids("Player1, Red Cape, Blue Shield")

        self.assertEqual(result, "Player1,k_ksset3,xmas_sword")

    @patch.object(
        __import__(
            "backend.services.accessory_agent_service",
            fromlist=["AccessoryAgentService"],
        ).AccessoryAgentService,
        "_find_accessory_id",
    )
    def test_get_accessory_ids_multiple_players(self, mock_find):
        """Test getting accessory IDs for multiple players."""
        mock_find.side_effect = lambda name: {
            "Red Cape": "k_ksset3",
            "Blue Shield": "xmas_sword",
            "Green Sword": "dw1_black",
        }.get(name)

        input_text = "Player1, Red Cape, Blue Shield\nPlayer2, Green Sword, Red Cape"
        result = self.service.get_accessory_ids(input_text)

        self.assertIn("Player1,k_ksset3,xmas_sword", result)
        self.assertIn("Player2,dw1_black,k_ksset3", result)

    @patch.object(
        __import__(
            "backend.services.accessory_agent_service",
            fromlist=["AccessoryAgentService"],
        ).AccessoryAgentService,
        "_find_accessory_id",
    )
    def test_get_accessory_ids_no_match(self, mock_find):
        """Test getting accessory IDs with no matches keeps original names."""
        mock_find.return_value = None

        result = self.service.get_accessory_ids("Player1, NonExistentItem")

        self.assertEqual(result, "Player1,NonExistentItem")

    @patch("google.generativeai.embed_content")
    def test_find_accessory_id_exception_returns_none(self, mock_embed):
        """Test that exceptions in _find_accessory_id are caught and return None."""
        mock_embed.side_effect = RuntimeError("Embedding API down")

        result = self.service._find_accessory_id("Some Accessory")

        self.assertIsNone(result)

    @patch("google.generativeai.embed_content")
    def test_disambiguate_with_gemini_exception_falls_back(self, mock_embed):
        """Test that Gemini exception in disambiguation falls back to top match."""
        mock_embed.return_value = {"embedding": [0.1] * 768}

        mock_rpc_response = MagicMock()
        mock_rpc_response.data = [
            {
                "accessory_id": "id_top",
                "accessory_name": "Top Match",
                "similarity": 0.85,
            },
            {
                "accessory_id": "id_second",
                "accessory_name": "Second Match",
                "similarity": 0.80,
            },
        ]
        self.mock_supabase.rpc.return_value.execute.return_value = mock_rpc_response

        # Gemini raises an exception
        self.mock_model.generate_content.side_effect = RuntimeError("Gemini down")

        result = self.service._find_accessory_id("Some Query")

        # Should fallback to top similarity match
        self.assertEqual(result, "id_top")

    @patch.object(
        __import__(
            "backend.services.accessory_agent_service",
            fromlist=["AccessoryAgentService"],
        ).AccessoryAgentService,
        "_find_accessory_id",
    )
    def test_get_accessory_ids_skips_empty_parts(self, mock_find):
        """Test that lines producing empty parts are skipped."""
        mock_find.side_effect = lambda name: {"Sword": "id_sword"}.get(name)

        # The ",,,," line produces parts=[] after stripping blanks
        input_text = ",,,,\nPlayer1, Sword"
        result = self.service.get_accessory_ids(input_text)

        self.assertEqual(result, "Player1,id_sword")

    @patch.object(
        __import__(
            "backend.services.accessory_agent_service",
            fromlist=["AccessoryAgentService"],
        ).AccessoryAgentService,
        "_find_accessory_id",
    )
    def test_get_accessory_ids_exception_returns_error(self, mock_find):
        """Test that unexpected exceptions in get_accessory_ids return error string."""
        mock_find.side_effect = RuntimeError("Unexpected error")

        result = self.service.get_accessory_ids("Player1, SomeItem")

        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Unexpected error", result)
