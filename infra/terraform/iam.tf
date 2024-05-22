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