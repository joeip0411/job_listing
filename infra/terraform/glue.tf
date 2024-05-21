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

# resource "aws_glue_catalog_table" "brz__job_listing" {
#   catalog_id    = jsonencode(654654412098)
#   database_name = "job"
#   description   = null
#   name          = "brz__job_listing"
#   owner         = null
#   parameters = {
#     previous_metadata_location = "s3://joeip-data-engineering-iceberg-test/job.db/brz__job_listing/metadata/00042-4cc545b0-1e79-4086-b899-1bee44460c05.metadata.json"
#   }
#   retention          = 0
#   table_type         = "EXTERNAL_TABLE"
#   view_expanded_text = null
#   view_original_text = null
#   storage_descriptor {
#     bucket_columns            = []
#     compressed                = false
#     input_format              = null
#     location                  = "s3://joeip-data-engineering-iceberg-test/job.db/brz__job_listing"
#     number_of_buckets         = 0
#     output_format             = null
#     parameters                = {}
#     stored_as_sub_directories = false
#     columns {
#       comment = null
#       name    = "description"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "1"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "id"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "2"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "location"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "3"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "redirect_url"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "4"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "salary_is_predicted"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "5"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "company"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "6"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "__class__"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "7"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "adref"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "8"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "category"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "9"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "created"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "10"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "title"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "11"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "latitude"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "12"
#         "iceberg.field.optional" = "true"
#       }
#       type = "float"
#     }
#     columns {
#       comment = null
#       name    = "salary_min"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "13"
#         "iceberg.field.optional" = "true"
#       }
#       type = "int"
#     }
#     columns {
#       comment = null
#       name    = "longitude"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "14"
#         "iceberg.field.optional" = "true"
#       }
#       type = "float"
#     }
#     columns {
#       comment = null
#       name    = "contract_time"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "15"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "salary_max"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "16"
#         "iceberg.field.optional" = "true"
#       }
#       type = "int"
#     }
#     columns {
#       comment = null
#       name    = "contract_type"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "17"
#         "iceberg.field.optional" = "true"
#       }
#       type = "string"
#     }
#     columns {
#       comment = null
#       name    = "extraction_time_utc"
#       parameters = {
#         "iceberg.field.current"  = "true"
#         "iceberg.field.id"       = "18"
#         "iceberg.field.optional" = "true"
#       }
#       type = "timestamp"
#     }
#   }
# }

# import {
#   to = aws_glue_catalog_table.brz__job_listing
#   id = format("%s:%s:%s", var.aws_account_id, var.glue_database_name, "brz__job_listing")
# }