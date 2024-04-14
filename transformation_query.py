from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("ReadParquetExample") \
    .getOrCreate()

# Read Parquet file into DataFrame
job_listing = spark.read.parquet("job_listings.parquet")
job_listing.createOrReplaceTempView('raw_job_listing')

bronze = spark.sql("""
    select 
        id,
        title,
        from_json(
          company,
          '__CLASS__ string, display_name string'
        ).display_name as company,
        created,
        from_json(
            category,
          '__CLASS__ string, tag string, label string'
        ).label as category,
        salary_is_predicted,
        split(
            regexp_replace(
                from_json(
                    location, 'area string, display_name string'
                ).area, 
            '[\]\\\["]',
            ''
            ),
            ','
        ) as area,
        contract_type,
        contract_time,
        salary_min,
        salary_max,
        to_utc_timestamp(current_timestamp(), "Australia/Sydney") as extraction_datetime_utc
        
    from raw_job_listing
""").createOrReplaceTempView('bronze_job_listing')


spark.sql("""
    select
        id,
        title,
        company,
        to_timestamp(created) as ad_creation_datetime_utc,
        category,
        cast(salary_is_predicted as boolean) as salary_is_predicted,
        area[0] as country,
        area[1] as state,
        area[2] as region,
        area[3] as city,
        contract_type,
        contract_time,
        cast(salary_min as int) as salary_min,
        cast(salary_max as int) as salary_max,
        extraction_datetime_utc
          
    from bronze_job_listing

""").createOrReplaceTempView('silver_job_listing')

spark.sql("""
    select
        *
    from silver_job_listing
    where lower(title) like '%data%engineer%'
    order by salary_max desc
""").show()