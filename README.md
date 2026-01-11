# AKS Guardrails Incident Lab (Senior • Azure • Terraform)

This repo is a **hands-on incident lab**: you get an intentionally imperfect AKS platform stack plus a deterministic guardrail that points to what’s missing.

- **Topic:** Containers (AKS / Kubernetes)
- **IaC:** Terraform
- **Guardrail:** `guardrail unmet: cluster telemetry missing` (multi-signal, offline-safe)
- **Catalog scenario ID:** `cat-k8s-inc-0066-azure-tf`

## Scenario context (sanitized)
These are **abstract** incident patterns used to shape symptoms and evidence expectations (no real customer data, no IDs).

- 2019-2024 • Containers • Senior — Admission control webhook recursion + autoscaler thrash driving API server saturation
- 2018-2025 • Containers • Senior — DNS resolution amplification (ndots/search) causing CoreDNS pressure and cascading retries

## What you’re practicing
You’re acting as the on-call senior engineer for a platform team running AKS in two Azure regions (`uksouth` primary, `westeurope` secondary).

Your goal is to make the platform “production-credible” by closing gaps around:
- **cluster addon/telemetry config**
- **log/metrics destination**
- **diagnostic setting binding evidence**
- **cluster access scope evidence**
- and the network “plumbing” required for resilient operations (reverse links + route associations)

(Those phrases are also the evidence tokens you should capture in your write-up.)

## Quick start (local)

### 1) Terraform sanity checks (no backend)
```bash
cd senior/terraform
terraform fmt -check
terraform init -backend=false
terraform validate
```

### 2) Run guardrails locally
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 scripts/guardrails/run.py
```

Expected (initial) result: the runner exits non-zero with:
- `guardrail unmet: cluster telemetry missing`
- an `issues:` line with aggregated counts (no file paths)

## Your tasks
Start here: **`senior/tasks.md`**.

## Notes
- The guardrail is intentionally **config-inspection** (offline-safe); it does not contact Azure.
- Terraform applies are not required to complete the exercise—use `terraform validate` and guardrail output as your “gates”.

---

Follow on LinkedIn: https://www.linkedin.com/in/lam-ai
