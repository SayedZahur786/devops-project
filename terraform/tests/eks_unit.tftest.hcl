# Unit tests for the EKS module configuration values.
# These run offline: the AWS provider is MOCKED, so no AWS account,
# credentials or cost are involved. terraform >= 1.7 required for mocks.

mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = {
      names = ["ap-south-1a", "ap-south-1b"]
    }
  }

  mock_resource "aws_iam_role" {
    defaults = {
      arn = "arn:aws:iam::123456789012:role/mock-role"
    }
  }
}

run "unit_config_values" {
  command = plan

  variables {
    region              = "ap-south-1"
    cluster_name        = "hackboard-eks"
    vpc_cidr            = "10.0.0.0/16"
    node_instance_type  = "t3.medium"
    node_desired_size   = 2
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR does not match var.vpc_cidr"
  }

  assert {
    condition     = length(aws_subnet.public) == 2 && length(aws_subnet.private) == 2
    error_message = "Expected 2 public and 2 private subnets"
  }

  assert {
    condition     = aws_subnet.public[0].cidr_block == "10.0.0.0/24"
    error_message = "First public subnet should be the first /24 of the VPC CIDR"
  }

  assert {
    condition     = aws_subnet.private[0].cidr_block == "10.0.10.0/24"
    error_message = "First private subnet should be cidrsubnet(vpc_cidr, 8, 10)"
  }

  assert {
    condition     = aws_subnet.public[0].map_public_ip_on_launch == true
    error_message = "Public subnets must auto-assign public IPs"
  }

  assert {
    condition     = aws_eks_cluster.main.version == "1.31"
    error_message = "EKS control plane version pin changed unexpectedly"
  }

  assert {
    condition     = aws_iam_role.eks_cluster.name == "hackboard-eks-cluster-role"
    error_message = "Cluster IAM role name mismatch"
  }
}

run "unit_scaling_and_tags" {
  command = plan

  variables {
    cluster_name      = "hackboard-eks"
    node_desired_size = 2
  }

  assert {
    condition     = aws_eks_node_group.main.scaling_config[0].desired_size == 2
    error_message = "Node group desired size should follow var.node_desired_size"
  }

  assert {
    condition     = aws_eks_node_group.main.scaling_config[0].min_size == 1 && aws_eks_node_group.main.scaling_config[0].max_size == 3
    error_message = "Node group scaling bounds should stay 1..3"
  }

  assert {
    condition     = contains(aws_eks_node_group.main.instance_types, "t3.medium") && length(aws_eks_node_group.main.instance_types) == 1
    error_message = "Node group instance type mismatch"
  }

  assert {
    condition     = aws_eks_cluster.main.tags["Project"] == "hackboard-capstone"
    error_message = "Cluster must carry the hackboard-capstone project tag"
  }

  assert {
    condition     = aws_subnet.public[0].tags["kubernetes.io/cluster/hackboard-eks"] == "shared"
    error_message = "Subnets must be tagged for the EKS cluster (load balancer discovery)"
  }
}
