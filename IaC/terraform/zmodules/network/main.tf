resource "azurerm_resource_group" "primary" {
  name     = var.resource_group_name
  location = var.location_primary
  tags     = var.tags
}

resource "azurerm_virtual_network" "primary" {
  name                = "vnet-${var.project_name}-${var.env}-primary"
  address_space       = [var.vnet_cidr_primary]
  location            = azurerm_resource_group.primary.location
  resource_group_name = azurerm_resource_group.primary.name
  tags                = var.tags
}

resource "azurerm_subnet" "aks" {
  name                 = "snet-aks"
  resource_group_name  = azurerm_resource_group.primary.name
  virtual_network_name = azurerm_virtual_network.primary.name
  address_prefixes     = [var.subnet_cidr_primary]
}

resource "azurerm_virtual_network" "dr" {
  name                = "vnet-${var.project_name}-${var.env}-dr"
  address_space       = [var.vnet_cidr_dr]
  location            = var.location_dr
  resource_group_name = azurerm_resource_group.primary.name
  tags                = var.tags
}

# Intentionally only one direction of peering is present (guardrail expects both directions)
resource "azurerm_virtual_network_peering" "primary_to_dr" {
  name                      = "peer-primary-to-dr"
  resource_group_name       = azurerm_resource_group.primary.name
  virtual_network_name      = azurerm_virtual_network.primary.name
  remote_virtual_network_id = azurerm_virtual_network.dr.id

  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = false
  use_remote_gateways          = false
}

resource "azurerm_route_table" "aks" {
  name                = "rt-${var.project_name}-${var.env}-aks"
  location            = azurerm_resource_group.primary.location
  resource_group_name = azurerm_resource_group.primary.name
  tags                = var.tags
}

resource "azurerm_route" "default_egress" {
  name                = "default-egress"
  resource_group_name = azurerm_resource_group.primary.name
  route_table_name    = azurerm_route_table.aks.name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = "Internet"
}

# Intentionally missing the subnet-to-route-table attachment resource (guardrail expects an explicit association)
