location            = "Australia East"
resource_group_name = "koalatech-week08-rg"

# Must be globally unique across all of Azure
acr_name             = "sit722week08"
storage_account_name = "sit722week08"

aks_cluster_name = "sit722-week08-aks"
aks_dns_prefix   = "koalatech"

# Three nodes: staging, production and the monitoring stack share the cluster
aks_node_count   = 3
aks_node_vm_size = "Standard_B4ms"

environment = "development"

tags = {
  Project     = "KoalaTech Course Platform"
  ManagedBy   = "Terraform"
  Practical   = "Week10"
  Environment = "Development"
}
