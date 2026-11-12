module "safe_rds" {
  source = "git::https://github.com/safe-global/terraform-aws-safe-network.git?ref=v2.9.0"

  vpc_id = data.aws_vpc.this.id

  aurora = {
    engine_version = "17.9"
    cluster_family = "aurora-postgresql17"
    cluster_size   = 1
    min_capacity   = 0.5
    max_capacity   = 4

    db_name       = "mainnet_safe_locking_service"
    db_admin_user = "mainnet_safe_locking_service_admin"

    subnets = data.aws_db_subnet_group.private.subnet_ids

    allowed_ingress_security_group_ids = [for sg in data.aws_security_group.allowed_ingress : sg.id]

    storage_encrypted   = true
    deletion_protection = var.deletion_protection
    skip_final_snapshot = var.skip_final_snapshot

    monitoring_role_arn = data.aws_iam_role.rds_monitoring_role.arn

    zone_id          = data.aws_route53_zone.db_safe_internal.zone_id
    cluster_dns_name = "safe-locking-service"
  }

  vault = {
    mount = "kv"
    path  = "aurora/safe-locking-service"
  }

  onepassword = {
    vault = data.onepassword_vault.db_credentials.uuid
  }

  context = module.this.context
}
