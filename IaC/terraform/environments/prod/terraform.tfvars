project_name        = "orion"
env                 = "prod"
location_primary    = "uksouth"
location_dr         = "westeurope"
resource_group_name = "rg-orion-aks-prod"

owner       = "payments"
cost_center = "1001"

vnet_cidr_primary   = "10.10.0.0/16"
subnet_cidr_primary = "10.10.1.0/24"
vnet_cidr_dr        = "10.20.0.0/16"

kubernetes_version = "1.29.2"
node_count         = 3
