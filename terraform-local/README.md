# terraform-local - free local Kubernetes with Terraform

Same Terraform workflow as the AWS EKS module in `../terraform`, applied to a
free local kind (Kubernetes IN Docker) cluster. Requires: docker, terraform,
kind, kubectl.

    terraform init
    terraform plan
    terraform apply -auto-approve
    kubectl get nodes
    terraform destroy -auto-approve
