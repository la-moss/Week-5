# Senior tasks — AKS Guardrails Incident Lab

Catalog scenario ID: `cat-k8s-inc-0066-azure-tf`  
Guardrail failure string (must match CI/local): **`guardrail unmet: cluster telemetry missing`**

## Scenario context (sanitized)
- 2019-2024 • Containers • Senior — Admission control webhook recursion + autoscaler thrash driving API server saturation
- 2018-2025 • Containers • Senior — DNS resolution amplification (ndots/search) causing CoreDNS pressure and cascading retries

## Operating constraints
- Prove the symptom before any change.
- Keep blast radius low; smallest scope first.
- Document rollback before change.
- Terraform runs with `-backend=false` for this lab.

## Ticket 1 — Stop “telemetry drift” and unblock incident response
### Symptoms (what on-call sees)
- Platform dashboards are partially empty, and incident triage requires manual querying.
- An “AKS cluster telemetry” check fails in CI.

### What to do
1. Run the guardrail and capture its **before** output.
2. Produce evidence for:
   - **cluster addon/telemetry config**
   - **log/metrics destination**
   - **diagnostic setting binding evidence**
3. Fix the IaC so the diagnostic settings are **actually bound to the AKS cluster** (not “somewhere else”).
4. Re-run the guardrail and capture the **after** output.

### Acceptance criteria
- Guardrail reports `diagnostic_binding_missing=0`.
- Terraform `fmt` + `validate` succeed.

## Ticket 2 — Multi-region network hygiene for AKS platform dependencies
### Symptoms (what on-call sees)
- Failover drills are inconsistent; “secondary” can’t reliably reach required internal endpoints.
- Network paths appear asymmetric during debugging.

### What to do
1. Ensure the multi-region VNet connectivity is **bidirectional** (reverse link present).
2. Ensure subnets that need it are explicitly associated to a route table.
3. Capture evidence for:
   - **cluster access scope evidence** (how the cluster reaches dependencies / what networks it’s attached to)
   - the reverse link state (show what changed in config)

### Acceptance criteria
- Guardrail reports `reverse_link_missing=0` and `route_assoc_missing=0`.
- No additional broadening of access beyond what’s needed (keep changes minimal).

## Ticket 3 — Close the loop: document the incident-ready posture
### What to do
Create a short write-up (PR description or Issue submission) that includes:
- Guardrail output before/after
- Terraform validate output
- A short explanation of the changes and why they’re sufficient
- Rollback plan

## Helpful commands
```bash
cd senior/terraform
terraform fmt -check
terraform init -backend=false
terraform validate

# guardrails
cd ../../
python3 -m venv .venv
source .venv/bin/activate
python3 scripts/guardrails/run.py
```
