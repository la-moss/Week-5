module "network" {
  source = "./modules/network"

  project_name         = var.project_name
  env                  = var.env
  resource_group_name  = var.resource_group_name

  location_primary     = var.location_primary
  location_dr          = var.location_dr

  vnet_cidr_primary    = var.vnet_cidr_primary
  subnet_cidr_primary  = var.subnet_cidr_primary
  vnet_cidr_dr         = var.vnet_cidr_dr

  tags = local.tags
}

module "monitoring" {
  source = "./modules/monitoring"

  project_name         = var.project_name
  env                  = var.env
  resource_group_name  = module.network.resource_group_name
  location             = var.location_primary
  tags                 = local.tags
}

module "aks" {
  source = "./modules/aks"

  project_name         = var.project_name
  env                  = var.env
  location             = var.location_primary
  resource_group_name  = module.network.resource_group_name

  subnet_id            = module.network.aks_subnet_id
  kubernetes_version   = var.kubernetes_version
  node_count           = var.node_count

  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id

  tags = local.tags
}
