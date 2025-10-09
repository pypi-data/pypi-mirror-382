from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, row_number
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType

# Common schema for (optional) logs; we won't compute counts here
error_schema = StructType([
    StructField("table", StringType()),
    StructField("column", StringType()),
    StructField("check_type", StringType()),
    StructField("passed", BooleanType()),
    StructField("invalid_count", IntegerType())
])

def _empty_log(df, table, column, check_type):
    # No counts here to avoid triggering actions
    return df.sparkSession.createDataFrame(
        [(table, column, check_type, None, None)],
        schema=error_schema
    )

def null_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "null_check"
    valid_df = df.filter(col(column).isNotNull())
    invalid_df = df.filter(col(column).isNull()) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def unique_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "unique_check"
    window_spec = Window.partitionBy(column).orderBy(column)
    df_with_rn = df.withColumn("row_num", row_number().over(window_spec))
    valid_df = df_with_rn.filter(col("row_num") == 1).drop("row_num")
    invalid_df = df_with_rn.filter(col("row_num") > 1).drop("row_num") \
                           .withColumn("table", lit(table)) \
                           .withColumn("column", lit(column)) \
                           .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def allowed_values_check(df, row, allowed_values=None):
    table = row["table"]; column = row["column"]; check_type = "allowed_values_check"
    valid_df = df.filter(col(column).isin(allowed_values))
    invalid_df = df.filter(~col(column).isin(allowed_values)) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def range_check(df, row, min_value=None, max_value=None):
    table = row["table"]; column = row["column"]; check_type = "range_check"
    # Build condition robustly
    if min_value is None and max_value is None:
        condition = col(column).isNotNull()  # trivially true for non-nulls
    elif min_value is None:
        condition = col(column) <= max_value
    elif max_value is None:
        condition = col(column) >= min_value
    else:
        condition = (col(column) >= min_value) & (col(column) <= max_value)

    valid_df = df.filter(condition)
    invalid_df = df.filter(~condition) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def non_negative_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "non_negative_check"
    valid_df = df.filter(col(column) >= 0)
    invalid_df = df.filter(col(column) < 0) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def regex_check(df, row, pattern=None):
    table = row["table"]; column = row["column"]; check_type = "regex_check"
    valid_df = df.filter(col(column).rlike(pattern))
    invalid_df = df.filter(~col(column).rlike(pattern)) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def not_empty_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "not_empty_check"
    # Check if DataFrame has rows
    row_count = df.count()
    if row_count > 0:
        # Table is not empty
        valid_df = df
        invalid_df = df.limit(0).withColumn("table", lit(table)) \
                                .withColumn("column", lit(column)) \
                                .withColumn("check_type", lit(check_type))
    else:
        # Table is empty
        valid_df = df.limit(0)
        invalid_df = df.limit(0).withColumn("table", lit(table)) \
                                .withColumn("column", lit(column)) \
                                .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def data_type_check(df, row, expected_type=None):
    table = row["table"]; column = row["column"]; check_type = "data_type_check"
    # Get actual type from schema
    actual_type = dict(df.dtypes).get(column, None)
    # Convert Spark dtypes (string like "int", "string") into canonical form
    spark_type_map = {
        "string": "StringType",
        "int": "IntegerType",
        "bigint": "LongType",
        "double": "DoubleType",
        "float": "FloatType",
        "date": "DateType",
        "timestamp": "TimestampType",
        "boolean": "BooleanType"
    }
    # Map actual_type string to expected SparkType name
    actual_type_fmt = spark_type_map.get(actual_type, actual_type)

    if actual_type_fmt == expected_type:
        # All good: valid_df is full df, invalid/log are empty
        valid_df = df
        invalid_df = df.limit(0).withColumn("table", lit(table)) \
                                .withColumn("column", lit(column)) \
                                .withColumn("check_type", lit(check_type))
        log_df = _empty_log(df, table, column, check_type)
    else:
        # Mismatch: whole df goes to invalid (schema mismatch cannot be row-level)
        valid_df = df.limit(0)
        invalid_df = df.withColumn("table", lit(table)) \
                       .withColumn("column", lit(column)) \
                       .withColumn("check_type", lit(check_type))
        log_df = _empty_log(df, table, column, check_type)

    return valid_df, invalid_df, log_df
