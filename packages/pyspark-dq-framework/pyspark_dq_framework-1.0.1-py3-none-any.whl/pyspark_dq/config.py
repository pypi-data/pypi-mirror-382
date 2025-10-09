import yaml
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType

def dq_config(spark: SparkSession, config_path: str):
    """
    Load DQ config from local or remote storage and return a flattened Spark DataFrame
    and the return_mode option.

    Supports:
    - Local filesystem
    - S3 (s3://)
    - Azure Data Lake / ADLS (abfss://)
    - Databricks DBFS (dbfs:/)
    - Google Cloud Storage (gs://)
    """
    # Read config YAML depending on storage type
    if config_path.startswith(("s3://", "dbfs:/", "abfss:/", "gs://")):
        # Read remote YAML via Spark (Shared-cluster-safe: avoid RDD)
        lines_df = spark.read.text(config_path)
        lines = [row["value"] for row in lines_df.collect()]
        yml_str = "\n".join(lines)
        config = yaml.safe_load(yml_str)
    else:
        # Local file read
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

    # Extract return_mode safely (default = "summary")
    return_mode = config.get("return_mode", "summary")

    # Flatten model section into list of Rows
    schema = StructType([
                StructField("table", StringType(), True),
                StructField("column", StringType(), True),
                StructField("check", StringType(), True),
                StructField("params", StringType(), True)
            ])
    rules = []
    for table in config.get("model", []):
        table_name = table["name"]
        for col in table.get("columns", []):
            column_name = col["name"]
            for check in col.get("checks", []):
                if isinstance(check, dict):
                    # Check with parameters
                    check_name, params = list(check.items())[0]
                    rules.append(Row(table=table_name, column=column_name, check=check_name, params=json.dumps(params)))
                else:
                    # Simple check without parameters
                    rules.append(Row(table=table_name, column=column_name, check=check, params=None))

    # Convert to Spark DataFrame
    dq_config_df = spark.createDataFrame(rules, schema=schema)

    return dq_config_df, return_mode
