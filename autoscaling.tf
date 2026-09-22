resource "aws_launch_template" "phonebook" {
  name_prefix            = "${var.project_name}-lt-"
  image_id               = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.app.id]

  user_data = base64encode(templatefile("${path.module}/userdata.sh.tftpl", {
    repo_url       = var.repo_url
    db_host        = aws_db_instance.phonebook.address
    db_port        = aws_db_instance.phonebook.port
    db_user        = var.db_username
    db_password    = var.db_password
    db_name        = var.db_name
    app_port       = var.app_port
    developer_name = "Yazen Albu"
  }))

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name = "Web Server of Yazen Phonebook App"
    }
  }

  depends_on = [aws_db_instance.phonebook]
}

resource "aws_autoscaling_group" "phonebook" {
  name                      = "${var.project_name}-asg"
  min_size                  = var.min_size
  max_size                  = var.max_size
  desired_capacity          = var.desired_capacity
  health_check_type         = "ELB"
  health_check_grace_period = 300

  vpc_zone_identifier = data.aws_subnets.default.ids
  target_group_arns   = [aws_lb_target_group.phonebook.arn]

  launch_template {
    id      = aws_launch_template.phonebook.id
    version = "$Latest"
  }

  depends_on = [aws_lb_listener.http]

  tag {
    key                 = "Name"
    value               = "Web Server of Yazen Phonebook App"
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_policy" "cpu_target" {
  name                   = "${var.project_name}-cpu-target"
  autoscaling_group_name = aws_autoscaling_group.phonebook.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }

    target_value = 50
  }
}
