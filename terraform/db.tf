resource "aws_db_instance" "winsanity_db" {
  allocated_storage      = 20
  db_name                = var.db_name
  engine                 = "postgres"
  engine_version         = "16.3"
  instance_class         = "db.t3.micro"
  
  username               = var.db_username
  password               = var.db_password
  
  parameter_group_name   = "default.postgres16"
  skip_final_snapshot    = true

  publicly_accessible    = false
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
}

