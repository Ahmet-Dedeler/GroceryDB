import os
import json
import pandas as pd
from tqdm import tqdm
import query_builder


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def main() -> None:
    DB = query_builder.get_mongo_databases(verbose=True)

    bad = query_builder.bad_categories_more_strict
    cleaned = DB['GroceryDB']['CleanedData']

    projection = {
        "_id": 0,
        "original_ID": 1,
        "name": 1,
        "store": 1,
        "brand": 1,
        "url": 1,
        "harmonized single category": 1,
        "12P FPro": 1,
        "12P class": 1,
        "isConverted": 1,
        "has10P": 1,
        # price fields may not be present for all items; include if available
        "price": 1,
        "price percal": 1,
    }

    # Baseline filter (like their example notebook): exclude bad categories
    query_baseline = {
        "harmonized single category": {"$nin": bad},
    }

    # Stricter UI-like filter: require nutrient completeness and price info
    query_ui_like = {
        "harmonized single category": {"$nin": bad},
        "isConverted": 1,
        "has10P": 1,
        "price": {"$ne": None},
        "price percal": {"$ne": None},
    }

    print("Running baseline query (exclude bad categories)...")
    docs_baseline = list(cleaned.find(query_baseline, projection))
    df_baseline = pd.DataFrame(docs_baseline)
    print(f"Baseline count: {len(df_baseline)}")

    print("Running UI-like query (exclude bad categories + require nutrition + price fields)...")
    docs_ui_like = list(cleaned.find(query_ui_like, projection))
    df_ui_like = pd.DataFrame(docs_ui_like)
    print(f"UI-like count: {len(df_ui_like)}")

    out_dir = os.path.join(os.path.dirname(__file__), "output")
    ensure_output_dir(out_dir)

    path_baseline = os.path.join(out_dir, "gdb_cleaned_baseline.csv")
    path_ui_like = os.path.join(out_dir, "gdb_cleaned_ui_like.csv")

    df_baseline.to_csv(path_baseline, index=False)
    df_ui_like.to_csv(path_ui_like, index=False)

    print("Saved:")
    print(" -", path_baseline)
    print(" -", path_ui_like)


if __name__ == "__main__":
    main()