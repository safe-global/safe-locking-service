namespace   = "safe"
name        = "locking-service"
environment = "production"

tags = {
  "safe.local/service" = "safe-locking-service"
  "safe.local/project" = "safe-locking-service"
}

vpc_name             = "eks-safe-production-vpc"
db_subnet_group_name = "eks-cluster-private"

allowed_ingress_security_group_names = [
  "eks-cluster-sg-eks-safe-production-927325767",
  "production-vpn-vpn-sg",
  "production-ci-vpn-vpn-sg",
  "eks-pod-datadog-agent-clusterchecks",
]

onepassword_vault_name = "Database Creds"

deletion_protection = true
skip_final_snapshot = false

state_backend_stage = "production"
state_backend_name  = "locking-service"
