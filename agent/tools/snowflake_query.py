"""
snowflake_query.py
==================
Tool for the Agentic AI Assistant: execute parameterized SQL against
Snowflake and return results in a Pythonic format (list[dict]).

Requirements
------------
pip install snowflake-connector-python==3.6.0

Environment Variables
---------------------
SNOWFLAKE_ACCOUNT     e.g. abc-xy12345
SNOWFLAKE_USER        e.g. COREY_LEATH
SNOWFLAKE_PASSWORD    *****  (or use key-pair auth)
SNOWFLAKE_DATABASE    e.g. ANALYTICS_DB
SNOWFLAKE_SCHEMA      e.g. PUBLIC
SNOWFLAKE_WAREHOUSE   e.g. COMPUTE_WH
"""

import os
from contextlib import contextmanager

import snowflake.connector


@contextmanager
def snowflake_connection():
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    )
    try:
        yield conn
    finally:
        conn.close()

def run_query(sql: str, params: tuple | None = None) -> list[dict]:
    """
    Execute SQL and return results as list of dicts.

    Parameters
    ----------
    sql : str
        Parameterized SQL (use %s placeholders).
    params : tuple | None
        Values for placeholders.

    Returns
    -------
    list[dict]
        Query results with keys=column names, values=rows.
    """
    with snowflake_connection() as conn:
        cur = conn.cursor(snowflake.connector.DictCursor)
        cur.execute(sql, params) if params else cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        return results

# Quick CLI test (commented; ensure env vars first)
# if __name__ == "__main__":
#     rows = run_query("SELECT CURRENT_TIMESTAMP() AS ts")
#     print(rows)
