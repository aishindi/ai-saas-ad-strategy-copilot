from database.db import get_connection


def run_sql_query(query: str, params: tuple = ()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_top_roi_segments():
    query = """
    SELECT industry, company_size, role, region, historical_roi
    FROM audience_segments
    ORDER BY historical_roi DESC
    LIMIT 5
    """
    return run_sql_query(query)


def compare_platforms(platform1: str, platform2: str):
    query = """
    SELECT platform, avg_ctr, avg_cvr, avg_cac, avg_roi
    FROM platform_metrics
    WHERE platform IN (?, ?)
    """
    return run_sql_query(query, (platform1, platform2))


def get_underperforming_campaigns(roi_threshold: float = 1.5):
    query = """
    SELECT campaign_name, platform, roi, cost, conversions
    FROM campaigns
    WHERE roi < ?
    ORDER BY roi ASC
    """
    return run_sql_query(query, (roi_threshold,))


def get_best_regions_by_cac():
    query = """
    SELECT region, AVG(cost * 1.0 / NULLIF(conversions, 0)) AS avg_cac
    FROM campaigns
    GROUP BY region
    ORDER BY avg_cac ASC
    """
    return run_sql_query(query)