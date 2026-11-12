output "cluster_endpoint" {
  description = "Aurora cluster writer endpoint"
  value       = module.safe_rds.cluster_endpoint
}

output "cluster_dns_name" {
  description = "Route53 DNS name for the Aurora cluster"
  value       = module.safe_rds.cluster_dns_name
}

output "cluster_database_name" {
  description = "Database name"
  value       = module.safe_rds.cluster_database_name
}

output "vault_admin_secret_path" {
  description = "Vault path holding the application (admin) DB credentials"
  value       = module.safe_rds.vault_admin_secret_path
}
