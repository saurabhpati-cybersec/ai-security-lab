"""API: read markdown files from docs/."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from webapp.paths import REPO_ROOT

router = APIRouter(tags=["docs"])

DOCS_DIR = REPO_ROOT / "docs"

# Friendly titles for each known doc (used by index page).
DOC_TITLES = {
    "tutorial": ("🎓 Step-by-step tutorial", "20-minute hands-on tour. Every step is a click — no terminal commands."),
    "00-honest-assessment": ("📊 Honest Assessment", "Hype vs market value for AI security skills."),
    "threat-model": ("🎯 Threat Model", "T-01..T-17, STRIDE × OWASP × trifecta."),
    "glossary": ("📖 Glossary", "Precise definitions of every term used in this lab."),
    "ai-agent-security-checklist": ("✅ Build & Deploy Checklist", "Lifecycle checklist: Design → Build → Deploy → Operate → Retire."),
    "secure-prompt-design-checklist": ("✍️ Secure Prompt Design", "Guidance for hardening system prompts and handling untrusted content."),
    "incident-report-template": ("📝 Incident Report Template", "Structured template for post-incident write-ups."),
    "learning-tracker": ("📈 Learning Tracker", "Day-by-day progress with numeric outcomes."),
    "references": ("🔗 References", "Bibliography: frameworks, CVEs, foundational research."),
}

# Explicit ordering used by the index page (tutorial first; reference docs second).
DOC_ORDER = list(DOC_TITLES.keys())


@router.get("/docs")
async def list_docs() -> dict:
    if not DOCS_DIR.exists():
        return {"docs": []}
    present = {f.stem for f in DOCS_DIR.glob("*.md")}
    out = []
    # Emit known docs in the explicit DOC_ORDER first.
    for slug in DOC_ORDER:
        if slug in present:
            title, desc = DOC_TITLES[slug]
            out.append({"slug": slug, "title": title, "description": desc})
    # Then any unknown docs (alphabetical) so new files surface without code edits.
    for slug in sorted(present - set(DOC_ORDER)):
        title = slug.replace("-", " ").title()
        out.append({"slug": slug, "title": title, "description": ""})
    return {"docs": out}


@router.get("/docs/{slug}")
async def get_doc(slug: str) -> dict:
    f = DOCS_DIR / f"{slug}.md"
    if not f.exists() or not f.is_file():
        raise HTTPException(status_code=404, detail=f"doc not found: {slug}")
    title, desc = DOC_TITLES.get(slug, (slug.replace("-", " ").title(), ""))
    return {
        "slug": slug,
        "title": title,
        "description": desc,
        "content": f.read_text(encoding="utf-8"),
    }
