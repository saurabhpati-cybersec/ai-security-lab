# Day 1 Deliverable: Completed Threat Model

Complete `docs/threat-model.md` with:

- 15+ threats (T-01..T-NN) each tagged with:
  - STRIDE category (Spoofing / Tampering / Repudiation / Info Disclosure / Denial of Service / Elevation of Privilege)
  - OWASP LLM 2025 mapping (LLM01:2025 through LLM10:2025)
  - OWASP Agentic mapping (AAA-01 through AAA-10)
  - Trifecta legs (data / untrusted_input / egress)
  - Attack vector (concrete description of how the attack is executed)
  - Impact (what the attacker achieves)
  - Controls (which technical controls mitigate the threat)
  - Residual risk (qualitative: Low / Medium / High, with justification)
  - Lab reference (which day(s) demonstrate this threat)
- Trifecta matrix showing which threats activate which legs, identifying full-trifecta threats (all three legs active)
- Committed to git with message: `docs: complete threat model for reference agent`

## Verification

Run the eval to confirm:

```bash
python3 labs/day-01-threat-modeling/eval.py
```

Expected output:

```
PASS: 17 threats tagged with STRIDE/OWASP/trifecta
```
