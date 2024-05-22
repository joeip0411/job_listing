resource "aws_iam_user" "airflow" {
  name                 = "airflow"
  path                 = "/"
}

resource "aws_iam_policy" "airflow" {
  name        = "airflow"
  path        = "/"
  policy = jsonencode({
    Statement = [{
      Action   = [
        "glue:*", 
        "elasticmapreduce:*", 
        "athena:*", 
        "ec2:AuthorizeSecurityGroupIngress", 
        "ec2:RevokeSecurityGroupIngress", 
        "ecr:CompleteLayerUpload", 
        "ecr:GetAuthorizationToken", 
        "ecr:UploadLayerPart", 
        "ecr:InitiateLayerUpload", 
        "ecr:BatchCheckLayerAvailability", 
        "ecr:PutImage", 
        "ecs:*", 
        "iam:PassRole"]
      Effect   = "Allow"
      Resource = ["*"]
      Sid      = "airflow"
    }]
    Version = "2012-10-17"
  })
}

resource "aws_iam_user_policy_attachment" "airflow_policy_to_airflow_user" {
  policy_arn = aws_iam_policy.airflow.arn
  user       = aws_iam_user.airflow.name
}

resource "aws_iam_user_policy_attachment" "amazon_emr_role_to_airflow_user" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceRole"
  user       = aws_iam_user.airflow.name
}

resource "aws_iam_user_policy_attachment" "amazon_s3_full_access_to_airflow_user" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  user       = aws_iam_user.airflow.name
}

resource "aws_iam_role" "emr_service_role" {
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "elasticmapreduce.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
  description           = "Allows Elastic MapReduce to call AWS services such as EC2 on your behalf."
  force_detach_policies = false
  managed_policy_arns   = ["arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceRole"]
  max_session_duration  = 3600
  name                  = "EMR-service-role"
  name_prefix           = null
  path                  = "/"
}

resource "aws_iam_role_policy_attachment" "amazon_emr_role_to_emr_service_role" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceRole"
  role       = aws_iam_role.emr_service_role.name
}

resource "aws_iam_role" "emr_ec2_instance_profile" {
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
  description           = "Allows EC2 instances to call AWS services on your behalf."
  force_detach_policies = false
  managed_policy_arns   = [aws_iam_policy.emr_ec2_instance_profile_policy.arn]
  max_session_duration  = 3600
  name                  = "EMR-EC2-instance-profile"
  path                  = "/"
}

resource "aws_iam_policy" "emr_ec2_instance_profile_policy" {
  name        = "AmazonEMR-InstanceProfile-Policy-20240417T100616"
  path        = "/service-role/"
  policy = jsonencode({
    Statement = [
      {Action   = [
        "s3:AbortMultipartUpload", 
        "s3:CreateBucket", 
        "s3:DeleteObject", 
        "s3:GetBucketVersioning", 
        "s3:GetObject", 
        "s3:GetObjectTagging", 
        "s3:GetObjectVersion", 
        "s3:ListBucket", 
        "s3:ListBucketMultipartUploads", 
        "s3:ListBucketVersions", 
        "s3:ListMultipartUploadParts", 
        "s3:PutBucketVersioning", 
        "s3:PutObject", 
        "s3:PutObjectTagging"]
      Effect   = "Allow"
      Resource = ["arn:aws:s3:::*"]
      }, 
      {Action   = ["glue:*"]
      Effect   = "Allow"
      Resource = ["*"]
      Sid      = "OtherPermissions"
      }
    ]
    Version = "2012-10-17"
  })
}


