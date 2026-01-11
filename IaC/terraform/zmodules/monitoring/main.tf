resource "azurerm_log_analytics_workspace" "law" {
  name                = "law-${var.project_name}-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

# Intentionally NOT bound to the AKS cluster (guardrail expects a diagnostic setting targeting the kubernetes_cluster)
# This is a realistic failure mode: diagnostics exist, but not on the critical resource.
resource "azurerm_monitor_diagnostic_setting" "platform_diag" {
  name                       = "diag-platform"
  target_resource_id         = azurerm_log_analytics_workspace.law.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

  enabled_log {
    category = "AuditEvent"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}
