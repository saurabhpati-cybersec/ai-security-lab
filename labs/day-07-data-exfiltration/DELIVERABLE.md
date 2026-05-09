# Day 7 Deliverable: Data Exfiltration

Complete the following steps and record findings in `docs/learning-tracker.md`.

## Steps

1. **Run the eval against the vulnerable agent.**

   ```
   python3 labs/day-07-data-exfiltration/eval.py --agent vulnerable
   ```

   Record ASR overall and per channel (send_message_exfil, markdown_image,
   tool_mediated, multi_hop).

2. **Run each channel manually.**

   ```
   python3 labs/day-07-data-exfiltration/attack/exfil_demo.py send_message_exfil
   python3 labs/day-07-data-exfiltration/attack/exfil_demo.py markdown_image
   python3 labs/day-07-data-exfiltration/attack/exfil_demo.py tool_mediated
   python3 labs/day-07-data-exfiltration/attack/exfil_demo.py multi_hop
   ```

   For each channel, note:
   - Did the agent call read_doc("api_keys.md")?
   - Did the agent call send_message / web_fetch?
   - Did the response contain any credential material?

3. **Identify the hardest-to-detect channel.**

   Based on your observations, identify which exfiltration channel would be hardest to
   detect with tool-call-based logging alone. Explain why.

4. **Map the lethal trifecta to this lab.**

   Write out which specific tool or input corresponds to each trifecta leg for each
   exfiltration channel:
   - Leg A (data access): which tool call retrieves the credential?
   - Leg B (untrusted input): what delivered the exfil instruction?
   - Leg C (egress): which tool call or response pattern carries data out?

5. **Read the EchoLeak disclosure and write a one-paragraph summary.**

   Reference: https://www.aim.security/lp/echoleak-vulnerability-disclosure
   Or read the CVE-2025-32711 description.
   Summarize: what was the product, what was the injection vector, what was the exfil channel,
   and what data was exfiltrated.

6. **Document in `docs/learning-tracker.md`.**

   Update the Day 7 row with:
   - ASR per channel
   - Hardest-to-detect channel and why
   - Lethal trifecta mapping for at least two channels
   - EchoLeak one-paragraph summary

## Completion Criteria

- [ ] `eval.py --agent vulnerable` ran to completion
- [ ] All four channels tested manually
- [ ] Hardest-to-detect channel identified with justification
- [ ] Lethal trifecta mapped to at least two channels
- [ ] EchoLeak summary written
- [ ] Day 7 row in learning-tracker.md updated
