output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.rg.name
}

# GitHub repository variable: ACR_NAME
output "acr_name" {
  description = "GitHub repository variable ACR_NAME"
  value       = azurerm_container_registry.acr.name
}

# GitHub repository variable: ACR_LOGIN_SERVER
output "acr_login_server" {
  description = "GitHub repository variable ACR_LOGIN_SERVER"
  value       = azurerm_container_registry.acr.login_server
}

# GitHub repository variable: AKS_RESOURCE_GROUP
output "aks_resource_group" {
  description = "GitHub repository variable AKS_RESOURCE_GROUP"
  value       = azurerm_resource_group.rg.name
}

# GitHub repository variable: AKS_CLUSTER_NAME
output "aks_cluster_name" {
  description = "GitHub repository variable AKS_CLUSTER_NAME"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "storage_account_name" {
  description = "Name of the Azure Storage Account"
  value       = azurerm_storage_account.storage_account.name
}

# Environment secret: AZURE_STORAGE_CONNECTION_STRING
output "storage_connection_string" {
  description = "Environment secret AZURE_STORAGE_CONNECTION_STRING"
  value       = azurerm_storage_account.storage_account.primary_connection_string
  sensitive   = true
}

output "subscription_id" {
  description = "Subscription the resources were created in"
  value       = split("/", azurerm_resource_group.rg.id)[2]
}

output "aks_get_credentials_command" {
  description = "Azure CLI command used to configure kubectl"
  value = join(" ", [
    "az aks get-credentials",
    "--resource-group",
    azurerm_resource_group.rg.name,
    "--name",
    azurerm_kubernetes_cluster.aks.name,
    "--overwrite-existing"
  ])
}
