resource "aws_glue_catalog_database" "job" {
  catalog_id   = var.aws_account_id
  name         = var.glue_database_name
  create_table_default_permission {
    permissions = ["ALL"]
    principal {
      data_lake_principal_identifier = "IAM_ALLOWED_PRINCIPALS"
    }
  }
}

resource "aws_glue_catalog_table" "stg__job_description" {
  catalog_id    = var.aws_account_id
  database_name = var.glue_database_name
  name          = "stg__job_description"
  table_type         = "EXTERNAL_TABLE"
  open_table_format_input {
    iceberg_input {
      metadata_operation = "CREATE"
    }
  }
  storage_descriptor {

    location = format("s3://%s/%s.db/stg__job_description", aws_s3_bucket.datalake_storage_bucket.id, var.glue_database_name)
    columns {
      name    = "id"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "1"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "full_description"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "2"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "extraction_time_utc"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "3"
        "iceberg.field.optional" = "true"
      }
      type = "timestamp"
    }
  }
}

resource "aws_glue_catalog_table" "stg__job_skills" {
  catalog_id    = var.aws_account_id
  database_name = var.glue_database_name
  name          = "stg__job_skills"
  table_type    = "EXTERNAL_TABLE"
  
  open_table_format_input {
    iceberg_input {
      metadata_operation = "CREATE"
    }
  }
  storage_descriptor {

    location = format("s3://%s/%s.db/stg__job_skills", aws_s3_bucket.datalake_storage_bucket.id, var.glue_database_name)

    columns {
      name    = "id"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "1"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "skill"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "2"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "extraction_time_utc"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "3"
        "iceberg.field.optional" = "true"
      }
      type = "timestamp"
    }
  }
}

resource "aws_glue_catalog_table" "stg__job_listing" {
  catalog_id    = var.aws_account_id
  database_name = var.glue_database_name
  name          = "stg__job_listing"
  table_type    = "EXTERNAL_TABLE"

  open_table_format_input {
    iceberg_input {
      metadata_operation = "CREATE"
    }
  }
  storage_descriptor {

    location = format("s3://%s/%s.db/stg__job_listing", aws_s3_bucket.datalake_storage_bucket.id, var.glue_database_name)

    columns {
      name    = "description"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "1"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "id"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "2"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "location"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "3"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "redirect_url"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "4"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "salary_is_predicted"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "5"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "company"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "6"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "__class__"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "7"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "adref"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "8"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "category"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "9"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "created"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "10"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "title"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "11"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "latitude"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "12"
        "iceberg.field.optional" = "true"
      }
      type = "float"
    }
    columns {
      name    = "salary_min"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "13"
        "iceberg.field.optional" = "true"
      }
      type = "int"
    }
    columns {
      name    = "longitude"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "14"
        "iceberg.field.optional" = "true"
      }
      type = "float"
    }
    columns {
      name    = "contract_time"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "15"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "salary_max"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "16"
        "iceberg.field.optional" = "true"
      }
      type = "int"
    }
    columns {
      name    = "contract_type"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "17"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      name    = "extraction_time_utc"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "18"
        "iceberg.field.optional" = "true"
      }
      type = "timestamp"
    }
  }
}