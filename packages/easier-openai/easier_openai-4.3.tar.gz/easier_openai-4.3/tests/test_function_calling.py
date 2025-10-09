import json
from types import SimpleNamespace
from unittest.mock import MagicMock


from easier_openai.assistant import Assistant


def make_assistant() -> Assistant:
    assistant = Assistant.__new__(Assistant)
    assistant.system_prompt = ""
    assistant.model = "test-model"
    assistant.reasoning = None
    assistant.conversation_id = "conv_test"
    assistant.conversation = None
    assistant.client = SimpleNamespace(responses=MagicMock())
    return assistant


def test_prepare_function_tools_generates_schema_and_map():
    assistant = make_assistant()

    def describe_city(city: str) -> dict:
        """
        Description:
            Provide a short description for a city.
        Args:
            city: The city to describe.
        """

        return {"city": city}

    prepared, tool_map = assistant._prepare_function_tools([describe_city])

    assert len(prepared) == 1
    schema = prepared[0]
    assert schema["type"] == "function"
    assert schema["name"] == "describe_city"
    assert "city" in schema["parameters"]["properties"]
    assert tool_map["describe_city"] is describe_city
    assert hasattr(describe_city, "schema")


def test_submit_tool_outputs_until_complete_executes_tools_and_returns_final_response():
    assistant = make_assistant()

    tool_call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(
            name="describe_city", arguments=json.dumps({"city": "Paris"})
        ),
    )

    required_action = SimpleNamespace(
        type="submit_tool_outputs",
        submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call]),
    )

    initial_response = SimpleNamespace(
        status="requires_action",
        required_action=required_action,
        id="resp_1",
    )

    final_response = SimpleNamespace(
        status="completed",
        required_action=None,
        output_text="done",
    )

    assistant.client.responses.submit_tool_outputs = MagicMock(
        return_value=final_response
    )

    def describe_city(city: str) -> dict:
        return {"city": city}

    result = assistant._submit_tool_outputs_until_complete(
        initial_response,
        {"describe_city": describe_city},
    )

    assistant.client.responses.submit_tool_outputs.assert_called_once()
    call_kwargs = assistant.client.responses.submit_tool_outputs.call_args.kwargs
    assert call_kwargs["response_id"] == "resp_1"
    assert call_kwargs["tool_outputs"] == [
        {"tool_call_id": "call_1", "output": json.dumps({"city": "Paris"})}
    ]
    assert result is final_response


def test_chat_flows_through_function_calling_cycle():
    assistant = make_assistant()
    assistant.client.responses.stream = MagicMock()

    captured = {}

    def describe_city(city: str) -> dict:
        captured["city"] = city
        return {"city": city.title()}

    tool_call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(
            name="describe_city", arguments=json.dumps({"city": "paris"})
        ),
    )

    required_action = SimpleNamespace(
        type="submit_tool_outputs",
        submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call]),
    )

    initial_response = SimpleNamespace(
        status="requires_action",
        required_action=required_action,
        id="resp_1",
        output_text="",
        conversation="conv_result",
    )

    final_response = SimpleNamespace(
        status="completed",
        required_action=None,
        output_text="Paris is lovely.",
        conversation="conv_result",
    )

    assistant.client.responses.create.return_value = initial_response
    assistant.client.responses.submit_tool_outputs.return_value = final_response

    result = assistant.chat("Tell me about Paris", custom_tools=[describe_city])

    assert result == "Paris is lovely."
    assistant.client.responses.create.assert_called_once()
    tools_arg = assistant.client.responses.create.call_args.kwargs["tools"]
    assert tools_arg and tools_arg[0]["name"] == "describe_city"
    submit_kwargs = assistant.client.responses.submit_tool_outputs.call_args.kwargs
    assert submit_kwargs["response_id"] == "resp_1"
    assert json.loads(submit_kwargs["tool_outputs"][0]["output"]) == {
        "city": "Paris"
    }
    assert captured["city"] == "paris"
