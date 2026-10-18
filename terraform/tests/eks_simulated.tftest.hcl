# Simulated EKS deployment test.
# The AWS provider is MOCKED: terraform plans and "applies" the whole module
# against generated values, so this simulates a real `terraform apply` of the
# VPC + EKS stack with no AWS account, no credentials and no cost.
# terraform >= 1.7 required for mocks.

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

run "simulated_apply_defaults" {
  command = apply

  assert {
    condition     = output.cluster_name == "hackboard-eks"
    error_message = "Cluster name output mismatch after simulated apply"
  }

  assert {
    condition     = output.configure_kubectl == "aws eks update-kubeconfig --region ap-south-1 --name hackboard-eks"
    error_message = "kubectl bootstrap command output mismatch"
  }

  assert {
    condition     = aws_eks_cluster.main.name == "hackboard-eks"
    error_message = "EKS cluster was not created with the expected name"
  }

  assert {
    condition     = aws_eks_node_group.main.cluster_name == aws_eks_cluster.main.name
    error_message = "Node group is not attached to the cluster"
  }
}

run "simulated_apply_custom" {
  command = apply

  variables {
    cluster_name       = "hackboard-eks-prod"
    region             = "us-east-1"
    node_desired_size  = 3
    node_instance_type = "t3.large"
  }

  assert {
    condition     = output.cluster_name == "hackboard-eks-prod"
    error_message = "Cluster name output should follow var.cluster_name"
  }

  assert {
    condition     = aws_eks_node_group.main.scaling_config[0].desired_size == 3
    error_message = "Desired size should follow var.node_desired_size"
  }

  assert {
    condition     = contains(aws_eks_node_group.main.instance_types, "t3.large")
    error_message = "Instance type should follow var.node_instance_type"
  }
}
