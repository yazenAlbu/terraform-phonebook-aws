variable "aws_region" {
  description = "AWS Region used by the project."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefix used for AWS resource names and tags."
  type        = string
  default     = "yazen-terraform-phonebook"
}

variable "instance_type" {
  description = "EC2 instance type used by the Auto Scaling Group."
  type        = string
  default     = "t3.micro"
}

variable "app_port" {
  description = "Port used by the Flask/Gunicorn application."
  type        = number
  default     = 5000
}

variable "desired_capacity" {
  description = "Desired number of EC2 instances."
  type        = number
  default     = 2
}

variable "min_size" {
  description = "Minimum number of EC2 instances."
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of EC2 instances."
  type        = number
  default     = 3
}

variable "db_name" {
  description = "MySQL database name."
  type        = string
  default     = "phonebook_db"
}

variable "db_username" {
  description = "MySQL master username."
  type        = string
  default     = "phonebookadmin"
}

variable "db_password" {
  description = "MySQL master password. Store it only in a local terraform.tfvars file."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 12 && can(regex("^[A-Za-z0-9!#%_*+=.:-]+$", var.db_password))
    error_message = "db_password must be at least 12 characters and use only letters, numbers, or ! # % _ * + = . : -. Do not use spaces, /, @, or double quotes."
  }
}

variable "db_instance_class" {
  description = "Amazon RDS instance class."
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GiB."
  type        = number
  default     = 20
}

variable "repo_url" {
  description = "Public GitHub repository cloned by EC2 user data."
  type        = string
  default     = "https://github.com/yazenAlbu/terraform-phonebook-aws.git"
}
