"""Tests for starter.python.openai_client._convert_messages and OpenAIAdapter filtering."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from starter.python.openai_client import _convert_messages


def test_string_content_passes_through() -> None:
    msgs = [{"role": "user", "content": "hello"}]
    out = _convert_messages(msgs)
    assert out == [{"role": "user", "content": "hello"}]


def test_assistant_tool_use_with_text() -> None:
    msgs = [
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Calling tool"},
                {
                    "type": "tool_use",
                    "id": "toolu_abc",
                    "name": "read_doc",
                    "input": {"name": "faq.md"},
                },
            ],
        }
    ]
    out = _convert_messages(msgs)

    assert len(out) == 1
    assert out[0]["role"] == "assistant"
    assert out[0]["content"] == "Calling tool"
    assert "tool_calls" in out[0]
    assert len(out[0]["tool_calls"]) == 1

    tc = out[0]["tool_calls"][0]
    assert tc["id"] == "toolu_abc"
    assert tc["type"] == "function"
    assert tc["function"]["name"] == "read_doc"
    assert tc["function"]["arguments"] == '{"name": "faq.md"}'


def test_assistant_tool_use_without_text_uses_null_content() -> None:
    msgs = [
        {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "toolu_x", "name": "f", "input": {}},
            ],
        }
    ]
    out = _convert_messages(msgs)
    assert out[0]["content"] is None
    assert len(out[0]["tool_calls"]) == 1


def test_user_tool_result_becomes_tool_role_message() -> None:
    msgs = [
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "toolu_abc", "content": "doc body here"},
            ],
        }
    ]
    out = _convert_messages(msgs)

    assert len(out) == 1
    assert out[0]["role"] == "tool"
    assert out[0]["tool_call_id"] == "toolu_abc"
    assert out[0]["content"] == "doc body here"


def test_tool_result_with_list_content_flattens() -> None:
    msgs = [
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_y",
                    "content": [
                        {"type": "text", "text": "part1 "},
                        {"type": "text", "text": "part2"},
                    ],
                },
            ],
        }
    ]
    out = _convert_messages(msgs)
    assert out[0]["content"] == "part1 part2"


def test_full_multi_turn_round_trip() -> None:
    msgs = [
        {"role": "user", "content": "Read faq.md"},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Reading."},
                {
                    "type": "tool_use",
                    "id": "toolu_1",
                    "name": "read_doc",
                    "input": {"name": "faq.md"},
                },
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "toolu_1", "content": "FAQ contents"},
            ],
        },
    ]
    out = _convert_messages(msgs)

    assert len(out) == 3
    assert out[0] == {"role": "user", "content": "Read faq.md"}
    assert out[1]["role"] == "assistant"
    assert "tool_calls" in out[1]
    assert out[2]["role"] == "tool"
    assert out[2]["tool_call_id"] == "toolu_1"


# ---------------------------------------------------------------------------
# Regression tests: multi_tool_use.parallel pseudo-tool filtering
# ---------------------------------------------------------------------------

def _make_oai_tool_call(id_: str, name: str, arguments: dict) -> SimpleNamespace:
    """Build a minimal fake OpenAI tool-call object (mirrors the SDK shape)."""
    return SimpleNamespace(
        id=id_,
        type="function",
        function=SimpleNamespace(
            name=name,
            arguments=json.dumps(arguments),
        ),
    )


def _make_oai_response(*tool_calls: SimpleNamespace, content: str = "") -> MagicMock:
    """Build a minimal fake OpenAI chat-completion response."""
    message = SimpleNamespace(
        content=content or None,
        tool_calls=list(tool_calls) if tool_calls else None,
    )
    choice = SimpleNamespace(message=message)
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_adapter() -> "OpenAIAdapter":  # noqa: F821
    """Instantiate OpenAIAdapter with a fake API key (no real HTTP calls)."""
    from starter.python.openai_client import OpenAIAdapter

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-fake"}):
        adapter = OpenAIAdapter(model="gpt-4.1", agent_id="test", session_id="test")
    return adapter


TOOL_DEFS = [
    {
        "name": "web_fetch",
        "description": "Fetch a URL",
        "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}},
    },
    {
        "name": "read_doc",
        "description": "Read a document",
        "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}},
    },
    {
        "name": "send_message",
        "description": "Send a message",
        "input_schema": {
            "type": "object",
            "properties": {"recipient": {"type": "string"}, "body": {"type": "string"}},
        },
    },
]


def test_multi_tool_use_parallel_is_filtered_out() -> None:
    """multi_tool_use.parallel must be dropped; only real tool calls survive."""
    adapter = _make_adapter()

    # Fake response: one real tool call + the OpenAI pseudo-tool
    real_call = _make_oai_tool_call("call_real", "read_doc", {"name": "faq.md"})
    pseudo_call = _make_oai_tool_call(
        "call_pseudo",
        "multi_tool_use.parallel",
        {
            "tool_uses": [
                {"recipient_name": "functions.read_doc", "parameters": {"name": "faq.md"}},
                {"recipient_name": "functions.web_fetch", "parameters": {"url": "http://x"}},
            ]
        },
    )
    fake_response = _make_oai_response(real_call, pseudo_call)

    with patch.object(adapter._client.chat.completions, "create", return_value=fake_response):
        _, tool_calls = adapter.run(
            messages=[{"role": "user", "content": "Read faq.md"}],
            tools=TOOL_DEFS,
            system_prompt="You are an assistant.",
        )

    names = [tc["name"] for tc in tool_calls]
    assert "multi_tool_use.parallel" not in names, (
        "multi_tool_use.parallel pseudo-tool must be filtered out"
    )
    assert names == ["read_doc"], f"Expected only [read_doc], got {names}"


def test_real_tool_calls_all_pass_through() -> None:
    """All three real tool calls must survive when no pseudo-tool is present."""
    adapter = _make_adapter()

    fake_response = _make_oai_response(
        _make_oai_tool_call("c1", "web_fetch", {"url": "http://example.com"}),
        _make_oai_tool_call("c2", "read_doc", {"name": "notes.md"}),
        _make_oai_tool_call("c3", "send_message", {"recipient": "alice", "body": "hi"}),
    )

    with patch.object(adapter._client.chat.completions, "create", return_value=fake_response):
        _, tool_calls = adapter.run(
            messages=[{"role": "user", "content": "Do everything"}],
            tools=TOOL_DEFS,
            system_prompt="You are an assistant.",
        )

    names = [tc["name"] for tc in tool_calls]
    assert names == ["web_fetch", "read_doc", "send_message"]


def test_parallel_tool_calls_false_is_passed_to_create() -> None:
    """The adapter must pass parallel_tool_calls=False to suppress the pseudo-tool server-side."""
    adapter = _make_adapter()

    fake_response = _make_oai_response(
        _make_oai_tool_call("c1", "read_doc", {"name": "x.md"})
    )

    with patch.object(
        adapter._client.chat.completions, "create", return_value=fake_response
    ) as mock_create:
        adapter.run(
            messages=[{"role": "user", "content": "hello"}],
            tools=TOOL_DEFS,
            system_prompt="You are an assistant.",
        )

    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs.get("parallel_tool_calls") is False, (
        "parallel_tool_calls=False must be forwarded to chat.completions.create"
    )
