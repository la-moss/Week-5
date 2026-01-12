output "resource_group_name" {
  value = module.network.resource_group_name
}

output "aks_cluster_id" {
  value = module.aks.aks_cluster_id
}

output "log_analytics_workspace_id" {
  value = module.monitoring.log_analytics_workspace_id
}
