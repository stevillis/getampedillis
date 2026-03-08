import os
import time

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

INITIAL_WAIT = 5
MAX_WAIT = 100


def get_existing_accessory_ids(supabase):
    """Fetch all accessory_ids already embedded in Supabase."""
    existing = set()
    response = supabase.table("accessory_embeddings").select("accessory_id").execute()
    for row in response.data:
        existing.add(row["accessory_id"])
    return existing


def embed_with_retry(model, name, max_retries=10):
    """Generate embedding with automatic retry on rate limit errors."""
    wait_time = INITIAL_WAIT
    for attempt in range(max_retries):
        try:
            result = genai.embed_content(
                model=model,
                content=name,
                output_dimensionality=768,
            )
            return result["embedding"]
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                print(
                    f"  Rate limited. Waiting {wait_time}s "
                    f"(attempt {attempt + 1}/{max_retries})..."
                )
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, MAX_WAIT)
            else:
                raise
    raise RuntimeError(f"Failed to embed '{name}' after {max_retries} retries")


if __name__ == "__main__":
    load_dotenv()

    GETAMPEDVIVE_GEMINI_API_KEY = os.environ.get("GETAMPEDVIVE_GEMINI_API_KEY")
    GETAMPEDVIVE_GEMINI_EMBEDDING_MODEL = os.environ.get(
        "GETAMPEDVIVE_GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"
    )
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GETAMPEDVIVE_GEMINI_API_KEY)

    # Load already-embedded IDs to skip them
    existing_ids = get_existing_accessory_ids(supabase)
    print(f"Found {len(existing_ids)} already embedded. Skipping those.")

    df = pd.read_excel("data/accs_by_year.xlsx")
    total = len(df)
    embedded_count = 0
    skipped_count = 0

    for idx, row in df.iterrows():
        name = str(row["Name"]).strip()
        acc_id = str(row["ID"]).strip()

        if acc_id in existing_ids:
            skipped_count += 1
            continue

        embedding = embed_with_retry(GETAMPEDVIVE_GEMINI_EMBEDDING_MODEL, name)

        supabase.table("accessory_embeddings").insert(
            {
                "accessory_id": acc_id,
                "accessory_name": name,
                "embedding": embedding,
            }
        ).execute()

        embedded_count += 1
        print(
            f"[{skipped_count + embedded_count}/{total}] "
            f"Embedded: {name} (ID: {acc_id})"
        )

    print(
        f"\nDone! Embedded {embedded_count} new items, "
        f"skipped {skipped_count} existing."
    )
