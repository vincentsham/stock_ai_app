# ============================================================
# DATABASE SECURITY GROUP
# ============================================================

resource "aws_security_group" "db_sg" {
  name        = "winsanity-db-sg"
  description = "Allow inbound traffic from within the VPC and self"
  vpc_id      = module.vpc.vpc_id

  # Allow the group to trust its own members
  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"
    self      = true
  }

  # Allow outbound to the internet
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "winsanity-db-sg"
  }
}

# ============================================================
# ALB SECURITY GROUP
# ============================================================

resource "aws_security_group" "alb_sg" {
  name        = "winsanity-alb-sg"
  description = "Allow inbound HTTP/HTTPS to the ALB"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP from anywhere"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS from anywhere (for future TLS)"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "winsanity-alb-sg"
  }
}

# ============================================================
# WEB APP SECURITY GROUP
# ============================================================

resource "aws_security_group" "web_sg" {
  name        = "winsanity-web-sg"
  description = "Allow inbound from ALB on port 3000 and all outbound"
  vpc_id      = module.vpc.vpc_id

  # Only accept traffic from the ALB
  ingress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
    description     = "Allow traffic from ALB only"
  }

  # Allow all outbound (internet APIs, database, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "winsanity-web-sg"
  }
}

# Allow the web app SG to reach the database on port 5432
resource "aws_security_group_rule" "web_to_db" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.web_sg.id
  security_group_id        = aws_security_group.db_sg.id
  description              = "Allow web app tasks to reach the database"
}
