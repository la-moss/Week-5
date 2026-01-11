variable "project_name" { type = string }
variable "env" { type = string }
variable "location" { type = string }
variable "resource_group_name" { type = string }

variable "subnet_id" { type = string }
variable "kubernetes_version" { type = string }
variable "node_count" { type = number }

variable "log_analytics_workspace_id" { type = string }

variable "tags" { type = map(string) }
