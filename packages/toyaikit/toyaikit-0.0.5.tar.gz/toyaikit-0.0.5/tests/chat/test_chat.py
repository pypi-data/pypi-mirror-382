from types import SimpleNamespace as D
from unittest.mock import MagicMock, call

from toyaikit.chat.chat import ChatAssistant
from toyaikit.llm import OpenAIClient


def test_openaiclient_send_request():
    mock_tools = MagicMock()
    tools_list = [{"name": "tool1", "description": "tool1_description"}]
    mock_tools.get_tools.return_value = tools_list

    mock_openai = MagicMock()
    mock_response = MagicMock()
    mock_openai.responses.create.return_value = mock_response

    # Pass the mock_openai directly to OpenAIClient
    client = OpenAIClient(model="gpt-4o-mini", client=mock_openai)

    chat_messages = [{"role": "user", "content": "hi"}]
    result = client.send_request(chat_messages, tools=mock_tools)

    mock_openai.responses.create.assert_called_once_with(
        model="gpt-4o-mini", input=chat_messages, tools=tools_list
    )
    assert result == mock_response


def test_chatassistant_run_one_cycle(monkeypatch):
    mock_tools = MagicMock()
    mock_tools.function_call.return_value = {
        "role": "function",
        "content": "result",
    }

    mock_interface = MagicMock()
    # Simulate user input: first call returns 'hello', second call returns 'stop'
    mock_interface.input.side_effect = ["hello", "stop"]

    mock_interface.display = MagicMock()
    mock_interface.display_response = MagicMock()
    mock_interface.display_function_call = MagicMock()

    mock_llm_client = MagicMock()

    # Simulate LLM response: one message with content as list of objects with text attribute
    message = D(type="message", content=[D(text="hi")])
    response = D(output=[message])

    mock_llm_client.send_request.return_value = response

    assistant = ChatAssistant(
        tools=mock_tools,
        developer_prompt="You are a helpful assistant.",
        chat_interface=mock_interface,
        llm_client=mock_llm_client,
    )

    # Run the assistant (should exit after one cycle)
    assistant.run()

    assert mock_interface.input.call_count >= 2
    mock_interface.display_response.assert_called()


def test_chatassistant_function_call_flow_with_fakes():
    mock_tools = MagicMock()
    call1 = {"role": "function", "content": "result_func1"}
    call2 = {"role": "function", "content": "result_func2"}
    mock_tools.function_call.side_effect = [call1, call2]

    mock_interface = MagicMock()
    mock_interface.input.side_effect = ["ask", "stop"]

    mock_llm_client = MagicMock()

    function_call1 = D(type="function_call", name="func1", arguments="{}")
    function_call2 = D(type="function_call", name="func2", arguments="{}")
    message = D(type="message", content=[D(text="Here is your answer.")])

    mock_llm_client.send_request.side_effect = [
        MagicMock(output=[function_call1, function_call2]),
        MagicMock(output=[message]),
    ]

    assistant = ChatAssistant(
        tools=mock_tools,
        developer_prompt="You are a helpful assistant.",
        chat_interface=mock_interface,
        llm_client=mock_llm_client,
    )
    assistant.run()

    # Check function_call called for each function_call entry
    assert mock_tools.function_call.call_count == 2
    mock_tools.function_call.assert_has_calls(
        [call(function_call1), call(function_call2)]
    )

    # Check display_function_call called for each function call with correct signature
    assert mock_interface.display_function_call.call_count == 2
    mock_interface.display_function_call.assert_has_calls(
        [
            call("func1", "{}", call1),
            call("func2", "{}", call2),
        ]
    )

    # Check display_response called for the message with markdown text
    assert mock_interface.display_response.call_count == 1
    mock_interface.display_response.assert_called_with("Here is your answer.")

    # Check input() called at least twice ("ask" and "stop")
    assert mock_interface.input.call_count >= 2


def test_chatassistant_order_message_and_function_calls():
    mock_interface = MagicMock()
    mock_interface.input.side_effect = ["ask", "stop"]

    mock_llm_client = MagicMock()

    message1 = D(type="message", content=[D(text="First message.")])
    function_call1 = D(type="function_call", name="func1", arguments="{}")
    function_call2 = D(type="function_call", name="func2", arguments="{}")
    message2 = D(type="message", content=[D(text="Second message.")])

    # The LLM first returns a message and two function calls, then a message
    mock_llm_client.send_request.side_effect = [
        MagicMock(output=[message1, function_call1, function_call2]),
        MagicMock(output=[message2]),
    ]

    mock_tools = MagicMock()

    # Simulate function_call returning a result for each call
    call1 = {"role": "function", "content": "result_func1"}
    call2 = {"role": "function", "content": "result_func2"}
    mock_tools.function_call.side_effect = [
        call1,
        call2,
    ]

    assistant = ChatAssistant(
        tools=mock_tools,
        developer_prompt="You are a helpful assistant.",
        chat_interface=mock_interface,
        llm_client=mock_llm_client,
    )
    assistant.run()

    # Check input() called twice
    assert mock_interface.input.call_count == 2

    # Check LLM called twice
    assert mock_llm_client.send_request.call_count == 2

    # Check function_call called for each function_call entry
    assert mock_tools.function_call.call_count == 2
    mock_tools.function_call.assert_has_calls(
        [call(function_call1), call(function_call2)]
    )

    # Check display_response called for each message with markdown text
    assert mock_interface.display_response.call_count == 2
    mock_interface.display_response.assert_has_calls(
        [call("First message."), call("Second message.")]
    )

    # Check display_function_call called for each function call with correct signature
    assert mock_interface.display_function_call.call_count == 2
    mock_interface.display_function_call.assert_has_calls(
        [
            call("func1", "{}", call1),
            call("func2", "{}", call2),
        ]
    )

    # Check the order of all relevant calls
    expected_order = [
        call.input(),
        call.display_response("First message."),
        call.display_function_call("func1", "{}", call1),
        call.display_function_call("func2", "{}", call2),
        call.display_response("Second message."),
        call.input(),
    ]
    actual_calls = [c for c in mock_interface.mock_calls if c in expected_order]
    assert actual_calls == expected_order
