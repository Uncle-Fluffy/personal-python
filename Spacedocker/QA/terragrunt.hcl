terraform {
  source = "git::ssh://${get_env("BITBUCKET_USER")}@bitbucket.org/exp-realty/exp-tf-modules.git//provider/aws/modules/pipeline/sam?ref=v3.11.1"
}

include {
  path = find_in_parent_folders()
}

locals {
  constants = merge(
  yamldecode(file(find_in_parent_folders("constants.yaml"))),
  yamldecode(file(find_in_parent_folders("region.yaml"))),
  yamldecode(file(find_in_parent_folders("env.yaml")))
  )
}

inputs = {
  name = "${local.constants.name}-sam-pipeline"
  template = file("buildspec.yml")
  vars = {
    ADD_UPDATE_OFFICE_EXECUTION_ROLE_NAME = "AddUpdateLambda-execution_role"
    ADD_UPDATE_OFFICE_LAMBDA_NAME = "AddUpdateOffice"
    API_GATEWAY_NAME = "spacedocker-restapi"
    API_STAGE_NAME = "v1"
    AUTH_FUNCTION_NAME = "oauth-token-authorizer"
    BUCKET_NAME = "spacedocker-qa-static-assets"
    CAPABILITIES = "CAPABILITY_NAMED_IAM"
    DATA_MIGRATION_BUCKET_NAME = "enterprise-exported-data-exp-qa"
    DB_INSTANCE_CLASS = "db.t3.medium"
    DB_INSTANCE_IDENTIFIER = "spacedocker-qa"
    DB_NAME = local.constants.name
    DB_PASSWORD = "TestPassword1"
    DB_SECURITY_GROUP_NAME = "spacedocker_rds_sg"
    DB_USERNAME = "postgres"
    ENV = local.constants.env
    IMPORT_ROLE_NAME = "Spacedocker-DataImport"
    LAMBDA_FUNCTION_NAME = "SpaceDocker-backend-stream"
    LAMBDA_FUNCTION_ROLE_NAME = "spacedocker-lambdaExecutionRole"
    LAMBDA_SECURITY_GROUP_NAME = "spacedocker-lambda-sg"
    LAMBDA_VPC_ENDPOINT_OVERRIDE = ""
    LAMBDA_VPC_ENDPOINT_SERVICE_NAME = "com.amazonaws.us-east-1.lambda"
    LOCAL_API_GATEWAY_NAME = "spacedocker-restapi-local"
    LOCAL_AUTH_FUNCTION_NAME = "oauth-token-authorizer-local"
    LOCAL_OKTA_CLIENT_ID = "0oaz4invq6GYgXdkP0h7"
    LOCAL_OKTA_DOMAIN = "exprealty.oktapreview.com"
    OKTA_CLIENT_ID = "0oa11hlve4azvW7MA0h8"
    OKTA_DOMAIN = "exprealty.oktapreview.com"
    PUBLIC_API_GATEWAY_NAME = "spacedocker-public-api"
    PUBLIC_API_STAGE_NAME = "rest"
    PUBLIC_USAGE_PLAN_NAME = "spacedocker-basic"
    QUEUE_NAME = "spacedocker-addUpdateOfficeQueue"
    REGION = "us-east-1"
    S3_BUCKET = "aws-sam-cli-managed-default-samclisourcebucket-1d271vn4h23qj" # this is the same for all QA SAM apps in the us-east-1 region
    S3_PREFIX = local.constants.name
    SQS_DISPATCH_FUNCTION_NAME = "SpaceDockerSQSDispatcher"
    SQS_VPC_ENDPOINT_OVERRIDE = ""
    STACK_NAME = local.constants.name
    SUBNET_1A_ID = "subnet-039776cbd0bf2b10a"
    SUBNET_1B_ID = "subnet-056523ef718b2ef76"
    SUBNET_1C_ID = "subnet-060e86e6226447837"
    TRANSIT_GATEWAY_ID = "tgw-050bd803119b5c36b"
    VPC_ENDPOINT_SERVICE_NAME = "com.amazonaws.us-east-1.sqs"
    VPC_ID = "vpc-0c9b9e01573e3b796"
  }
  policy_description = "${local.constants.name}-sam-pipeline"
  assume_role_policy = file("role.json")
  policy = file("policy.json")
  environment_compute_type = "BUILD_GENERAL1_MEDIUM"
  namespace = "exp"
  artifact_store_location = "exp-codepipeline-qa"  # this is the same for all QA pipelines in the us-east-1 region
  connection_arn = "arn:aws:codestar-connections:us-east-1:427827735592:connection/5d633cba-e882-4871-b8b8-a6bff8d6ec11" # this is the same for all QA pipelines in the us-east-1 region
  full_repository_id = "exp-realty/spacedocker"
  branch_name = "acceptance"
}
