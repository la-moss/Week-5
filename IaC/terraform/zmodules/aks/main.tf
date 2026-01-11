resource "azurerm_kubernetes_cluster" "this" {
  name                = "aks-${var.project_name}-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "aks-${var.project_name}-${var.env}"

  kubernetes_version  = var.kubernetes_version

  identity {
    type = "SystemAssigned"
  }

  default_node_pool {
    name           = "system"
    node_count     = var.node_count
    vm_size        = "Standard_DS2_v2"
    vnet_subnet_id = var.subnet_id
    type           = "VirtualMachineScaleSets"
  }

  # Telemetry addon enabled (workspace exists), but diagnostics aren't bound to the cluster yet (see monitoring module).
  oms_agent {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  tags = var.tags
}
