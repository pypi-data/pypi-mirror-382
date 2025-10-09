# 🛡️ PySpark Data Quality Framework (pyspark_dq_framework)

This framework provides a **config-driven, extensible Data Quality (DQ) framework** built on top of **PySpark**.  
It allows defining validation checks in a `config.yml` file and running them on one or more DataFrames.

---

## 📁 Project Structure
```
pyspark_dq_framework/
├── pyspark_dq/                   # your Python package
│   ├── __init__.py
│   ├── dq_checks.py              # Core data quality functions
│   ├── config.py                 # YAML parser to config DataFrame
│   ├── run_dq.py                 # Engine to run checks with logging
│   └── validate_checks.py        # Check validation
├── README.md
├── LICENSE
├── MANIFEST.in
├── setup.py
```
---

## ⚙️ Configuration (config.yml)

```
return_mode: summary   # options: summary (default) | summary+clean | summary+error | all

model:
  - name: df
    columns:
      - name: ID
        checks:
          - null_check
      - name: Age
        checks:
          - null_check
          - positive_age_check:
              min_age: 21

  - name: df2
    columns:
      - name: ID
        checks:
          - null_check
      - name: Salary
        checks:
          - non_negative_check
```

---

## 🛠️ Code Example for Executing framework

### If config file is in : 
- local: pass file path in config_path parameter
- S3: pass s3 path
- Azure Blob Storage or (ADLS Gen2 for data lake): pass blob storage path
- Google Cloud Storage (GCS): pass GCS path

### Code Example:
```
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark_dq.run_dq import run_dq_pipeline
from pyspark_dq.dq_checks import *

# Custom check
def positive_age_check(df, row, min_age=0):
    table = row["table"]
    column = row["column"]
    check_type = "positive_age_check"

    valid_df = df.filter(col(column) >= min_age)
    invalid_df = df.filter(col(column) < min_age) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))

    log_df = df.sparkSession.createDataFrame(
        [(table, column, check_type, invalid_df.count() == 0, invalid_df.count())],
        ["table", "column", "check_type", "passed", "invalid_count"]
    )
    return valid_df, invalid_df, log_df

if __name__ == "__main__":
    
    spark = SparkSession.builder.appName("pyspark_dq_framework").getOrCreate()

    # Example Data
    data1 = [(1, "Ram", 20), (None, "Shyam", 20)]
    df = spark.createDataFrame(data1, ["ID", "Name", "Age"])

    data2 = [
        (1, "Ram", "Software Engineer", 20000),
        (2, "Shyam", "Product Manager", 80000),
        (3, "Radha", "Senior Software Engineer", 50000)
    ]
    df2 = spark.createDataFrame(data2, ["ID", "Name", "Designation", "Salary"])

    df_dict = {"df": df, "df2": df2}

    # Register checks
    check_function_map = {
        "null_check": null_check,
        "unique_check": unique_check,
        "allowed_values_check": allowed_values_check,
        "range_check": range_check,
        "non_negative_check": non_negative_check,
        "regex_check": regex_check,
        "not_empty_check": not_empty_check,
        "data_type_check": data_type_check,
        "positive_age_check": positive_age_check
    }

    # Run pipeline
    results = run_dq_pipeline(
        spark,
        df_dict=df_dict,
        config_path="config.yml",
        checks=check_function_map
    )

    print(results)
```

---

## 🔄 Return Modes

The `return_mode` in `config.yml` controls what is returned:

- summary → Only summary logs  
- summary+clean → Summary + cleaned DataFrames  
- summary+error → Summary + error DataFrames  
- all → Summary + clean + error DataFrames  

---

## ⚙️ Prerequisites

Before installing and using the `pyspark-dq-framework` package, ensure the following Python modules are available:

| Module | Version | Description |
|--------|---------|-------------|
| `pyspark` | `>=3.5.5` | Required for all Spark DataFrame operations. If running on Databricks, EMR, or other managed Spark clusters, PySpark is usually pre-installed. |
| `pyyaml` | `>=6.0.2` | Required to read YAML configuration files for defining dynamic data quality checks. |

> 💡 **Tip:** PySpark can be installed optionally with the package using:
>
> ```bash
> pip install pyspark-dq-framework[pyspark]
> ```
>
> If you already have PySpark installed on your cluster, you can just install:
>
> ```bash
> pip install pyspark-dq-framework
> ```

---

## ▶️ How to Run

### 📦 Install PyPi package in your environment
```
pip install pyspark-dq-framework
```

### 📚 Import required libraries
```
from pyspark.sql import SparkSession
from pyspark_dq.dq_checks import *
from pyspark_dq.run_dq import run_dq_pipeline
```

### ⚡ `run_dq_pipeline` Function

Runs the Data Quality (DQ) pipeline on one or more Spark DataFrames according to a YAML configuration and user-defined checks.

#### 📝 Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `spark` | `SparkSession` | The active Spark session to execute the DQ pipeline. All Spark DataFrame operations will be performed using this session. |
| `df_dict` | `Dict[str, DataFrame]` | A dictionary of input DataFrames to validate. Keys are table names (strings), and values are the corresponding Spark DataFrames. The pipeline will process each DataFrame according to its configuration. |
| `config_path` | `str` | Path to the YAML configuration file that defines the DQ checks for each table and column. This configuration specifies which checks to run, expected types, regex patterns, or other rules. |
| `checks` | `Dict[str, callable]`, optional | A dictionary mapping check names (strings) to Python functions. Each function implements a DQ check, takes a DataFrame and a configuration row, and returns `(valid_df, invalid_df, log_df)`. This allows adding custom checks dynamically. |
| `max_json_records` | `int`, optional, default=100 | Maximum number of failing rows per check to include in the summary JSON column. If set to `None`, all failed rows will be captured. This is useful for controlling summary size while maintaining accurate failed counts. |

### 🎯 Returns

A dictionary with the following structure:

```python
{
    "table_name": {
        "clean": DataFrame,  # final cleaned DataFrame after all checks
        "error": DataFrame   # combined invalid rows across all checks with __failed_check and __failed_column log columns (optional, depending on return mode)
    },
    "summary": DataFrame     # summary table with failed counts and JSON of failed rows
}
```

### 🚀 Example Usage
```
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Dictionary of input DataFrames
df_dict = {
    "sales": sales_df,
    "customers": customers_df
}

# Dictionary of custom DQ check functions
checks = {
    "not_empty_check": not_empty_check,
    "data_type_check": data_type_check
}

results = run_dq_pipeline(
    spark,
    df_dict=df_dict,
    config_path="config.yaml",
    checks=checks,
    max_json_records=100
)

summary_df = results["summary"]
clean_sales_df = results["sales"]["clean"]
error_sales_df = results["sales"]["error"]

clean_customers_df = results["customers"]["clean"]
error_customers_df = results["customers"]["error"]
```

---

### 💻 Add sample code without custom check (here I am taking file name as main.py)
#### /main.py
```
from pyspark.sql import SparkSession
from pyspark_dq.run_dq import run_dq_pipeline
from pyspark_dq.dq_checks import null_check, unique_check
    
spark = SparkSession.builder.appName("pyspark_dq_framework").getOrCreate()

# Example Data
# Dataframe 1
data1 = [
          (1, "Ram", 20),
          (None, "Shyam", 20)
        ]
df1 = spark.createDataFrame(data1, ["ID", "Name", "Age"])

# Datframe 2
data2 = [
          (1, "Ram", "Software Engineer", 20000),
          (2, "Shyam", "Product Manager", 80000),
          (3, "Radha", "Senior Software Engineer", 50000)
        ]
df2 = spark.createDataFrame(data2, ["ID", "Name", "Designation", "Salary"])

# Dataframes Dictionary
df_dict = {"df1": df1, "df2": df2}

# Register checks
check_function_map = {
        "null_check": null_check,
        "unique_check": unique_check
    }

# Run pipeline
results = run_dq_pipeline(
            spark,
            df_dict=df_dict,
            config_path="config.yml",
            checks=check_function_map
          )

print(results)
```

---

### ⚡ Add sample code with custom check (here I am taking file name as main.py)
#### /main.py
```
from pyspark.sql import SparkSession
from pyspark_dq.run_dq import run_dq_pipeline
from pyspark_dq.dq_checks import null_check, unique_check


# Custom check
def positive_age_check(df, row, min_age=0):
    table = row["table"]
    column = row["column"]
    check_type = "positive_age_check"

    valid_df = df.filter(col(column) >= min_age)
    invalid_df = df.filter(col(column) < min_age) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))

    log_df = df.sparkSession.createDataFrame(
        [(table, column, check_type, invalid_df.count() == 0, invalid_df.count())],
        ["table", "column", "check_type", "passed", "invalid_count"]
    )
    return valid_df, invalid_df, log_df

# Inititalize spark session 
spark = SparkSession.builder.appName("pyspark_dq_framework").getOrCreate()

# Example Data
# Dataframe 1
data1 = [
          (1, "Ram", 20),
          (None, "Shyam", 20)
        ]
df1 = spark.createDataFrame(data1, ["ID", "Name", "Age"])

# Datframe 2
data2 = [
          (1, "Ram", "Software Engineer", 20000),
          (2, "Shyam", "Product Manager", 80000),
          (3, "Radha", "Senior Software Engineer", 50000)
        ]
df2 = spark.createDataFrame(data2, ["ID", "Name", "Designation", "Salary"])

# Dataframes Dictionary
df_dict = {"df1": df1, "df2": df2}

# Register checks
check_function_map = {
        "null_check": null_check,
        "unique_check": unique_check,
        "positive_age_check": positive_age_check
    }

# Run pipeline
results = run_dq_pipeline(
            spark,
            df_dict=df_dict,
            config_path="config.yml",
            checks=check_function_map
          )

print(results)
```

## 📝 General Config YAML Structure
#### /config.yml
```
return_mode: <return mode>   # options: summary (default) | summary+clean | summary+error | all

model:
  - name: <dataframe_name>
    columns:
      - name: <column_name>
        checks:
          - <check_name>
          - <check_name_with_params>:
              param1: value
              param2: value
```
---

## 💻 Run locally
```
python main.py
```

## 📊 Run in Databricks
```
dbutils.notebook.run("main", 60)
```

## ☁️ Run with S3 config
```
python main.py --config s3://my-bucket/config.yml
```
---

## ✅ Features

- Config-driven DQ checks  
- Works with local, S3, GCP, Azure, DBFS  
- Extensible with custom checks  
- Flexible return_mode for different use cases  

## 📋 Supported Data Quality Checks

- null_check
- unique_check
- allowed_values_check
- range_check
- non_negative_check
- regex_check
- not_empty_check
- data_type_check

---

| Check Name             | Description                               | Parameters                          |
| ---------------------- | ----------------------------------------- | ----------------------------------- |
| `null_check`           | Ensures no null values.                   | None                                |
| `unique_check`         | Ensures uniqueness of values.             | None                                |
| `allowed_values_check` | Ensures value is in allowed set.          | `allowed_values: [list_of_values]`          |
| `range_check`          | Ensures value is within numeric range.    | `min_value`, `max_value` (optional) |
| `non_negative_check`   | Ensures value >= 0.                       | None                                |
| `regex_check`          | Ensures value matches regex pattern.      | `pattern: "<regex>"`                |
| `not_empty_check`      | Ensures dataset/column is not empty.      | None                                |
| `data_type_check`      | Ensures value matches expected data type. | `expected_type`                     |
| `positive_age_check`   | Ensures age is >= min_age.                | `min_age`                           |

---

## 📑 YAML Usage Examples for Each Check

| Check Name             | YAML Example                                                                 |
| ---------------------- | ---------------------------------------------------------------------------- |
| `null_check`           | `- null_check`                                                               |
| `unique_check`         | `- unique_check`                                                             |
| `allowed_values_check` | `- allowed_values_check:\n    allowed_values: [Male, Female, Other]`                 |
| `range_check`          | `- range_check:\n    min_value: 10\n    max_value: 100`                      |
| `non_negative_check`   | `- non_negative_check`                                                       |
| `regex_check`          | `- regex_check:\n    pattern: "^[A-Za-z0-9_]+$"`                             |
| `not_empty_check`      | `- not_empty_check`                                                          |
| `data_type_check`      | `- data_type_check:\n    expected_type: IntegerType`                             |
| `positive_age_check`   | `- positive_age_check:\n    min_age: 21`                                     |

---

## 📑 Explaination of each check with proper YAML format for config.yml file

### null_check
- Ensures that the column does not contain NULL values.
- Records with NULL values will go into the invalid dataset.
```
model:
  - name: df
    columns:
      - name: ID
        checks:
          - null_check
```

### unique_check
- Ensures that the column contains unique values.
- Duplicates will be flagged as invalid.
```
model:
  - name: df
    columns:
      - name: ID
        checks:
          - unique_check
```

### allowed_values_check
- Ensures that the column values belong to a defined set of allowed values.
- Invalid values are flagged.
#### Parameters
- allowed_values → list of allowed values.
```
model:
  - name: df
    columns:
      - name: Status
        checks:
          - allowed_values_check:
              allowed_values: ["Active", "Inactive", "Pending"]
```

### range_check
- Ensures that the column values fall within a numeric range.
#### Parameters
- min_value → minimum acceptable value (optional).
- max_value → maximum acceptable value (optional).
```
model:
  - name: df
    columns:
      - name: Age
        checks:
          - range_check:
              min_value: 18
              max_value: 60
```

### non_negative_check
- Ensures that the column values are greater than or equal to 0.
```
model:
  - name: df
    columns:
      - name: Salary
        checks:
          - non_negative_check
```

### regex_check
- Ensures that the column values match a given regex pattern.
- Useful for emails, phone numbers, codes, etc.
#### Parameters
- pattern → valid regex pattern.
```
model:
  - name: df
    columns:
      - name: Email
        checks:
          - regex_check:
              pattern: "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$"
```

### not_empty_check
- Ensures that the column (or dataset) is not empty.
- If no records exist, the check fails.
```
model:
  - name: df
    columns:
      - name: ID
        checks:
          - not_empty_check
```

### data_type_check
- Ensures that the column matches the expected data type.
- You need to provide the expected type in parameters
#### Parameters
- expected_type → e.g., IntegerType, StringType, DoubleType.
```
model:
  - name: df
    columns:
      - name: Age
        checks:
          - data_type_check:
              expected_type: IntegerType
```

