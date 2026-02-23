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

  publicly_accessible    = true
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
}

resource "aws_security_group" "db_sg" {
  name        = "winsanity-db-sg"
  description = "Allow inbound traffic from within the VPC and self"
  vpc_id      = module.vpc.vpc_id

  # Rule 1: Allow traffic from the VPC CIDR (Standard)
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  # Rule 2: THE CRITICAL FIX - Allow the group to trust its own members
  # This matches the manual rule you just saved in the console.
  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"
    self      = true 
  }

  # Rule 3: Allow your agent to talk to the internet (OpenAI, Gemini)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group_rule" "allow_my_mac" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = ["142.198.248.69/32"]
  security_group_id = aws_security_group.db_sg.id 
}

