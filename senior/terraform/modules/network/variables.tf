variable "project_name" { type = string }
variable "env" { type = string }
variable "resource_group_name" { type = string }

variable "location_primary" { type = string }
variable "location_dr" { type = string }

variable "vnet_cidr_primary" { type = string }
variable "subnet_cidr_primary" { type = string }
variable "vnet_cidr_dr" { type = string }

variable "tags" {
  type = map(string)
}
