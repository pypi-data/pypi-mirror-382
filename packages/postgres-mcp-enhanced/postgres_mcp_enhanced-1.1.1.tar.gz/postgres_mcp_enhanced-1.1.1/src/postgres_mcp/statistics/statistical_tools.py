"""Statistical Analysis Tools for PostgreSQL MCP Server.

This module provides 8 statistical analysis tools:
- stats_descriptive: Mean, median, mode, std dev
- stats_percentiles: Quartiles, percentiles, outliers
- stats_correlation: Correlation analysis
- stats_regression: Linear regression analysis
- stats_time_series: Time series analysis
- stats_distribution: Distribution fitting
- stats_hypothesis: Basic hypothesis testing
- stats_sampling: Statistical sampling methods
"""

import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import cast

from typing_extensions import LiteralString

from ..sql import SqlDriver

logger = logging.getLogger(__name__)


def safe_float(value: Any) -> Optional[float]:
    """Safely convert a value to float, returning None if not possible."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> Optional[int]:
    """Safely convert a value to int, returning None if not possible."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class StatisticalTools:
    """Statistical analysis operations for PostgreSQL."""

    def __init__(self, sql_driver: SqlDriver):
        """Initialize statistical tools.

        Args:
            sql_driver: SQL driver instance for database operations
        """
        self.sql_driver = sql_driver

    async def stats_descriptive(
        self,
        table_name: str,
        column_name: str,
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate descriptive statistics for a numeric column.

        Args:
            table_name: Source table name
            column_name: Numeric column to analyze
            where_clause: Optional WHERE clause for filtering
            where_params: Parameters for WHERE clause

        Returns:
            Descriptive statistics (mean, median, mode, std dev, etc.)

        Examples:
            # Basic statistics for all data
            await stats_descriptive('sales', 'amount')

            # Statistics for filtered data
            await stats_descriptive('sales', 'amount',
                                  where_clause='region = %s',
                                  where_params=['West'])
        """
        try:
            where_sql = f"WHERE {where_clause}" if where_clause else ""
            params = where_params or []

            query = f"""
            WITH stats AS (
                SELECT
                    COUNT(*) as count,
                    AVG({column_name}) as mean,
                    STDDEV_POP({column_name}) as stddev_pop,
                    STDDEV_SAMP({column_name}) as stddev_samp,
                    VAR_POP({column_name}) as variance_pop,
                    VAR_SAMP({column_name}) as variance_samp,
                    MIN({column_name}) as min,
                    MAX({column_name}) as max,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {column_name}) as median,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {column_name}) as q1,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {column_name}) as q3,
                    MODE() WITHIN GROUP (ORDER BY {column_name}) as mode
                FROM {table_name}
                {where_sql}
            )
            SELECT
                count,
                mean,
                stddev_pop,
                stddev_samp,
                variance_pop,
                variance_samp,
                min,
                max,
                median,
                q1,
                q3,
                mode,
                (q3 - q1) as iqr,
                (max - min) as range,
                CASE
                    WHEN stddev_pop > 0 THEN (mean / stddev_pop)
                    ELSE NULL
                END as coefficient_of_variation
            FROM stats
            """

            result = await self.sql_driver.execute_query(cast(LiteralString, query), params)

            if not result:
                return {
                    "success": False,
                    "error": "No data returned from query",
                }

            row = result[0].cells
            return {
                "success": True,
                "table": table_name,
                "column": column_name,
                "count": row.get("count"),
                "mean": safe_float(row.get("mean")),
                "median": safe_float(row.get("median")),
                "mode": safe_float(row.get("mode")),
                "std_dev_population": safe_float(row.get("stddev_pop")),
                "std_dev_sample": safe_float(row.get("stddev_samp")),
                "variance_population": safe_float(row.get("variance_pop")),
                "variance_sample": safe_float(row.get("variance_samp")),
                "min": safe_float(row.get("min")),
                "max": safe_float(row.get("max")),
                "q1": safe_float(row.get("q1")),
                "q3": safe_float(row.get("q3")),
                "iqr": safe_float(row.get("iqr")),
                "range": safe_float(row.get("range")),
                "coefficient_of_variation": safe_float(row.get("coefficient_of_variation")),
            }

        except Exception as e:
            logger.error(f"Error in stats_descriptive: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def stats_percentiles(
        self,
        table_name: str,
        column_name: str,
        percentiles: Optional[List[float]] = None,
        detect_outliers: bool = True,
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate percentiles and detect outliers.

        Args:
            table_name: Source table name
            column_name: Numeric column to analyze
            percentiles: List of percentiles to calculate (0-1 scale)
            detect_outliers: Whether to detect outliers using IQR method
            where_clause: Optional WHERE clause for filtering
            where_params: Parameters for WHERE clause

        Returns:
            Percentile values and outlier information

        Examples:
            # Standard quartiles
            await stats_percentiles('sales', 'amount')

            # Custom percentiles with outlier detection
            await stats_percentiles('sales', 'amount',
                                  percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
        """
        try:
            if percentiles is None:
                percentiles = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]

            where_sql = f"WHERE {where_clause}" if where_clause else ""
            params = where_params or []

            # Build percentile calculations
            percentile_calcs: List[str] = []
            for p in percentiles:
                percentile_calcs.append(f"PERCENTILE_CONT({p}) WITHIN GROUP (ORDER BY {column_name}) as p{int(p * 100)}")

            query = f"""
            WITH percentiles AS (
                SELECT
                    {", ".join(percentile_calcs)}
                FROM {table_name}
                {where_sql}
            )
            """

            if detect_outliers:
                query += f"""
                , quartiles AS (
                    SELECT
                        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {column_name}) as q1,
                        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {column_name}) as q3
                    FROM {table_name}
                    {where_sql}
                ),
                outlier_bounds AS (
                    SELECT
                        q1,
                        q3,
                        q3 - q1 as iqr,
                        q1 - 1.5 * (q3 - q1) as lower_bound,
                        q3 + 1.5 * (q3 - q1) as upper_bound
                    FROM quartiles
                ),
                outliers AS (
                    SELECT COUNT(*) as outlier_count
                    FROM {table_name}, outlier_bounds
                    {where_sql}
                    {"AND" if where_clause else "WHERE"} (
                        {column_name} < outlier_bounds.lower_bound OR
                        {column_name} > outlier_bounds.upper_bound
                    )
                )
                SELECT
                    percentiles.*,
                    outlier_bounds.q1,
                    outlier_bounds.q3,
                    outlier_bounds.iqr,
                    outlier_bounds.lower_bound,
                    outlier_bounds.upper_bound,
                    outliers.outlier_count
                FROM percentiles, outlier_bounds, outliers
                """
            else:
                query += "SELECT * FROM percentiles"

            result = await self.sql_driver.execute_query(cast(LiteralString, query), params)

            if not result:
                return {
                    "success": False,
                    "error": "No data returned from query",
                }

            row = result[0].cells
            response: Dict[str, Any] = {
                "success": True,
                "table": table_name,
                "column": column_name,
                "percentiles": {},
            }

            # Extract percentile values
            for p in percentiles:
                key = f"p{int(p * 100)}"
                if key in row:
                    response["percentiles"][f"p{int(p * 100)}"] = safe_float(row[key])

            # Add outlier information if detected
            if detect_outliers:
                response["outlier_detection"] = {
                    "q1": safe_float(row.get("q1")),
                    "q3": safe_float(row.get("q3")),
                    "iqr": safe_float(row.get("iqr")),
                    "lower_bound": safe_float(row.get("lower_bound")),
                    "upper_bound": safe_float(row.get("upper_bound")),
                    "outlier_count": int(row.get("outlier_count") or 0),
                }

            return response

        except Exception as e:
            logger.error(f"Error in stats_percentiles: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def stats_correlation(
        self,
        table_name: str,
        column1: str,
        column2: str,
        method: str = "pearson",
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate correlation between two numeric columns.

        Args:
            table_name: Source table name
            column1: First numeric column
            column2: Second numeric column
            method: Correlation method ('pearson' or 'spearman')
            where_clause: Optional WHERE clause for filtering
            where_params: Parameters for WHERE clause

        Returns:
            Correlation coefficient and related statistics

        Examples:
            # Pearson correlation
            await stats_correlation('sales', 'price', 'quantity')

            # Spearman rank correlation
            await stats_correlation('sales', 'price', 'quantity', method='spearman')
        """
        try:
            where_sql = f"WHERE {where_clause}" if where_clause else ""
            params = where_params or []

            if method.lower() == "pearson":
                # Pearson correlation coefficient
                query = f"""
                WITH stats AS (
                    SELECT
                        COUNT(*) as n,
                        CORR({column1}, {column2}) as correlation,
                        AVG({column1}) as mean1,
                        AVG({column2}) as mean2,
                        STDDEV_POP({column1}) as stddev1,
                        STDDEV_POP({column2}) as stddev2,
                        COVAR_POP({column1}, {column2}) as covariance
                    FROM {table_name}
                    {where_sql}
                )
                SELECT
                    n,
                    correlation,
                    mean1,
                    mean2,
                    stddev1,
                    stddev2,
                    covariance,
                    POWER(correlation, 2) as r_squared
                FROM stats
                """
            elif method.lower() == "spearman":
                # Spearman rank correlation
                query = f"""
                WITH ranked AS (
                    SELECT
                        RANK() OVER (ORDER BY {column1}) as rank1,
                        RANK() OVER (ORDER BY {column2}) as rank2
                    FROM {table_name}
                    {where_sql}
                )
                SELECT
                    COUNT(*) as n,
                    CORR(rank1, rank2) as correlation,
                    POWER(CORR(rank1, rank2), 2) as r_squared
                FROM ranked
                """
            else:
                return {
                    "success": False,
                    "error": f"Unknown correlation method: {method}. Use 'pearson' or 'spearman'",
                }

            result = await self.sql_driver.execute_query(cast(LiteralString, query), params)

            if not result:
                return {
                    "success": False,
                    "error": "No data returned from query",
                }

            row = result[0].cells
            response = {
                "success": True,
                "table": table_name,
                "column1": column1,
                "column2": column2,
                "method": method,
                "n": int(row.get("n") or 0),
                "correlation": safe_float(row.get("correlation")),
                "r_squared": safe_float(row.get("r_squared")),
            }

            if method.lower() == "pearson":
                response.update(
                    {
                        "mean1": safe_float(row.get("mean1")),
                        "mean2": safe_float(row.get("mean2")),
                        "stddev1": safe_float(row.get("stddev1")),
                        "stddev2": safe_float(row.get("stddev2")),
                        "covariance": safe_float(row.get("covariance")),
                    }
                )

            return response

        except Exception as e:
            logger.error(f"Error in stats_correlation: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def stats_regression(
        self,
        table_name: str,
        x_column: str,
        y_column: str,
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate linear regression analysis.

        Args:
            table_name: Source table name
            x_column: Independent variable (X)
            y_column: Dependent variable (Y)
            where_clause: Optional WHERE clause for filtering
            where_params: Parameters for WHERE clause

        Returns:
            Linear regression coefficients and statistics

        Examples:
            # Simple linear regression
            await stats_regression('sales', 'advertising_spend', 'revenue')
        """
        try:
            where_sql = f"WHERE {where_clause}" if where_clause else ""
            params = where_params or []

            query = f"""
            WITH regression_data AS (
                SELECT
                    COUNT(*) as n,
                    REGR_SLOPE({y_column}, {x_column}) as slope,
                    REGR_INTERCEPT({y_column}, {x_column}) as intercept,
                    REGR_R2({y_column}, {x_column}) as r_squared,
                    REGR_AVGX({y_column}, {x_column}) as mean_x,
                    REGR_AVGY({y_column}, {x_column}) as mean_y,
                    REGR_SXX({y_column}, {x_column}) as sxx,
                    REGR_SYY({y_column}, {x_column}) as syy,
                    REGR_SXY({y_column}, {x_column}) as sxy,
                    CORR({x_column}, {y_column}) as correlation
                FROM {table_name}
                {where_sql}
            )
            SELECT
                n,
                slope,
                intercept,
                r_squared,
                mean_x,
                mean_y,
                sxx,
                syy,
                sxy,
                correlation,
                SQRT(r_squared) as r,
                CASE
                    WHEN n > 2 THEN SQRT((1 - r_squared) * syy / (n - 2))
                    ELSE NULL
                END as std_error
            FROM regression_data
            """

            result = await self.sql_driver.execute_query(cast(LiteralString, query), params)

            if not result:
                return {
                    "success": False,
                    "error": "No data returned from query",
                }

            row = result[0].cells
            slope = safe_float(row.get("slope"))
            intercept = safe_float(row.get("intercept"))
            return {
                "success": True,
                "table": table_name,
                "x_column": x_column,
                "y_column": y_column,
                "n": int(row.get("n") or 0),
                "slope": slope,
                "intercept": intercept,
                "r_squared": safe_float(row.get("r_squared")),
                "r": safe_float(row.get("r")),
                "correlation": safe_float(row.get("correlation")),
                "mean_x": safe_float(row.get("mean_x")),
                "mean_y": safe_float(row.get("mean_y")),
                "std_error": safe_float(row.get("std_error")),
                "equation": f"y = {slope:.4f}x + {intercept:.4f}" if slope is not None and intercept is not None else None,
            }

        except Exception as e:
            logger.error(f"Error in stats_regression: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def stats_time_series(
        self,
        table_name: str,
        time_column: str,
        value_column: str,
        interval: str = "1 day",
        aggregation: str = "avg",
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze time series data with aggregation.

        Args:
            table_name: Source table name
            time_column: Timestamp column
            value_column: Value column to aggregate
            interval: Time interval for grouping (e.g., '1 hour', '1 day', '1 week')
            aggregation: Aggregation function ('avg', 'sum', 'count', 'min', 'max')
            where_clause: Optional WHERE clause for filtering
            where_params: Parameters for WHERE clause

        Returns:
            Time series data with trend and statistics

        Examples:
            # Daily average sales
            await stats_time_series('orders', 'created_at', 'amount',
                                   interval='1 day', aggregation='avg')

            # Hourly order count
            await stats_time_series('orders', 'created_at', 'order_id',
                                   interval='1 hour', aggregation='count')
        """
        try:
            where_sql = f"WHERE {where_clause}" if where_clause else ""
            params = where_params or []

            # Validate aggregation function
            valid_aggs = ["avg", "sum", "count", "min", "max"]
            if aggregation.lower() not in valid_aggs:
                return {
                    "success": False,
                    "error": f"Invalid aggregation: {aggregation}. Use one of: {', '.join(valid_aggs)}",
                }

            agg_func = aggregation.upper()

            query = f"""
            WITH time_series AS (
                SELECT
                    DATE_TRUNC('{interval}', {time_column}) as time_bucket,
                    {agg_func}({value_column}) as value
                FROM {table_name}
                {where_sql}
                GROUP BY DATE_TRUNC('{interval}', {time_column})
                ORDER BY time_bucket
            ),
            aggregated AS (
                SELECT
                    COUNT(*) as period_count,
                    AVG(value) as mean,
                    STDDEV_POP(value) as stddev,
                    MIN(value) as min_value,
                    MAX(value) as max_value
                FROM time_series
            ),
            first_last AS (
                SELECT
                    MIN(value) FILTER (WHERE time_bucket = (SELECT MIN(time_bucket) FROM time_series)) as first_value,
                    MAX(value) FILTER (WHERE time_bucket = (SELECT MAX(time_bucket) FROM time_series)) as last_value
                FROM time_series
            ),
            trend AS (
                SELECT
                    REGR_SLOPE(value, EXTRACT(EPOCH FROM time_bucket)) as trend_slope,
                    REGR_R2(value, EXTRACT(EPOCH FROM time_bucket)) as trend_r_squared
                FROM time_series
            )
            SELECT
                aggregated.period_count,
                aggregated.mean,
                aggregated.stddev,
                aggregated.min_value,
                aggregated.max_value,
                first_last.first_value,
                first_last.last_value,
                trend.trend_slope,
                trend.trend_r_squared,
                (first_last.last_value - first_last.first_value) as total_change,
                CASE
                    WHEN first_last.first_value != 0 THEN
                        ((first_last.last_value - first_last.first_value) / first_last.first_value) * 100
                    ELSE NULL
                END as percent_change
            FROM aggregated, first_last, trend
            """

            result = await self.sql_driver.execute_query(cast(LiteralString, query), params)

            if not result:
                return {
                    "success": False,
                    "error": "No data returned from query",
                }

            row = result[0].cells
            return {
                "success": True,
                "table": table_name,
                "time_column": time_column,
                "value_column": value_column,
                "interval": interval,
                "aggregation": aggregation,
                "period_count": int(row.get("period_count") or 0),
                "mean": safe_float(row.get("mean")),
                "stddev": safe_float(row.get("stddev")),
                "min_value": safe_float(row.get("min_value")),
                "max_value": safe_float(row.get("max_value")),
                "first_value": safe_float(row.get("first_value")),
                "last_value": safe_float(row.get("last_value")),
                "total_change": safe_float(row.get("total_change")),
                "percent_change": safe_float(row.get("percent_change")),
                "trend_slope": safe_float(row.get("trend_slope")),
                "trend_r_squared": safe_float(row.get("trend_r_squared")),
            }

        except Exception as e:
            logger.error(f"Error in stats_time_series: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def stats_distribution(
        self,
        table_name: str,
        column_name: str,
        bins: int = 10,
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze data distribution and fit to common distributions.

        Args:
            table_name: Source table name
            column_name: Numeric column to analyze
            bins: Number of bins for histogram
            where_clause: Optional WHERE clause for filtering
            where_params: Parameters for WHERE clause

        Returns:
            Distribution analysis with histogram and statistics

        Examples:
            # Analyze sales distribution
            await stats_distribution('sales', 'amount', bins=20)
        """
        try:
            where_sql = f"WHERE {where_clause}" if where_clause else ""
            params = where_params or []

            query = f"""
            WITH bounds AS (
                SELECT
                    MIN({column_name}) as min_val,
                    MAX({column_name}) as max_val,
                    (MAX({column_name}) - MIN({column_name})) / {bins} as bin_width
                FROM {table_name}
                {where_sql}
            ),
            histogram AS (
                SELECT
                    WIDTH_BUCKET({column_name}, bounds.min_val, bounds.max_val, {bins}) as bin,
                    COUNT(*) as frequency,
                    bounds.min_val + (WIDTH_BUCKET({column_name}, bounds.min_val, bounds.max_val, {bins}) - 1) * bounds.bin_width as bin_lower,
                    bounds.min_val + WIDTH_BUCKET({column_name}, bounds.min_val, bounds.max_val, {bins}) * bounds.bin_width as bin_upper
                FROM {table_name}, bounds
                {where_sql}
                GROUP BY bin, bounds.min_val, bounds.bin_width, bounds.max_val
                ORDER BY bin
            ),
            stats AS (
                SELECT
                    COUNT(*) as total_count,
                    AVG({column_name}) as mean,
                    STDDEV_POP({column_name}) as stddev,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {column_name}) as median
                FROM {table_name}
                {where_sql}
            ),
            skewness_calc AS (
                SELECT
                    AVG(POWER(({column_name} - stats.mean) / NULLIF(stats.stddev, 0), 3)) as skewness,
                    AVG(POWER(({column_name} - stats.mean) / NULLIF(stats.stddev, 0), 4)) - 3 as kurtosis
                FROM {table_name}, stats
                {where_sql}
            )
            SELECT
                json_agg(json_build_object(
                    'bin', histogram.bin,
                    'bin_lower', histogram.bin_lower,
                    'bin_upper', histogram.bin_upper,
                    'frequency', histogram.frequency,
                    'relative_frequency', histogram.frequency::float / stats.total_count
                ) ORDER BY histogram.bin) as histogram_data,
                stats.total_count,
                stats.mean,
                stats.stddev,
                stats.median,
                skewness_calc.skewness,
                skewness_calc.kurtosis
            FROM histogram, stats, skewness_calc
            GROUP BY stats.total_count, stats.mean, stats.stddev, stats.median,
                     skewness_calc.skewness, skewness_calc.kurtosis
            """

            result = await self.sql_driver.execute_query(cast(LiteralString, query), params)

            if not result:
                return {
                    "success": False,
                    "error": "No data returned from query",
                }

            row = result[0].cells
            return {
                "success": True,
                "table": table_name,
                "column": column_name,
                "bins": bins,
                "total_count": int(row.get("total_count") or 0),
                "mean": safe_float(row.get("mean")),
                "stddev": safe_float(row.get("stddev")),
                "median": safe_float(row.get("median")),
                "skewness": safe_float(row.get("skewness")),
                "kurtosis": safe_float(row.get("kurtosis")),
                "histogram": row.get("histogram_data"),
            }

        except Exception as e:
            logger.error(f"Error in stats_distribution: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def stats_hypothesis(
        self,
        table_name: str,
        column_name: str,
        test_type: str = "t_test",
        hypothesis_value: Optional[float] = None,
        group_column: Optional[str] = None,
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Perform basic hypothesis testing.

        Args:
            table_name: Source table name
            column_name: Numeric column to test
            test_type: Type of test ('t_test', 'z_test', 'chi_square')
            hypothesis_value: Hypothesized mean value (for one-sample tests)
            group_column: Column for grouping (for two-sample tests)
            where_clause: Optional WHERE clause for filtering
            where_params: Parameters for WHERE clause

        Returns:
            Hypothesis test results with test statistic and interpretation

        Examples:
            # One-sample t-test
            await stats_hypothesis('sales', 'amount', test_type='t_test',
                                  hypothesis_value=1000)

            # Two-sample t-test
            await stats_hypothesis('sales', 'amount', test_type='t_test',
                                  group_column='region')
        """
        try:
            where_sql = f"WHERE {where_clause}" if where_clause else ""
            params = where_params or []

            if test_type.lower() == "t_test" and hypothesis_value is not None:
                # One-sample t-test
                query = f"""
                WITH stats AS (
                    SELECT
                        COUNT(*) as n,
                        AVG({column_name}) as sample_mean,
                        STDDEV_SAMP({column_name}) as sample_std
                    FROM {table_name}
                    {where_sql}
                )
                SELECT
                    n,
                    sample_mean,
                    sample_std,
                    {hypothesis_value} as hypothesis_mean,
                    (sample_mean - {hypothesis_value}) / (sample_std / SQRT(n)) as t_statistic,
                    n - 1 as degrees_of_freedom
                FROM stats
                """
            elif test_type.lower() == "t_test" and group_column:
                # Two-sample t-test
                query = f"""
                WITH group_stats AS (
                    SELECT
                        {group_column} as group_value,
                        COUNT(*) as n,
                        AVG({column_name}) as mean,
                        STDDEV_SAMP({column_name}) as std
                    FROM {table_name}
                    {where_sql}
                    GROUP BY {group_column}
                    LIMIT 2
                ),
                test_calc AS (
                    SELECT
                        MAX(CASE WHEN rn = 1 THEN mean END) as mean1,
                        MAX(CASE WHEN rn = 1 THEN std END) as std1,
                        MAX(CASE WHEN rn = 1 THEN n END) as n1,
                        MAX(CASE WHEN rn = 2 THEN mean END) as mean2,
                        MAX(CASE WHEN rn = 2 THEN std END) as std2,
                        MAX(CASE WHEN rn = 2 THEN n END) as n2
                    FROM (
                        SELECT *, ROW_NUMBER() OVER () as rn
                        FROM group_stats
                    ) ranked
                )
                SELECT
                    n1,
                    n2,
                    mean1,
                    mean2,
                    std1,
                    std2,
                    (mean1 - mean2) / SQRT((std1 * std1 / n1) + (std2 * std2 / n2)) as t_statistic,
                    n1 + n2 - 2 as degrees_of_freedom
                FROM test_calc
                """
            else:
                return {
                    "success": False,
                    "error": "Invalid test configuration. Provide either hypothesis_value (one-sample) or group_column (two-sample)",
                }

            result = await self.sql_driver.execute_query(cast(LiteralString, query), params)

            if not result:
                return {
                    "success": False,
                    "error": "No data returned from query",
                }

            row = result[0].cells
            t_stat = safe_float(row.get("t_statistic"))

            response = {
                "success": True,
                "table": table_name,
                "column": column_name,
                "test_type": test_type,
                "t_statistic": t_stat,
                "degrees_of_freedom": int(row.get("degrees_of_freedom") or 0) if row.get("degrees_of_freedom") else None,
            }

            # Add interpretation
            if t_stat is not None:
                if abs(t_stat) > 2.576:
                    response["interpretation"] = "Highly significant (p < 0.01)"
                elif abs(t_stat) > 1.96:
                    response["interpretation"] = "Significant (p < 0.05)"
                elif abs(t_stat) > 1.645:
                    response["interpretation"] = "Marginally significant (p < 0.10)"
                else:
                    response["interpretation"] = "Not significant (p >= 0.10)"

            if hypothesis_value is not None:
                response.update(
                    {
                        "n": int(row.get("n") or 0),
                        "sample_mean": safe_float(row.get("sample_mean")),
                        "sample_std": safe_float(row.get("sample_std")),
                        "hypothesis_mean": hypothesis_value,
                    }
                )
            else:
                response.update(
                    {
                        "n1": int(row.get("n1") or 0),
                        "n2": int(row.get("n2") or 0),
                        "mean1": safe_float(row.get("mean1")),
                        "mean2": safe_float(row.get("mean2")),
                        "std1": safe_float(row.get("std1")),
                        "std2": safe_float(row.get("std2")),
                    }
                )

            return response

        except Exception as e:
            logger.error(f"Error in stats_hypothesis: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def stats_sampling(
        self,
        table_name: str,
        sample_size: Optional[int] = None,
        sample_percent: Optional[float] = None,
        method: str = "random",
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Generate statistical samples from a table.

        Args:
            table_name: Source table name
            sample_size: Absolute number of rows to sample
            sample_percent: Percentage of rows to sample (0-100)
            method: Sampling method ('random', 'systematic', 'stratified')
            where_clause: Optional WHERE clause for filtering
            where_params: Parameters for WHERE clause

        Returns:
            Sample metadata and statistics

        Examples:
            # Random sample of 1000 rows
            await stats_sampling('orders', sample_size=1000, method='random')

            # Random 10% sample
            await stats_sampling('orders', sample_percent=10, method='random')
        """
        try:
            where_sql = f"WHERE {where_clause}" if where_clause else ""
            params = where_params or []

            # Determine sample size
            if sample_size is None and sample_percent is None:
                return {
                    "success": False,
                    "error": "Must specify either sample_size or sample_percent",
                }

            if method.lower() == "random":
                if sample_percent:
                    sample_clause = f"TABLESAMPLE BERNOULLI ({sample_percent})"
                else:
                    # At this point, sample_size must be set (checked earlier)
                    if sample_size is None:
                        return {
                            "success": False,
                            "error": "Must specify either sample_size or sample_percent",
                        }

                    # Get total count first
                    count_query = f"SELECT COUNT(*) as total FROM {table_name} {where_sql}"
                    count_result = await self.sql_driver.execute_query(cast(LiteralString, count_query), params)
                    total_optional = safe_int(count_result[0].cells.get("total")) if count_result else None

                    if total_optional is None or total_optional == 0:
                        return {
                            "success": False,
                            "error": "No rows found in table",
                        }

                    # Type guard: at this point total_optional is guaranteed to be int
                    assert isinstance(total_optional, int)
                    sample_percent = min((sample_size / float(total_optional or 1)) * 100, 100)
                    sample_clause = f"TABLESAMPLE BERNOULLI ({sample_percent})"

                query = f"""
                WITH sample AS (
                    SELECT COUNT(*) as sample_count
                    FROM {table_name} {sample_clause}
                    {where_sql}
                ),
                total AS (
                    SELECT COUNT(*) as total_count
                    FROM {table_name}
                    {where_sql}
                )
                SELECT
                    total.total_count,
                    sample.sample_count,
                    (sample.sample_count::float / total.total_count * 100) as actual_percent
                FROM sample, total
                """

                result = await self.sql_driver.execute_query(cast(LiteralString, query), params)

                if not result:
                    return {
                        "success": False,
                        "error": "No data returned from query",
                    }

                row = result[0].cells
                return {
                    "success": True,
                    "table": table_name,
                    "method": method,
                    "total_rows": int(row.get("total_count") or 0),
                    "sample_rows": int(row.get("sample_count") or 0),
                    "sample_percent": safe_float(row.get("actual_percent")) or 0.0,
                    "requested_sample_size": sample_size,
                    "requested_sample_percent": sample_percent,
                }

            else:
                return {
                    "success": False,
                    "error": f"Sampling method '{method}' not yet implemented. Use 'random'",
                }

        except Exception as e:
            logger.error(f"Error in stats_sampling: {e}")
            return {
                "success": False,
                "error": str(e),
            }
