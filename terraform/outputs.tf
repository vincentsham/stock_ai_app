output "public_subnets" {
  value = module.vpc.public_subnets
}

output "db_sg_id" {
  value = aws_security_group.db_sg.id
}