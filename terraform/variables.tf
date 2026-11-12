variable "vpc_name" {
  description = "Name tag of the VPC where the Aurora cluster and its security group live"
  type        = string
}

variable "db_subnet_group_name" {
  description = "Existing RDS DB subnet group whose subnets host the Aurora cluster"
  type        = string
}

variable "allowed_ingress_security_group_names" {
  description = "Names of the security groups allowed to reach the Aurora cluster on 5432: the EKS nodes running the app, the VPNs and the Datadog DBM clusterchecks pod"
  type        = list(string)
}

variable "vault_addr" {
  description = "Vault server address"
  type        = string
}

variable "onepassword_vault_name" {
  description = "Name of the 1Password vault where DB credentials are stored"
  type        = string
}

variable "deletion_protection" {
  description = "Enable deletion protection on the Aurora cluster"
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Skip the final snapshot when the cluster is destroyed"
  type        = bool
  default     = false
}

variable "state_backend_stage" {
  description = "Stage name for the state backend bucket"
  type        = string
}

variable "state_backend_name" {
  description = "Name component for the state backend bucket"
  type        = string
}
