variable "aws_region" {
  description = "AWS region where the infrastructure will be created."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix used for resource tags."
  type        = string
  default     = "multicloud-routing"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the single public subnet."
  type        = string
  default     = "10.0.1.0/24"
}

variable "my_ip_cidr" {
  description = "Your public IP address in CIDR format for SSH access, for example 203.0.113.10/32."
  type        = string
}

variable "wireguard_allowed_cidr" {
  description = "CIDR block allowed to reach WireGuard UDP port 51820."
  type        = string
  default     = "0.0.0.0/0"
}

variable "icmp_allowed_cidr" {
  description = "CIDR block allowed to ping the instance."
  type        = string
  default     = "0.0.0.0/0"
}

variable "instance_type" {
  description = "EC2 instance type for the Amazon Linux 2023 instance."
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Optional existing EC2 key pair name for SSH login."
  type        = string
  default     = null
}
