"""API: run an agent against a single input, capture events."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["agent"])


class RunAgentRequest(BaseModel):
    agent: str  # "vulnerable" | "protected"
    input: str
    enable_classifier: bool = False


class RunAgentResponse(BaseModel):
    response: str
    tool_calls: list[dict]
    tool_results: list[dict]
    events: list[dict]
    error: str | None = None


def _build_agent(name: str, enable_classifier: bool) -> Any:
    if name == "vulnerable":
        from agents.vulnerable.agent import VulnerableAgent

        return VulnerableAgent()
    if name == "protected":
        from agents.protected.agent import ProtectedAgent

        return ProtectedAgent(enable_classifier=enable_classifier)
    raise HTTPException(status_code=400, detail=f"unknown agent: {name}")


@router.post("/run-agent", response_model=RunAgentResponse)
async def run_agent(req: RunAgentRequest) -> RunAgentResponse:
    from agents.reference.agent import ToolCall, ToolResult
    from starter.python.log_schema import InMemoryLogWriter

    agent = _build_agent(req.agent, req.enable_classifier)
    writer = InMemoryLogWriter()
    agent.log_writer = writer

    tool_calls_made: list[dict] = []
    tool_results: list[dict] = []
    original_execute = agent._execute_tool

    def patched_execute(tc: ToolCall) -> ToolResult:
        tool_calls_made.append({"name": tc.name, "input": dict(tc.args)})
        result = original_execute(tc)
        tool_results.append({
            "tool_name": result.tool_name,
            "content": result.content,
            "error": result.error,
        })
        return result

    agent._execute_tool = patched_execute
    try:
        text = agent.run(req.input)
    except Exception as exc:  # noqa: BLE001
        return RunAgentResponse(
            response="",
            tool_calls=tool_calls_made,
            tool_results=tool_results,
            events=[ev.model_dump(mode="json") for ev in writer.events],
            error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        agent._execute_tool = original_execute

    return RunAgentResponse(
        response=text,
        tool_calls=tool_calls_made,
        tool_results=tool_results,
        events=[ev.model_dump(mode="json") for ev in writer.events],
    )
