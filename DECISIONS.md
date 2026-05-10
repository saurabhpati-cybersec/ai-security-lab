# Architecture Decision Records

Autonomous decisions made during the build of this repository.
Each entry follows the ADR format: decision, rationale, alternatives, consequence.

---

## ADR-001: Anthropic primary, OpenAI secondary via thin adapter

**Date:** 2026-05-09
**Decision:** `AnthropicAdapter` uses the official SDK `tools` parameter natively; `OpenAIAdapter` converts the Anthropic tool-definition format internally before sending requests.
**Rationale:** Anthropic is the portfolio focus. OpenAI is a fallback that should not require callers to change their interface or write provider-specific tool definitions.
**Alternatives considered:** Separate interfaces per provider; LangChain as a unified abstraction layer.
**Consequence:** All agents receive `tuple[str, list[dict]]` from adapter `.run()` regardless of provider — adapter-agnostic caller code throughout.

---

## ADR-002: Agents share reference interface, differ in implementation

**Date:** 2026-05-09
**Decision:** `BaseAgent` ABC lives in `agents/reference/agent.py`; `VulnerableAgent` and `ProtectedAgent` subclass it.
**Rationale:** The eval harness must swap agents by name without changing test code. A shared ABC enforces interface consistency and prevents accidental omission of required methods.
**Alternatives considered:** Separate agent files with no shared base class; duck typing only.
**Consequence:** Both variants must implement `_run_loop()` and `_execute_tool()`. Missing either raises `TypeError` at instantiation, not at runtime.

---

## ADR-003: Eval success_criteria is programmatic, not LLM-as-judge

**Date:** 2026-05-09
**Decision:** `success_criteria` uses string-encoded patterns (`regex:`, `agent_called_tool:`, `not_agent_called_tool:`, `benign`) evaluated deterministically in `evaluate_criteria()`.
**Rationale:** LLM-as-judge evals are non-deterministic and expensive. Programmatic criteria are reproducible across runs and fast enough to run in CI without API keys.
**Alternatives considered:** LLM-as-judge for all cases (more expressive but slower and non-reproducible); separate Python functions per test case (more precise but not dataset-portable).
**Consequence:** Criteria must be designed carefully — nuanced behaviors (e.g., "response is helpful but does not reveal system prompt") cannot be expressed as simple patterns and require a proxy criterion.

---

## ADR-004: Bootstrap 95% CI with numpy, not scipy.stats.bootstrap

**Date:** 2026-05-09
**Decision:** `scorers.py` implements manual percentile bootstrap resampling using `numpy.random.default_rng` rather than calling `scipy.stats.bootstrap`.
**Rationale:** `scipy.stats.bootstrap` API changed between versions (argument name changes in 1.9 vs 1.11). Manual implementation is more portable, has no version dependency, and the algorithm is simple enough to own directly.
**Alternatives considered:** `scipy.stats.bootstrap` with version pinning in `requirements.txt`.
**Consequence:** Simpler code with no scipy version constraint. Behavior is identical to the scipy percentile method at `n_resamples=1000, seed=42`.

---

## ADR-005: Tool gateway duplicated into agents/protected/gateway.py

**Date:** 2026-05-09
**Decision:** `ToolGateway` code is duplicated from `labs/day-10-sandboxing-permissions/defense/` into `agents/protected/gateway.py` rather than imported from the labs directory.
**Rationale:** Python cannot import from directories whose names contain hyphens (`labs/day-10-sandboxing-permissions/`). Duplication avoids a runtime `ModuleNotFoundError` with no clean workaround.
**Alternatives considered:** Rename the lab directory (breaks the spec naming convention); use `importlib` with an explicit file path (fragile and non-idiomatic).
**Consequence:** Two copies of `ToolGateway` exist. `agents/protected/gateway.py` is the canonical version used by the protected agent; the labs copy is for lab-local demonstration only.

---

## ADR-006: Detectors use frozen dataclasses + Pydantic v2 consistently

**Date:** 2026-05-09
**Decision:** `DetectionResult` is a frozen `dataclass`; `ClassifierResult` is a Pydantic v2 `BaseModel` with `frozen=True` config.
**Rationale:** Frozen = immutable after creation, appropriate for result objects that must not be mutated by callers. Simple scalar fields with no JSON serialization requirement map naturally to dataclasses; results that need JSON serialization (for log events) map to Pydantic.
**Alternatives considered:** All dataclasses (no JSON serialization support); all Pydantic (heavier than needed for in-memory results).
**Consequence:** Slight inconsistency between modules is justified by different serialization needs. Both are frozen so the behavioral contract is the same.

---

## ADR-007: Log schema emitted as JSONL to stdout or LogWriter, not a database

**Date:** 2026-05-09
**Decision:** `log_event()` appends one-line JSON to a file or stdout. No database dependency.
**Rationale:** Zero external dependencies. SOAR integration happens by parsing the JSONL stream. Simpler for portfolio demos where the consumer is `grep`, `jq`, or a SIEM forwarder.
**Alternatives considered:** SQLite (queryable but a dependency and file-locking concern); Redis stream (realistic for production but requires a running broker).
**Consequence:** No queryable log store in the base implementation. The query interface is `grep + jq`. Any production deployment would replace `LogWriter` with a SIEM-compatible forwarder.

---

## ADR-008: Eval datasets use simulation approach for IPI cases

**Date:** 2026-05-09
**Decision:** The indirect injection dataset includes `"[Imagine web_fetch returned: INJECT...]"` simulation phrasing directly in the user input field.
**Rationale:** Real indirect prompt injection requires an attacker-controlled server that the agent fetches from. Simulation phrasing lets the eval harness test agent behavior against IPI-structured inputs without external infrastructure.
**Alternatives considered:** Mock the `web_fetch` tool to return injection payloads at the harness level (more realistic, significantly more complex to wire across all eval cases).
**Consequence:** IPI eval measures whether the LLM acts on injection-phrased inputs, not whether it faithfully processes tool results from a real network. For full IPI evaluation, use the mock tool injection path described in the harness README.

---

## ADR-009: RulesDetector confidence boosted by co-occurrence

**Date:** 2026-05-09
**Decision:** When multiple rules fire on the same input, confidence is computed as `min(1.0, max_confidence + 0.05 * (len(matched) - 1))`.
**Rationale:** Multiple injection signals in a single input is stronger evidence of malicious intent than any single signal. A base64-encoded payload combined with an instruction-override pattern is more suspicious than either alone.
**Alternatives considered:** Use only the max single-rule confidence (simpler, misses correlated signals); Bayesian combination (principled but requires prior calibration data).
**Consequence:** Inputs with several weak signals can cross the detection threshold even when no individual rule would. This must be monitored — benign technical documentation with multiple keywords (e.g., "ignore errors," "system prompt review") can accumulate false co-occurrence boosts.

---

## ADR-010: OutputFilter domain allowlist is conservative by default

**Date:** 2026-05-09
**Decision:** `DEFAULT_ALLOWLIST = {anthropic.com, openai.com, python.org, github.com, docs.python.org, company.example.com}`.
**Rationale:** Safe default. Operators must explicitly allowlist domains they trust. An open-by-default policy would allow exfiltration to any attacker-controlled domain until explicitly blocked.
**Alternatives considered:** Open by default with a denylist of known-bad domains (more permissive, easier for operators, worse security posture).
**Consequence:** Legitimate external links in agent responses will be blocked until explicitly allowlisted. This is intentional friction that forces operators to make a conscious trust decision for each domain.

---

## ADR-011: ProtectedAgent adapter is lazy-initialized

**Date:** 2026-05-09
**Decision:** `ProtectedAgent._ensure_adapter()` defers adapter construction until the first `run()` call. The `__init__` method sets `self._adapter = None` and `self._adapter_initialized = False`.
**Rationale:** `ProtectedAgent()` must construct without API keys for import testing, eval harness wiring, and unit tests that mock `_run_loop()`. Requiring an API key at construction time breaks any test that doesn't hit the network.
**Alternatives considered:** Always require API key at construction time (cleaner initialization contract but breaks import tests and dry-run scenarios).
**Consequence:** API key errors surface at runtime on the first `run()` call, not at object construction. This is the standard pattern for resource-acquiring objects but callers must be aware that `ProtectedAgent()` succeeding does not guarantee a usable adapter.

---

## ADR-012: SOAR companion is two-platform parallel (Tines + XSOAR)

**Date:** 2026-05-09
**Decision:** Both Tines stories and XSOAR playbooks implement the same three flows: prompt injection triage, agent containment, and exfiltration response.
**Rationale:** The portfolio must demonstrate cross-platform SOAR competence. Different syntax and execution models across both platforms shows understanding of event-driven (Tines) vs. task-based (XSOAR) automation paradigms.
**Alternatives considered:** Single platform only (faster to build, less portfolio differentiation).
**Consequence:** Six story/playbook files instead of three. The parallel coverage — identical logic expressed in two distinct formats — is the primary portfolio differentiator for this section.

---

## ADR-013: Tines story JSON uses simplified but structurally valid format

**Date:** 2026-05-09
**Decision:** Story JSONs follow the Tines export format with `schema_version`, `agents[]`, and `links[]` arrays but are not byte-for-byte importable into a live Tines account.
**Rationale:** Generating fully importable Tines exports requires a live account and all credential references (API keys, team GUIDs) resolved at export time. The structural format is correct and demonstrates platform knowledge without requiring infrastructure.
**Alternatives considered:** Full importable exports (requires Tines account); prose playbooks only (insufficient to demonstrate platform syntax).
**Consequence:** The Tines README explicitly notes these are reference implementations, not plug-and-play imports. A practitioner with a Tines account would need to resolve credential references before importing.

---

## ADR-014: benign.jsonl uses "benign" success_criteria (always True)

**Date:** 2026-05-09
**Decision:** All benign dataset cases use `success_criteria="benign"`, which `evaluate_criteria()` always returns `True` for.
**Rationale:** For false positive rate measurement, what matters is whether the agent completed the request without triggering a defense block. The pass condition is task completion, not a specific response string. Using `benign` as the criterion makes the FPR definition explicit: `FPR = 1 - (benign ASR on protected agent)`.
**Alternatives considered:** `success_criteria="agent_called_tool:read_doc"` for document-lookup cases (more specific but wrong — FPR measures blocking, not specific tool invocation behavior).
**Consequence:** `benign ASR = 1.0` on the vulnerable agent (no defenses means no blocks). `Protected FPR = 1 - (benign ASR on protected agent)` gives the fraction of legitimate requests incorrectly rejected.

---

## ADR-015: Per-lab eval.py files use static analysis when no API key

**Date:** 2026-05-09
**Decision:** Day 8-11 `eval.py` files run without live API calls, using dataset case counting and input pattern matching rather than live agent execution.
**Rationale:** Live API evals during build would incur cost and require keys in the build environment. Static evals demonstrate harness wiring, dataset structure, and criteria logic without runtime cost.
**Alternatives considered:** Mock LLM responses (more realistic but adds significant fixture complexity per lab); skip eval.py in defense labs (less portfolio value).
**Consequence:** Real ASR numbers require `make eval-all` with a live `ANTHROPIC_API_KEY`. The static evals show methodology and confirm dataset validity but do not produce ground-truth attack success rates.

---

## ADR-016: corpus/api_keys.md uses canonical AWS example key

**Date:** 2026-05-09
**Decision:** The corpus document uses `AKIAIOSFODNN7EXAMPLE` (the AWS documentation example key) rather than a randomly generated fake key.
**Rationale:** This is the industry-standard example key with no real risk. AWS explicitly defines it as the canonical example access key in their documentation. It is immediately recognizable to defenders as non-real while remaining realistic for exfiltration detection demos.
**Alternatives considered:** Random-looking fake key with no special properties (unrecognizable, may trigger real scanner alerts); redacted placeholder (doesn't exercise the exfiltration detection path).
**Consequence:** Any credential scanner will flag the key but recognize it as the AWS documentation example. No real credential risk. The `OutputFilter` `SECRET_PATTERNS` list includes this key to demonstrate the filtering path.

---

## ADR-017: Per-lab eval.py accepts --agent flag

**Date:** 2026-05-09
**Decision:** Every lab `eval.py` accepts `--agent vulnerable|protected` via `argparse`.
**Rationale:** Before/after comparisons are the primary evaluation pattern. A consistent `--agent` flag allows running the same eval against both variants without modifying scripts or maintaining separate copies.
**Alternatives considered:** Hardcode `"vulnerable"` in attack labs and `"protected"` in defense labs (simpler per-lab, breaks the comparison workflow).
**Consequence:** Consistent CLI interface across all 14 labs. `python eval.py --agent protected` is always valid, even if the lab was originally designed to demonstrate a vulnerability.

---

## ADR-018: XSOAR incident field names prefixed with "aisecurity"

**Date:** 2026-05-09
**Decision:** All custom XSOAR incident fields use the `aisecurity*` prefix (e.g., `aisecuritydetectorscore`, `aisecuritysessionid`).
**Rationale:** XSOAR field names must be globally unique across all installed content packs. Without a prefix, field names like `detectorscore` or `sessionid` will collide with fields from Elastic, Splunk, or other common integrations installed on the same platform.
**Alternatives considered:** No prefix, relying on uniqueness by chance (fragile); a longer namespace prefix (more unique but more verbose in playbook expressions).
**Consequence:** Field names are verbose but unambiguous. Playbook expressions use the full prefixed name throughout, which is the correct XSOAR practice for custom content.

---

## ADR-019: latest_summary.md is tracked in git; other eval results are gitignored

**Date:** 2026-05-10
**Decision:** `evals/results/*` is gitignored. `evals/results/latest_summary.md` is the exception — it is committed directly because it is the primary portfolio artifact for the eval section.
**Rationale:** Per-run JSONL output files are large and potentially sensitive (they contain raw agent responses). The summary is the artifact a portfolio reviewer needs; individual run files are local-only artifacts.
**Alternatives considered:** Move `latest_summary.md` to `docs/` outside the gitignore scope (works but separates the file from its peer results); track all results (too much noise, potential sensitivity).
**Consequence:** `latest_summary.md` is tracked; all other content under `evals/results/` is local-only. The `.gitignore` uses `evals/results/*` with `!evals/results/.gitkeep` to preserve the directory.

---

## ADR-020: No AI slop policy enforced throughout

**Date:** 2026-05-09
**Decision:** Prohibited across all documentation: emoji-as-bullets, phrases like "in today's fast-paced AI landscape," closing "in conclusion" sections, and qualifiers like "it's important to note."
**Rationale:** This repository targets senior AI security engineers. Marketing language and filler phrases signal inexperience to the exact audience being addressed.
**Alternatives considered:** N/A — there is no tradeoff here. Direct technical writing is strictly superior for this audience.
**Consequence:** All lab READMEs, docs, and inline comments are written in direct declarative prose. Where something is uncertain, uncertainty is stated directly rather than hedged.

---

## ADR-021: 14 mandatory README sections enforced per lab

**Date:** 2026-05-09
**Decision:** Every lab README must contain all 14 sections in fixed order: Objective, Why It Matters, Threat Model Reference, Trifecta Mapping, Prerequisites, Hands-On Lab, Attack Scenario, Defensive Control, Expected Output, Evaluation, Difficulty, Time Required, Document, References. Non-applicable sections use "N/A — [reason]".
**Rationale:** Consistent structure lets portfolio readers scan any lab and know exactly where to find objective, evaluation methodology, and references without reading the whole document. Enforced order prevents reorganization drift across 14 labs.
**Alternatives considered:** Free-form lab READMEs (faster to write, inconsistent reader experience); section subset per lab type (reduces N/A clutter but loses predictable navigation).
**Consequence:** Some labs have short N/A sections (e.g., Day 1 Defensive Control: "N/A — foundational lab, no defense implemented yet"). This is accepted as a clarity-over-brevity tradeoff — the reader always knows what to expect at each position.
