"""
Service for handling accessory ID lookup using Supabase vector similarity search (RAG).
"""

import logging
import time
from typing import List, Optional

import google.generativeai as genai
from supabase import create_client

from backend.utils import (
    GETAMPEDVIVE_GEMINI_API_KEY,
    GETAMPEDVIVE_GEMINI_EMBEDDING_MODEL,
    GETAMPEDVIVE_GEMINI_MODEL,
    SUPABASE_KEY,
    SUPABASE_URL,
)

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSIONALITY = 768
HIGH_CONFIDENCE_THRESHOLD = 0.9


class AccessoryAgentService:
    """Service for handling accessory ID lookup using Supabase embeddings + RAG."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        embedding_model: str = None,
        supabase_url: str = None,
        supabase_key: str = None,
    ):
        """Initialize the service with API and Supabase configuration.

        Args:
            api_key: Gemini API key. Defaults to env var.
            model: Gemini model name. Defaults to env var.
            embedding_model: Gemini embedding model name. Defaults to env var.
            supabase_url: Supabase project URL. Defaults to env var.
            supabase_key: Supabase API key. Defaults to env var.
        """
        self.api_key = api_key or GETAMPEDVIVE_GEMINI_API_KEY
        self.model_name = model or GETAMPEDVIVE_GEMINI_MODEL
        self.embedding_model_name = (
            embedding_model or GETAMPEDVIVE_GEMINI_EMBEDDING_MODEL
        )

        resolved_supabase_url = supabase_url or SUPABASE_URL
        resolved_supabase_key = supabase_key or SUPABASE_KEY

        if not self.api_key:
            raise ValueError("Gemini API key is required")
        if not resolved_supabase_url or not resolved_supabase_key:
            raise ValueError("Supabase URL and key are required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.supabase = create_client(resolved_supabase_url, resolved_supabase_key)

    def _execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with exponential backoff on rate limits."""
        max_retries = 3
        base_delay = 2
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()
                if (
                    "429" in error_msg
                    or "resource exhausted" in error_msg
                    or "quota" in error_msg
                ):
                    if attempt < max_retries - 1:
                        sleep_time = base_delay * (2**attempt)
                        logger.warning(
                            f"Rate limit hit. Retrying in {sleep_time}s... (Attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(sleep_time)
                        continue
                raise e

    def _find_accessory_id(self, accessory_name: str) -> Optional[str]:
        """Find the best matching accessory ID using embedding similarity search.

        Args:
            accessory_name: The accessory name to search for.

        Returns:
            The accessory ID if a match is found, or None.
        """
        try:
            # 1. Generate embedding for the query
            def _embed():
                return genai.embed_content(
                    model=self.embedding_model_name,
                    content=accessory_name,
                    output_dimensionality=EMBEDDING_DIMENSIONALITY,
                )

            result = self._execute_with_retry(_embed)

            # 2. Search Supabase for similar embeddings
            response = self.supabase.rpc(
                "match_accessory",
                {
                    "query_embedding": result["embedding"],
                    "match_threshold": 0.7,
                    "match_count": 3,
                },
            ).execute()

            if not response.data:
                logger.warning(f"No embedding match found for: {accessory_name}")
                return None

            top_match = response.data[0]

            # 3. High confidence → return directly
            if top_match["similarity"] > HIGH_CONFIDENCE_THRESHOLD:
                logger.debug(
                    f"High confidence match: '{accessory_name}' → "
                    f"'{top_match['accessory_name']}' "
                    f"(similarity={top_match['similarity']:.3f})"
                )
                return top_match["accessory_id"]

            # 4. Ambiguous → let Gemini pick from shortlist
            candidates = [m["accessory_name"] for m in response.data]
            return self._disambiguate_with_gemini(
                accessory_name, candidates, response.data
            )

        except Exception as e:
            logger.error(f"Error finding accessory ID for '{accessory_name}': {e}")
            return None

    def _disambiguate_with_gemini(
        self,
        query: str,
        candidates: List[str],
        match_data: list,
    ) -> Optional[str]:
        """Use Gemini to pick the best match from a shortlist of candidates.

        Args:
            query: The original accessory name query.
            candidates: List of candidate accessory names.
            match_data: Full match data from Supabase (with accessory_id).

        Returns:
            The accessory ID of the best match, or the top candidate's ID as fallback.
        """
        try:
            prompt = (
                f"Given these candidate accessory names: {candidates}\n"
                f'Which one best matches: "{query}"?\n'
                f"Return ONLY the exact matching name from the list, or 'NOT_FOUND'."
            )

            def _generate():
                return self.model.generate_content(prompt)

            response = self._execute_with_retry(_generate)
            matched_name = response.text.strip()

            for m in match_data:
                if m["accessory_name"] == matched_name:
                    logger.debug(f"Gemini disambiguated: '{query}' → '{matched_name}'")
                    return m["accessory_id"]

        except Exception as e:
            logger.warning(f"Gemini disambiguation failed for '{query}': {e}")

        # Fallback to top similarity match
        logger.debug(
            f"Falling back to top match for '{query}': "
            f"'{match_data[0]['accessory_name']}'"
        )
        return match_data[0]["accessory_id"]

    def get_accessory_ids(self, input_text: str) -> str:
        """Get accessory IDs for the given input text.

        Each line should be: PlayerName, Accessory1, Accessory2, ...
        Returns formatted lines: PlayerName,id1,id2,...

        Args:
            input_text: User input text with player and accessories.

        Returns:
            Formatted string with player name and comma-separated accessory IDs.
        """
        try:
            lines = [line.strip() for line in input_text.split("\n") if line.strip()]
            results = []

            # Cache to avoid duplicate API calls for the same accessory
            accessory_cache = {}

            for line in lines:
                parts = [p.strip() for p in line.split(",") if p.strip()]
                if not parts:
                    continue

                player_name = parts[0]
                accessories = parts[1:]

                accessory_ids = []
                for acc in accessories:
                    if acc in accessory_cache:
                        acc_id = accessory_cache[acc]
                    else:
                        acc_id = self._find_accessory_id(acc)
                        accessory_cache[acc] = acc_id

                    if acc_id:
                        accessory_ids.append(acc_id)
                    else:
                        logger.warning(f"Could not find match for accessory: {acc}")
                        accessory_ids.append(acc)

                if accessory_ids:
                    results.append(f"{player_name},{','.join(accessory_ids)}")

            return "\n".join(results) if results else "No valid accessories found"

        except Exception as e:
            logger.error(f"Error processing accessory IDs: {e}")
            return f"Error: {e}"
