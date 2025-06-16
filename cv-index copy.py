#!/usr/bin/env python3
"""
Index the Common Voice dev CSV into Elasticsearch (Docker-Compose edition).
"""

import time
import pandas as pd
from elasticsearch import Elasticsearch, helpers, exceptions

ES_HOST = "http://es01:9200"          # Service name inside Docker network
INDEX   = "cv-transcriptions"
CSV     = "cv-valid-dev.csv"

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def create_index(es: Elasticsearch) -> None:
    """Create the target index with a simple mapping (if it doesn’t exist)."""
    mapping = {
        "mappings": {
            "properties": {
                "generated_text": {"type": "text"},
                "duration":       {"type": "float"},
                "age":            {"type": "integer"},
                "gender":         {"type": "keyword"},
                "accent":         {"type": "keyword"},
            }
        }
    }
    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX, body=mapping)
        print(f"✅ Created index “{INDEX}”")
    else:
        print(f"ℹ️  Index “{INDEX}” already exists")

def load_data():
    """Yield docs from the CSV for helpers.bulk()."""
    df = pd.read_csv(CSV)
    df = df.fillna(
        {
            "generated_text": "",
            "duration": 0,
            "age": 0,
            "gender": "",
            "accent": "",
        }
    )
    for _, row in df.iterrows():
        yield {
            "_index": INDEX,
            "_source": {
                "generated_text": row["generated_text"],
                "duration":       float(row["duration"]),
                "age":            int(row["age"]),
                "gender":         str(row["gender"]),
                "accent":         str(row["accent"]),
            },
        }

def wait_for_cluster(es: Elasticsearch,
                     status: str = "yellow",
                     timeout: int = 60) -> None:
    """
    Block until the cluster reaches the given health status
    (default: at least YELLOW). Raises if the timeout is exceeded.
    """
    print(f"🔄 Waiting for cluster health = “{status}”…")
    es.cluster.health(wait_for_status=status, request_timeout=timeout)
    print("🚦 Cluster ready.")

# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #

def main() -> None:
    print("🚀 Starting indexer script")

    es = Elasticsearch(
        ES_HOST,
        # Give the server longer than the default 10 s to answer big requests
        request_timeout=30,

        max_retries=5,            # retry on time-out or 5xx automatically
        retry_on_timeout=True,
    )

    # 1. Wait for the HTTP endpoint itself to answer
    for attempt in range(5):
        try:
            if es.ping():
                print("✅ Elasticsearch node responds to ping")
                break
        except exceptions.ConnectionError as err:
            print(f"⏳ Retry {attempt + 1}: not reachable yet – {err}")
        time.sleep(5)
    else:
        raise RuntimeError("❌ Elasticsearch did not start in time")

    # 2. Wait for the cluster to finish recovery/elect master
    wait_for_cluster(es, status="yellow", timeout=60)

    # 3. Create index (idempotent) and bulk-index the CSV
    create_index(es)
    helpers.bulk(es, load_data())
    print("🎉 Finished indexing")

if __name__ == "__main__":
    main()
