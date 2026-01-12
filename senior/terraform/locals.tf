locals {
  tags = {
    Owner      = var.owner
    CostCenter = var.cost_center
    env        = var.env
    project    = var.project_name
  }
}
