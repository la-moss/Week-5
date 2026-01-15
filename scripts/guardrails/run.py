#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

try:
    import hcl2  # type: ignore
except Exception:  # pragma: no cover - runtime import check
    hcl2 = None

FAIL = "guardrail unmet: cluster telemetry missing"
PASS = "guardrail met"

def _read_tf_files(root: Path) -> tuple[list[str], list[dict]]:
    texts: list[str] = []
    parsed: list[dict] = []
    for tf in sorted(root.rglob("*.tf")):
        try:
            content = tf.read_text(encoding="utf-8", errors="ignore")
            texts.append(content)
            if hcl2 is None:
                continue
            try:
                parsed.append(hcl2.loads(content))
            except Exception:
                # Skip invalid/partial files but keep raw text for regex fallback
                continue
        except Exception:
            continue
    return texts, parsed


def _flatten_resources(parsed: list[dict]) -> list[tuple[str, str, dict]]:
    resources: list[tuple[str, str, dict]] = []
    for doc in parsed:
        for block in doc.get("resource", []):
            for resource_type, instances in block.items():
                for name, body in instances.items():
                    resources.append((resource_type, name, body))
    return resources


def _expr_contains_cluster(expr) -> bool:
    if expr is None:
        return False
    if isinstance(expr, str):
        return "kubernetes_cluster" in expr or "aks_cluster_id" in expr
    if isinstance(expr, list):
        return any(_expr_contains_cluster(item) for item in expr)
    if isinstance(expr, dict):
        for key, value in expr.items():
            if key == "resource" and isinstance(value, list) and value:
                if "kubernetes_cluster" in value[0]:
                    return True
            if key == "module" and isinstance(value, list):
                # common pattern: module.aks.aks_cluster_id
                if any("aks" in part and "cluster" in part for part in value):
                    return True
            if _expr_contains_cluster(value):
                return True
    return False


def _extract_vnet_ref(expr) -> str | None:
    if isinstance(expr, dict) and "resource" in expr:
        value = expr.get("resource")
        if isinstance(value, list) and len(value) >= 2:
            res_type, res_name = value[0], value[1]
            if res_type == "azurerm_virtual_network":
                return res_name
    if isinstance(expr, str) and "azurerm_virtual_network" in expr:
        return expr
    return None


def _has_reverse_peering(resources: list[tuple[str, str, dict]], text: str) -> bool:
    peerings = []
    for resource_type, _, body in resources:
        if resource_type != "azurerm_virtual_network_peering":
            continue
        local_ref = _extract_vnet_ref(body.get("virtual_network_name"))
        remote_ref = _extract_vnet_ref(body.get("remote_virtual_network_id"))
        if local_ref and remote_ref:
            peerings.append((local_ref, remote_ref))
    if peerings:
        return any((b, a) in peerings for a, b in peerings)
    # fallback to regex if we couldn't resolve structured refs
    primary_to_secondary = re.search(r"remote_virtual_network_id\s*=.*(secondary|sec)", text, re.S | re.I)
    secondary_to_primary = (
        re.search(r"provider\s*=\s*azurerm\.secondary[\s\S]*?remote_virtual_network_id", text, re.I)
        or re.search(r"remote_virtual_network_id\s*=.*(primary|pri)", text, re.S | re.I)
    )
    return bool(primary_to_secondary and secondary_to_primary)


def _tags_present(parsed: list[dict], text: str) -> bool:
    # Check structured tags in resources/locals first
    for doc in parsed:
        for locals_block in doc.get("locals", []):
            if isinstance(locals_block, dict):
                for _, val in locals_block.items():
                    if isinstance(val, dict) and {"Owner", "CostCenter"} <= set(val.keys()):
                        return True
        for block in doc.get("resource", []):
            for _, instances in block.items():
                for _, body in instances.items():
                    tags = body.get("tags")
                    if isinstance(tags, dict) and {"Owner", "CostCenter"} <= set(tags.keys()):
                        return True
    # Fallback to regex for legacy text-only configs
    return bool(re.search(r"\bOwner\b", text, re.I) and re.search(r"CostCenter", text, re.I))


def main() -> int:
    root_arg = os.environ.get("IAC_ROOT", "senior/terraform")
    root = Path(root_arg)

    if not root.exists():
        print(FAIL)
        print("issues: iac_path_missing=1")
        return 1

    texts, parsed = _read_tf_files(root)
    text = "\n".join(texts)
    resources = _flatten_resources(parsed)

    cluster_missing = 0
    telemetry_missing = 0
    diagnostic_binding_missing = 0
    reverse_link_missing = 0
    route_assoc_missing = 0
    tags_missing = 0

    # cluster present
    if any(
        r_type in {"azurerm_kubernetes_cluster", "aws_eks_cluster", "google_container_cluster"}
        for r_type, _, _ in resources
    ) is False and re.search(
        r'resource\s+\"(azurerm_kubernetes_cluster|aws_eks_cluster|google_container_cluster)\"',
        text,
        re.I,
    ) is None:
        cluster_missing = 1

    # telemetry primitives present
    telemetry_resource_present = any(
        r_type == "azurerm_monitor_diagnostic_setting"
        or r_type == "azurerm_log_analytics_workspace"
        or r_type.startswith("aws_cloudwatch")
        or r_type.startswith("google_logging")
        or r_type.startswith("google_monitoring")
        for r_type, _, _ in resources
    )
    if not telemetry_resource_present and re.search(
        r"azurerm_monitor_diagnostic_setting|azurerm_log_analytics_workspace|aws_cloudwatch_|google_logging_|google_monitoring_",
        text,
        re.I,
    ) is None:
        telemetry_missing = 1

    # diagnostic binding to cluster (per diagnostic setting block, not cross-file)
    diag_settings = [body for r_type, _, body in resources if r_type == "azurerm_monitor_diagnostic_setting"]
    if diag_settings:
        bound = False
        for body in diag_settings:
            if _expr_contains_cluster(body.get("target_resource_id")):
                bound = True
                break
        if not bound:
            # fallback regex for edge cases
            if re.search(r"target_resource_id\s*=.*(kubernetes_cluster|aks_cluster_id)", text, re.I) is None:
                diagnostic_binding_missing = 1
    else:
        # no structured diagnostics found; fallback to regex scan
        diag_block = re.search(
            r'resource\s+"azurerm_monitor_diagnostic_setting"\s+"[^\\"]+"\s*\{(.*?)\}',
            text,
            re.S | re.I,
        )
        if diag_block and re.search(
            r"target_resource_id\s*=.*(kubernetes_cluster|aks_cluster_id)",
            diag_block.group(1),
            re.I,
        ):
            diagnostic_binding_missing = 0
        else:
            diagnostic_binding_missing = 1

    # reverse links/peerings/routes between primary/secondary (require both directions)
    if not _has_reverse_peering(resources, text):
        reverse_link_missing = 1

    # route table association for spokes
    if any(r_type == "azurerm_subnet_route_table_association" for r_type, _, _ in resources) is False and re.search(
        r"azurerm_subnet_route_table_association",
        text,
        re.I,
    ) is None:
        route_assoc_missing = 1

    # tags (Owner and CostCenter)
    if not _tags_present(parsed, text):
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
