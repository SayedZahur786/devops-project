terraform {
  required_version = ">= 1.6"
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.9"
    }
  }
}

# Local Kubernetes cluster via kind (Kubernetes IN Docker).
# Same Terraform workflow as the AWS EKS module in ../terraform,
# against a free local cluster instead of paid AWS infrastructure.
resource "kind_cluster" "hackboard" {
  name            = var.cluster_name
  wait_for_ready  = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control_plane"
    }
  }
}

variable "cluster_name" {
  description = "Name of the local kind cluster"
  type        = string
  default     = "hackboard-local"
}

output "cluster_name" {
  value = kind_cluster.hackboard.name
}

output "kubeconfig_path" {
  value = kind_cluster.hackboard.kubeconfig_path
}

output "cluster_endpoint" {
  value = kind_cluster.hackboard.endpoint
}
