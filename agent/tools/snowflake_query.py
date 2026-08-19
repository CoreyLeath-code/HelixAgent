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

 8ëÏ-¢G§²ÚîÆ­yÖS ¢—F†öâ7&2öÖ–âç¢—F†öâ7&2öÖ–âç’Ò×&ö×B$6ö×&RfV7F÷'2æBG&gB7VÖÖ'’ ¢""  ¦–×÷'B&w'6P¦–×÷'B÷0¦–×÷'B7—0 ¢2Vç7W&RF†R&ö¦V7B&ö÷B—2–âF†RF‚v†Vâ'Vææ–ær267&—@§7—2çF‚æ–ç6W'BƒÂ÷2çF‚æ¦ö–â†÷2çF‚æF—&æÖR…õöf–ÆUõò’Â"ââ"’ ¦g&öÒ7&2çWF–Ç2æÆövvW"–×÷'B6WGWöÆövvW  ¦ÆörÒ6WGWöÆövvW"‚  ¦FVb'6Uö&w2‚’Óâ&w'6RäæÖW76S ¢'6W"Ò&w'6Rä&wVÖVçE'6W"€¢FW67&—F–öãÒ$†VÆ—„vVçB(	2’×÷vW&VBvVçBg&ÖWv÷&² ¢¢'6W"æFEö&wVÖVçB€¢"Ò×&ö×B"À¢G—S×7G"À¢FVfVÇCÒ$†VÆÆòÂ†VÆ—„vVçB'VâV–6²6Öö¶RFW7Bâ"À¢†VÇÒ%&ö×BFò6VæBFòF†RvVçB"À¢¢&WGW&â'6W"ç'6Uö&w2‚  ¦FVbÖ–â‚’ÓâæöæS ¢&w2Ò'6Uö&w2‚¢Æöræ–æfò‚$†VÆ—„vVçB7F'F–ærâââ"¢Æöræ–æfò†b%&ö×C¢¶&w2ç&ö×GÒ" ¢G'“ ¢g&öÒvVçBævVçEö6÷&R–×÷'BvVçF–476—7Fç@ ¢Æöræ–æfò‚$–æ—F–Æ—¦–ærvVçB6÷&Râââ"¢76—7FçBÒvVçF–476—7FçB‚¢÷WGWBÒ76—7FçBç'Vâ†&w2ç&ö×B¢Æöræ–æfò‚$vVçB'Vâ6ö×ÆWFRâ"¢&–çB†b$vVçB÷WGWC¢¶÷WGWGÒ"¢W†6WBW†6WF–öâ2W†3¢2æ÷¢$ÄS¢Æörçv&æ–ær†b$vVçB6÷&RVæf–Æ&ÆR‡¶W†7Ò“²'Vææ–ærV6†òÖöFRâ"¢&–çB†b%´†VÆ—„vVçEÒV6†ó¢¶&w2ç&ö×GÒ"  ¦–bõöæÖUõòÓÒ%õöÖ–åõò# ¢Ö–â‚ 