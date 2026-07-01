terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Use the requested AWS region.
provider "aws" {
  region = var.aws_region
}

# Pick the latest Amazon Linux 2023 x86_64 AMI published by Amazon.
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Minimal VPC for a single public EC2 instance.
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# One public subnet in the first available Availability Zone.
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet"
  }
}

# Availability Zone lookup keeps the subnet portable inside us-east-1.
data "aws_availability_zones" "available" {
  state = "available"
}

# Internet access for the public subnet.
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public route table with a default route to the internet gateway.
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Attach the route table to the public subnet.
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security group for SSH, WireGuard, and ping.
resource "aws_security_group" "instance" {
  name        = "${var.project_name}-sg"
  description = "Allow SSH from your IP, WireGuard, and ICMP ping"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH from your IP only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    description = "WireGuard VPN"
    from_port   = 51820
    to_port     = 51820
    protocol    = "udp"
    cidr_blocks = [var.wireguard_allowed_cidr]
  }

  ingress {
    description = "ICMP ping"
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = [var.icmp_allowed_cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# Single low-cost public EC2 instance. No NAT Gateway, Load Balancer, or RDS.
resource "aws_instance" "main" {
  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.instance.id]
  associate_public_ip_address = true
  key_name                    = var.key_name

  tags = {
    Name = "${var.project_name}-instance"
  }
}
