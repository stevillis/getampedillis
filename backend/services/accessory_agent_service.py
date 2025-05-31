"""
Service for handling accessory ID generation using AI agent with Gemini.
"""

import logging
from typing import Dict, List, Optional, Tuple

import google.generativeai as genai
import pandas as pd

from backend.utils import (
    ACCS_BY_YEAR_FILE,
    GETAMPEDVIVE_GEMINI_API_KEY,
    GETAMPEDVIVE_GEMINI_MODEL,
)

logger = logging.getLogger(__name__)


class AccessoryAgentService:
    """Service for handling accessory ID generation using Gemini AI."""

    def __init__(self, api_key: str = None, model: str = None):
        """Initialize the service with API configuration.

        Args:
            api_key: Gemini API key. If not provided, will try to get from environment.
            model: Gemini model name. If not provided, will use default from environment.
        """
        self.api_key = api_key or GETAMPEDVIVE_GEMINI_API_KEY
        self.model_name = model or GETAMPEDVIVE_GEMINI_MODEL

        if not self.api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def load_accessories(
        self, file_path: str = None
    ) -> Tuple[Dict[str, str], List[str]]:
        """Load accessories mapping from Excel file.

        Args:
            file_path: Path to the Excel file. If not provided, uses default.

        Returns:
            Tuple containing:
                - Mapping of normalized names to IDs
                - List of original accessory names
        """
        file_path = file_path or ACCS_BY_YEAR_FILE
        try:
            df = pd.read_excel(file_path)
            mapping = {}
            original_names = []

            for _, row in df.iterrows():
                name = str(row["Name"]).strip()
                acc_id = str(row["ID"]).strip()

                original_names.append(name)
                normalized_name = name.lower().replace(" ", "")
                mapping[normalized_name] = acc_id

            # logger.info(f"Loaded {len(mapping)} accessories from {file_path}")
            return mapping, original_names

        except FileNotFoundError:
            logger.error(f"Accessories file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading accessories: {str(e)}")
            raise

    def _generate_gemini_prompt(self, accessory: str, original_names: List[str]) -> str:
        """Generate a prompt for Gemini to find the best matching accessory.

        Args:
            accessory: The accessory name to find a match for
            original_names: List of valid accessory names

        Returns:
            Formatted prompt for Gemini
        """
        return f"""
        Given the following list of valid accessory names:
        {', '.join(original_names[:50])}{'...' if len(original_names) > 50 else ''}

        Find the best matching accessory name for: "{accessory}"

        Return ONLY the matching name exactly as it appears in the list above.
        If no good match is found, return 'NOT_FOUND'.
        """

    def _find_best_match_with_difflib(
        self, query: str, options: List[str], threshold: float = 0.7
    ) -> Optional[str]:
        """Find the best match using difflib's sequence matcher.

        Args:
            query: The search query
            options: List of possible options
            threshold: Minimum similarity ratio (0-1) to consider a match

        Returns:
            Best matching option or None if no good match found
        """
        from difflib import get_close_matches

        # Try to find close matches
        matches = get_close_matches(
            query.lower(), [opt.lower() for opt in options], n=1, cutoff=threshold
        )

        if not matches:
            return None

        # Get the original case version of the best match
        best_match = matches[0]
        for option in options:
            if option.lower() == best_match:
                return option

        return None

    def _find_best_match_with_gemini(
        self, accessory: str, original_names: List[str]
    ) -> Optional[str]:
        """Find the best matching accessory name using Gemini with difflib fallback.

        Args:
            accessory: The accessory name to find a match for
            original_names: List of valid accessory names

        Returns:
            Best matching accessory name or None if not found
        """
        # First try Gemini
        try:
            prompt = self._generate_gemini_prompt(accessory, original_names)
            response = self.model.generate_content(prompt)

            # Extract the response text and clean it up
            matched_name = response.text.strip()

            # Check if the response is one of our valid names
            if matched_name in original_names:
                return matched_name

        except Exception as e:
            logger.warning(f"Error using Gemini for matching: {str(e)}")

        # If Gemini failed or didn't find a match, try difflib
        logger.debug("Gemini didn't find a match, falling back to difflib")
        return self._find_best_match_with_difflib(accessory, original_names)

    def get_accessory_ids(
        self, input_text: str, mapping: Dict[str, str], original_names: List[str]
    ) -> str:
        """Get accessory IDs for the given input text using Gemini for matching.

        Args:
            input_text: User input text with player and accessories
            mapping: Dictionary mapping normalized names to IDs
            original_names: List of original accessory names

        Returns:
            Formatted string with player name and comma-separated accessory IDs
        """
        try:
            # First, split into lines and process each line
            lines = [line.strip() for line in input_text.split("\n") if line.strip()]
            results = []

            for line in lines:
                if not line:
                    continue

                # Split into player and accessories
                parts = [p.strip() for p in line.split(",") if p.strip()]
                if not parts:
                    continue

                player_name = parts[0]
                accessories = parts[1:]

                # Process each accessory
                accessory_ids = []
                for acc in accessories:
                    normalized_acc = acc.lower().replace(" ", "")

                    # First try exact match
                    if normalized_acc in mapping:
                        accessory_ids.append(mapping[normalized_acc])
                        continue

                    # If no exact match, try Gemini for fuzzy matching
                    best_match = self._find_best_match_with_gemini(acc, original_names)
                    if best_match:
                        normalized_match = best_match.lower().replace(" ", "")
                        accessory_ids.append(mapping[normalized_match])
                        # logger.info(f"Matched '{acc}' to '{best_match}' using Gemini")
                    else:
                        logger.warning(f"Could not find match for accessory: {acc}")

                # Format the result line if we found any matches
                if accessory_ids:
                    results.append(f"{player_name},{','.join(accessory_ids)}")

            return "\n".join(results) if results else "No valid accessories found"

        except Exception as e:
            logger.error(f"Error processing accessory IDs: {str(e)}")
            return f"Error: {str(e)}"

    def _find_best_match(self, query: str, options: List[str]) -> Optional[str]:
        """Legacy method for finding best match (kept for backward compatibility).
        Now uses Gemini under the hood for better matching.

        Args:
            query: The search query
            options: List of possible options

        Returns:
            Best matching option or None if no good match found
        """
        return self._find_best_match_with_gemini(query, options)
