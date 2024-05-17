import os

import awswrangler as wr

if __name__ =="__main__":
    STAGE = os.getenv("STAGE", "dev")
    GLUE_DATABASE = os.getenv("GLUE_DATABASE", "job")

    tear_down_query = f"""
        DROP DATABASE {GLUE_DATABASE} CASCADE
    """
    wr.athena.start_query_execution(tear_down_query)
    print(GLUE_DATABASE + " destroyed")