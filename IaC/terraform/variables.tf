variable "project_name" {
  type        = string
  description = "Project/cluster prefix."
  default     = "orion"
}

variable "env" {
  type        = string
  description = "Environment name."
  default     = "prod"
}

variable "location_primary" {
  type        = string
  description = "Primary Azure region."
  default     = "uksouth"
}

variable "location_dr" {
  type        = string
  description = "DR/secondary Azure region."
  default     = "westeurope"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
  default     = "rg-orion-aks-prod"
}

# Non-empty defaults (still overridable via tfvars)
variable "owner" {
  type        = string
  description = "Chargeback / owning team."
  default     = "payments"
}

variable "cost_center" {
  type        = string
  description = "Chargeback cost center."
  default     = "1001"
}

variable "vnet_cidr_primary" {
  type        = string
  description = "CIDR for primary VNet."
  default     = "10.10.0.0/16"
}

variable "subnet_cidr_primary" {
  type        = string
  description = "CIDR for AKS subnet."
  default     = "10.10.1.0/24"
}

variable "vnet_cidr_dr" {
  type        = string
  description = "CIDR for DR/secondary VNet."
  default     = "10.20.0.0/16"
}

variable "kubernetes_version" {
  type        = string
  description = "AKS version (pin for predictability)."
  default     = "1.29.2"
}

variable "node_count" {
  type        = number
  description = "Default node count."
  default     = 3
}
