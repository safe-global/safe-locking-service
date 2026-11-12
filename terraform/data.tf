data "aws_vpc" "this" {
  tags = {
    Name = var.vpc_name
  }
}

data "aws_security_group" "allowed_ingress" {
  for_each = toset(var.allowed_ingress_security_group_names)

  vpc_id = data.aws_vpc.this.id
  name   = each.value
}

data "aws_db_subnet_group" "private" {
  name = var.db_subnet_group_name
}

data "aws_iam_role" "rds_monitoring_role" {
  name = "rds-monitoring-role"
}

data "aws_route53_zone" "db_safe_internal" {
  name         = "db.safe.internal"
  private_zone = true
  vpc_id       = data.aws_vpc.this.id
}

data "onepassword_vault" "db_credentials" {
  name = var.onepassword_vault_name
}
