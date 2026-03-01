# ============================================================
# APPLICATION LOAD BALANCER
# ============================================================

resource "aws_lb" "web_alb" {
  name               = "winsanity-web-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets

  tags = {
    Name = "winsanity-web-alb"
  }
}

# Target Group — forwards traffic to ECS tasks on port 3000
resource "aws_lb_target_group" "web_tg" {
  name        = "winsanity-web-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip" # Required for Fargate (awsvpc)

  health_check {
    path                = "/"
    protocol            = "HTTP"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
    interval            = 30
    matcher             = "200-399"
  }

  tags = {
    Name = "winsanity-web-tg"
  }
}

# Listener — HTTP on port 80, forwards to the target group
resource "aws_lb_listener" "web_http" {
  load_balancer_arn = aws_lb.web_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_tg.arn
  }
}
