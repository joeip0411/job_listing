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

resource "aws_glue_catalog_table" "stg__job_description_temp" {
  catalog_id    = jsonencode(654654412098)
  database_name = "job_dev"
  name          = "stg__job_description_temp"
  table_type    = "EXTERNAL_TABLE"

  open_table_format_input {
    iceberg_input {
      metadata_operation = "CREATE"
    }
  }

  storage_descriptor {

    location = "s3://joeip-data-engineering-iceberg-test/job_dev.db/stg__job_description_temp"

    columns {
      comment = null
      name    = "id"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "1"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      comment = null
      name    = "full_description"
      parameters = {
        "iceberg.field.current"  = "true"
        "iceberg.field.id"       = "2"
        "iceberg.field.optional" = "true"
      }
      type = "string"
    }
    columns {
      comment = null
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