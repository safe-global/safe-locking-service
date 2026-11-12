module "terraform_state_backend" {
  source  = "cloudposse/tfstate-backend/aws"
  version = "1.8.0"

  namespace             = "safe"
  stage                 = var.state_backend_stage
  name                  = var.state_backend_name
  attributes            = ["state"]
  dynamodb_enabled      = false
  s3_state_lock_enabled = true

  prevent_unencrypted_uploads = false

  terraform_backend_config_file_path = ""
  force_destroy                      = false
}
