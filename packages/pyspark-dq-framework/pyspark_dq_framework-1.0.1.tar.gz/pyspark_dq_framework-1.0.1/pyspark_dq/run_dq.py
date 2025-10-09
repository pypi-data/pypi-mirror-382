import json
from typing import Dict, Callable
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from .config import dq_config
from .validate_checks import validate_checks


def run_dq_pipeline(
    spark: SparkSession,
    df_dict: Dict[str, DataFrame],
    config_path: str,
    checks: Dict[str, Callable] = None,
    max_json_records: int = None
) -> Dict[str, Dict[str, DataFrame]]:
    """
    Optimized Data Quality Pipeline
    - Runs each check and generates clean/error/summary data in one pass.
    - Per-column, per-check failed counts (no overlap across same check name).
    """

    dq_config_df, return_mode = dq_config(spark, config_path)
    validate_checks(dq_config_df, checks)

    result_dict = []
    summary_rows = []

    for table_name, df in df_dict.items():
        df = df.persist()
        raw_with_id = None
        try:
            raw_df = df
            total_rows = raw_df.count()
            raw_with_id = raw_df.withColumn("__dq_row_id", F.monotonically_increasing_id()).persist()

            # prepare invalid rows collector
            row_invalid_flags = []

            # wrap each check to parse params
            def _wrapped(func):
                def call(df_, row_):
                    params = json.loads(row_["params"]) if row_["params"] else {}
                    return func(df_, row_, **params)
                return call

            table_check_map = {name: _wrapped(func) for name, func in checks.items()}
            rules = dq_config_df.filter(F.col("table") == table_name).collect()

            # Run checks and collect invalids + summary simultaneously
            for row in rules:
                check_name = row["check"]
                column_name = row["column"]

                if check_name not in table_check_map:
                    raise ValueError(f"Check {check_name} not found in provided checks")

                valid_df, invalid_df, _ = table_check_map[check_name](raw_with_id, row)

                # ensure __dq_row_id is present in invalid_df
                if "__dq_row_id" not in invalid_df.columns:
                    common_cols = [c for c in invalid_df.columns if c in raw_with_id.columns and c != "__dq_row_id"]
                    if common_cols:
                        invalid_ids = (
                            invalid_df.select(*common_cols).distinct()
                            .join(
                                raw_with_id.select("__dq_row_id", *common_cols).distinct(),
                                on=common_cols,
                                how="inner"
                            )
                            .select("__dq_row_id")
                        )
                        invalid_df = invalid_ids.join(raw_with_id, on="__dq_row_id", how="inner")
                    else:
                        raise ValueError(
                            f"Check {check_name} on column {column_name} cannot map to __dq_row_id. "
                            "Ensure check returns rows with identifying columns."
                        )

                # tag invalid rows
                invalid_df_tagged = (
                    invalid_df
                    .withColumn("__failed_check", F.lit(check_name))
                    .withColumn("__failed_column", F.lit(column_name))
                )

                # store invalid rows
                row_invalid_flags.append(invalid_df_tagged.select(*raw_with_id.columns, "__failed_check", "__failed_column"))

                # compute summary metrics right here
                failed_count = invalid_df_tagged.select("__dq_row_id").distinct().count()
                failed_percentage = round((failed_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

                # build failed record JSON (limited if needed)
                json_cols = [c for c in invalid_df_tagged.columns if c not in ("__failed_check", "__failed_column", "__dq_row_id")]
                failed_records_json = []
                if json_cols:
                    limit_df = invalid_df_tagged.limit(max_json_records) if max_json_records else invalid_df_tagged
                    failed_records_json = (
                        limit_df
                        .select(
                            F.to_json(
                                F.struct(*[F.col(c) for c in json_cols]),
                                options={"ignoreNullFields": "false"}
                            ).alias("json")
                        )
                        .agg(F.collect_list("json").alias("failed_records_json"))
                        .collect()[0]["failed_records_json"]
                    ) or []

                summary_rows.append(
                    (
                        table_name,
                        column_name,
                        check_name,
                        total_rows,
                        failed_count,
                        failed_percentage,
                        json.dumps(failed_records_json)
                    )
                )

            # union all invalid rows
            if row_invalid_flags:
                error_df = row_invalid_flags[0]
                for df_ in row_invalid_flags[1:]:
                    error_df = error_df.unionByName(df_, allowMissingColumns=True)
            else:
                empty_schema = raw_with_id.schema.add("__failed_check", "string").add("__failed_column", "string")
                error_df = spark.createDataFrame([], empty_schema)

            # build clean_df by removing failed ids
            if row_invalid_flags:
                error_ids = error_df.select("__dq_row_id").distinct()
                clean_df = raw_with_id.join(error_ids, on="__dq_row_id", how="left_anti").drop("__dq_row_id")
            else:
                clean_df = raw_df

            # prepare final results for this table
            table_result = {}
            if "summary+clean" in return_mode or "all" in return_mode:
                table_result["clean"] = clean_df
            if "summary+error" in return_mode or "all" in return_mode:
                table_result["error"] = error_df.drop("__dq_row_id")

            if table_result:
                result_dict.append((table_name.lower(), table_result))

        finally:
            if raw_with_id is not None:
                try:
                    raw_with_id.unpersist()
                except Exception:
                    pass
            try:
                df.unpersist()
            except Exception:
                pass

    # build summary dataframe
    summary_schema = """
        table_name STRING, 
        column_name STRING, 
        check_type STRING, 
        total_rows LONG, 
        failed_count LONG, 
        failed_percentage DOUBLE, 
        failed_records_json STRING
    """
    summary_df = spark.createDataFrame(summary_rows, schema=summary_schema)

    # final result dictionary
    final_result = {name: tbl for name, tbl in result_dict}
    final_result["summary"] = summary_df
    return final_result
