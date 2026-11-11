# 1. Extract data from one source, for example CSV, JSON, Parquet, Excel, or an API.
# 2. Transform the data by selecting the required columns and applying at least two changes,
# such as: handling missing values, changing data types, renaming columns, filtering rows,
# creating a new column.
# 3. Load the processed DataFrame into a database table using SQLAlchemy.
# 4. Read the created table from the database and display several rows to check that the data
# was saved correctly.

from re import compile

import pandas as pd
from sqlalchemy import create_engine, Engine


def extract() -> pd.DataFrame:
    return pd.read_csv("./products.csv")

def transform(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.isna().sum().sum():
        # raw.dropna(inplace=True)
        ...

    raw.drop_duplicates(inplace=True)
    
    raw["product_id"] = raw["product_id"].astype("int64")
    raw["unit_price"] = raw["unit_price"].astype("float64")
    raw["unit_cost"] = raw["unit_cost"].astype("float64")
    raw["weight_kg"] = raw["weight_kg"].astype("float64")

    raw["is_active"] = raw["is_active"].astype("bool")

    raw["created_at"] = pd.to_datetime(raw["created_at"], errors="coerce")

    def get_color(product_name_raw: str) -> str | None:
        color_pattern = compile(r"(\(.*\))")
        color_match = color_pattern.search(product_name_raw)

        if color_match:
            return color_match.group(1).strip("()")
        return None

    raw["color"] = raw["product_name"].apply(get_color).astype("str")

    clean = raw.copy()
    return clean

def load(clean: pd.DataFrame, engine: Engine) -> bool:
    if clean.to_sql("products_clean", engine, if_exists="replace", index=False):
        return True
    return False

def read(engine: Engine) -> None:
    products_clean = pd.read_sql("products_clean", engine)
    print(products_clean.head())
    print(products_clean.dtypes)
    
def main():
    engine = create_engine("sqlite:///ecommerce.sqlite")
    raw = extract()
    clean = transform(raw)
    load(clean, engine)
    read(engine)


if __name__ == "__main__":
    main()