import os

import awswrangler as wr

if __name__ =="__main__":
    
    STAGE = os.getenv("STAGE")
    GLUE_DATABASE = os.getenv("GLUE_DATABASE")
    GLUE_DATABASE_STORAGE_LOCATION = os.getenv("GLUE_DATABASE_STORAGE_LOCATION")
    PROD_GLUE_DATABASE = os.getenv("PROD_GLUE_DATABASE")

    wr.catalog.create_database(
        name=GLUE_DATABASE, 
        exist_ok=True)
    print(GLUE_DATABASE + " created")

    create_db_query = f"""
        SELECT 
            t.table_name
        FROM information_schema.tables t
        where t.table_schema = '{PROD_GLUE_DATABASE}'
            and t.table_type = 'BASE TABLE'
    """
    tables = wr.athena.read_sql_query(
        sql=create_db_query,
        database=GLUE_DATABASE,
    )

    for t in tables['table_name']:
        create_tb_query = f"""
            CREATE TABLE IF NOT EXISTS {GLUE_DATABASE}.{t} 
            WITH ( 
                table_type = 'ICEBERG', 
                location = '{GLUE_DATABASE_STORAGE_LOCATION}{GLUE_DATABASE}.db/{t}/', 
                is_external = false 
            ) AS 
            SELECT * 
            FROM {PROD_GLUE_DATABASE}.{t} 
        """

        wr.athena.start_query_execution(create_tb_query)
        print(GLUE_DATABASE + "." + t + " created")
        