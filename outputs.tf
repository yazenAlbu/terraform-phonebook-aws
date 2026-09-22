output "website_url" {
  description = "Public URL of the phonebook application."
  value       = "http://${aws_lb.phonebook.dns_name}"
}

output "load_balancer_dns_name" {
  description = "Application Load Balancer DNS name."
  value       = aws_lb.phonebook.dns_name
}

output "autoscaling_group_name" {
  description = "Auto Scaling Group name."
  value       = aws_autoscaling_group.phonebook.name
}

output "database_endpoint" {
  description = "RDS endpoint used by the application."
  value       = aws_db_instance.phonebook.endpoint
  sensitive   = true
}
