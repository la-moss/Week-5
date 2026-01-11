#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

FAIL = "guardrail unmet: cluster telemetry missing"
PASS = "guardrail met"

def main() -> int:
    root_arg = os.environ.get("IAC_ROOT", "senior/terraform")
    root = Path(root_arg)

    if not root.exists():
        print(FAIL)
        print("issues: iac_path_missing=1")
        return 1

    texts = []
    for tf in sorted(root.rglob("*.tf")):
        try:
            texts.append(tf.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
    text = "\n".join(texts)

    cluster_missing = 0
    telemetry_missing = 0
    diagnostic_binding_missing = 0
    reverse_link_missing = 0
    route_assoc_missing = 0
    tags_missing = 0

    # cluster present
    if re.search(r'resource\s+\"(azurerm_kubernetes_cluster|aws_eks_cluster|google_container_cluster)\"', text, re.I) is None:
        cluster_missing = 1

    # telemetry primitives present
    if re.search(r"azurerm_monitor_diagnostic_setting|azurerm_log_analytics_workspace|aws_cloudwatch_|google_logging_|google_monitoring_", text, re.I) is None:
        telemetry_missing = 1

    # diagnostic binding to cluster (per diagnostic setting block, not cross-file)
    diag_blocks = list(
        re.finditer(
            r'resource\s+\"azurerm_monitor_diagnostic_setting\"\s+\"[^\\\"]+\"\s*\{(.*?)\}',
            text,
            re.S | re.I,
        )
    )
    if diag_blocks:
        bound = False
        for m in diag_blocks:
            block = m.group(1)
            if re.search(r"target_resource_id\s*=.*kubernetes_cluster", block, re.I):
                bound = True
                break
        if not bound:
            diagnostic_binding_missing = 1
    else:
        diagnostic_binding_missing = 1

    # reverse links/peerings/routes between primary/secondary (require both directions)
    primary_to_secondary = re.search(r"remote_virtual_network_id\s*=.*(secondary|sec)", text, re.S | re.I)
    secondary_to_primary = (
        re.search(r"provider\s*=\s*azurerm\.secondary[\s\S]*?remote_virtual_network_id", text, re.I)
        or re.search(r"remote_virtual_network_id\s*=.*(primary|pri)", text, re.S | re.I)
    )
    if not (primary_to_secondary and secondary_to_primary):
        reverse_link_missing = 1

    # route table association for spokes
    if re.search(r"azurerm_subnet_route_table_association", text, re.I) is None:
        route_assoc_missing = 1

    # tags (Owner and CostCenter)
    if not (re.search(r"\bOwner\b", text, re.I) and re.search(r"CostCenter", text, re.I)):
        tags_missing = 1

    if any([cluster_missing, telemetry_missing, diagnostic_binding_missing, reverse_link_missing, route_assoc_missing, tags_missing]):
        print(FAIL)
        print(
            f"issues: cluster_missing={cluster_missing}, telemetry_missing={telemetry_missing}, "
            f"diagnostic_binding_missing={diagnostic_binding_missing}, reverse_link_missing={reverse_link_missing}, "
            f"route_assoc_missing={route_assoc_missing}, tags_missing={tags_missing}"
        )
        return 1

    print(PASS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
