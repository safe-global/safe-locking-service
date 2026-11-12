provider "aws" {
  region = "eu-central-1"
}

provider "vault" {
  address          = var.vault_addr
  skip_child_token = true
}

provider "onepassword" {}
