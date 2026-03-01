output "public_subnets" {
  value = module.vpc.public_subnets
}

output "db_sg_id" {
  value = aws_security_group.db_sg.id
}

output "web_sg_id" {
  value = aws_security_group.web_sg.id
}

output "alb_sg_id" {
  value = aws_security_group.alb_sg.id
}

output "alb_dns_name" {
  value       = aws_lb.web_alb.dns_name
  description = "Public URL of the web app (http://<dns>)"
}