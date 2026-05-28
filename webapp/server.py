"""FastAPI app for the ai-security-lab GUI."""

from __future__ import annotations

import sys

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from webapp.paths import REPO_ROOT, STATIC_DIR, TEMPLATES_DIR

# Make repo root importable for backend code that reuses agent/detector libs.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Load .env into os.environ on startup if dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

from webapp.api import agent as agent_api  # noqa: E402
from webapp.api import calibrate as calibrate_api  # noqa: E402
from webapp.api import chat as chat_api  # noqa: E402
from webapp.api import docs as docs_api  # noqa: E402
from webapp.api import helper as helper_api  # noqa: E402
from webapp.api import env as env_api  # noqa: E402
from webapp.api import eval_runs as eval_api  # noqa: E402
from webapp.api import labs as labs_api  # noqa: E402
from webapp.api import runs as runs_api  # noqa: E402
from webapp.api import summary as summary_api  # noqa: E402
from webapp.api import tests as tests_api  # noqa: E402

app = FastAPI(title="ai-security-lab", docs_url="/api/swagger", redoc_url="/api/redoc")


@app.on_event("startup")
async def _build_helper_index() -> None:
    """Build the BM25 index over docs/labs at server start.

    Cheap (~50 ms for ~150 markdown files), so we do it eagerly rather than
    on-demand. Re-run by restarting the server.
    """
    from webapp.helper.corpus import load_corpus
    from webapp.helper.retriever import BM25Retriever

    chunks = load_corpus(REPO_ROOT)
    helper_api.init_retriever(BM25Retriever(chunks))


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount API routers
app.include_router(env_api.router, prefix="/api")
app.include_router(agent_api.router, prefix="/api")
app.include_router(eval_api.router, prefix="/api")
app.include_router(runs_api.router, prefix="/api")
app.include_router(calibrate_api.router, prefix="/api")
app.include_router(labs_api.router, prefix="/api")
app.include_router(tests_api.router, prefix="/api")
app.include_router(summary_api.router, prefix="/api")
app.include_router(docs_api.router, prefix="/api")
app.include_router(chat_api.router, prefix="/api")
app.include_router(helper_api.router, prefix="/api")


# ── Pages ────────────────────────────────────────────────────────────────


def _ctx(request: Request, page: str, **extra) -> dict:
    """Shared template context."""
    import os

    return {
        "request": request,
        "page": page,
        "has_anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "has_openai": bool(os.environ.get("OPENAI_API_KEY")),
        **extra,
    }


@app.get("/", response_class=HTMLResponse)
async def page_welcome(request: Request) -> HTMLResponse:
    from webapp.api.summary import _load_highlights

    return templates.TemplateResponse(
        request, "welcome.html", _ctx(request, "welcome", highlights=_load_highlights())
    )


@app.get("/playground", response_class=HTMLResponse)
async def page_playground(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "playground.html", _ctx(request, "playground"))


@app.get("/eval", response_class=HTMLResponse)
async def page_eval(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "eval.html", _ctx(request, "eval"))


@app.get("/results", response_class=HTMLResponse)
async def page_results(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "results.html", _ctx(request, "results"))


@app.get("/calibration", response_class=HTMLResponse)
async def page_calibration(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "calibration.html", _ctx(request, "calibration"))


@app.get("/labs", response_class=HTMLResponse)
async def page_labs(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "labs.html", _ctx(request, "labs"))


@app.get("/settings", response_class=HTMLResponse)
async def page_settings(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "settings.html", _ctx(request, "settings"))


@app.get("/tests", response_class=HTMLResponse)
async def page_tests(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "tests.html", _ctx(request, "tests"))


@app.get("/docs", response_class=HTMLResponse)
async def page_docs(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "docs_index.html", _ctx(request, "docs"))


@app.get("/docs/{slug}", response_class=HTMLResponse)
async def page_doc(request: Request, slug: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "docs_view.html", _ctx(request, "docs", slug=slug)
    )


@app.get("/tutorial")
async def page_tutorial() -> RedirectResponse:
    """Backwards-compat: redirect old /tutorial path to /docs/tutorial."""
    return RedirectResponse(url="/docs/tutorial", status_code=301)


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}


@app.get("/favicon.ico")
async def favicon() -> RedirectResponse:
    return RedirectResponse(url="/static/favicon.svg", status_code=302)
