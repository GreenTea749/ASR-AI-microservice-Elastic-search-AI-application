#!/usr/bin/env python3
import os, time
import pandas as pd
from elasticsearch import Elasticsearch, helpers

ES_HOST = os.getenv("ES_HOST", "http://es01:9200")
INDEX   = os.getenv("ES_INDEX", "cv-transcriptions")
CSV     = "cv-valid-dev.csv"      # change to your 4 077-row CSV if needed

def create_index(es: Elasticsearch):
    # index properties: exposes .rawy (keyword) sub-field as well
    # allow partial matches for everything
    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "generated_text": {
                    "type": "text",
                    "fields": { "raw": { "type": "keyword" } }
                },
                "duration": { "type": "float" },
                "age":      { "type": "text" },
                "gender":   {
                    "type": "text",               
                    "fields": { "raw": { "type": "keyword" } }
                },
                "accent":   {
                    "type": "text",               
                    "fields": { "raw": { "type": "keyword" } }
                }
            }
        }
    }
    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX, body=mapping)
        print(f"Created index '{INDEX}'")

def load_data():
    df = pd.read_csv(CSV)
    df = df.fillna({
        "generated_text": "",
        "duration": 0,
        "age":      0,
        "gender":   "",
        "accent":   ""
    })
    for _, row in df.iterrows():
        yield {
            "_index": INDEX,
            "_source": {
                "generated_text": row.generated_text,
                "duration": float(row.duration),
                "age":      str(row.age),
                "gender":   str(row.gender),
                "accent":   str(row.accent)
            }
        }

def main():
    es = Elasticsearch(ES_HOST)
    for _ in range(10):
        if es.ping(): break
        print("Waiting for Elasticsearch…"); time.sleep(5)
    else:
        raise RuntimeError("Elasticsearch did not start in time")

    create_index(es)

    print("Bulk indexing…")
    indexed = helpers.bulk(
        es, load_data(),
        chunk_size=500,
        request_timeout=60
    )
    print(f"Indexed {indexed} documents")
    es.indices.refresh(index=INDEX)

if __name__ == "__main__":
    main()
