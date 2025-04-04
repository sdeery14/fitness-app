import pytest
from unittest.mock import patch, MagicMock
from app import chatbot_message, initialize_history, update_history, user, bot
from openai import APIError, APIConnectionError, RateLimitError

# Fixture to initialize history before each test
@pytest.fixture
def history():
    return initialize_history()

# Test case for successful chatbot message response
@patch('app.client.chat.completions.create')
def test_chatbot_message_success(mock_create, history):
    # Mocking the API response
    mock_create.return_value = [
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))])
    ]
    # Calling the function and converting the generator to a list
    response = list(chatbot_message(history))
    # Asserting the response
    assert response == ["Hello"]

@patch('app.client.chat.completions.create')
def test_chatbot_message_api_error(mock_create, history):
    # Mocking an API error with required arguments
    mock_create.side_effect = APIError(
        message="API Error",
        request=None,  # Provide the required 'request' argument
        body=None      # Provide the required 'body' argument
    )
    response = list(chatbot_message(history))
    assert "OpenAI API returned an API Error" in response[0]


@patch('app.client.chat.completions.create')
def test_chatbot_message_connection_error(mock_create, history):
    # Mocking a connection error with required arguments
    mock_create.side_effect = APIConnectionError(
        message="Connection Error",
        request=None  # Provide the required 'request' argument
    )
    response = list(chatbot_message(history))
    assert "Failed to connect to OpenAI API" in response[0]



@patch('app.client.chat.completions.create')
def test_chatbot_message_rate_limit_error(mock_create, history):
    # Create mock request and response objects
    mock_request = MagicMock()
    mock_response = MagicMock()

    # Mocking a rate limit error with required arguments
    mock_create.side_effect = RateLimitError(
        message="Rate Limit Error",
        body=mock_request,   # Provide the mock 'request' object
        response=mock_response  # Provide the mock 'response' object
    )

    # Call the function and convert the generator to a list
    response = list(chatbot_message(history))

    # Assert the error message in the response
    assert "OpenAI API request exceeded rate limit" in response[0]



# Test case for initializing history
def test_initialize_history():
    history = initialize_history()
    # Asserting the initial state of history
    assert len(history) == 1
    assert history[0]['role'] == 'system'

# Test case for updating history with a new message
def test_update_history(history):
    updated_history = update_history(history, 'user', 'Test message')
    # Asserting the updated state of history
    assert len(updated_history) == 2
    assert updated_history[1]['role'] == 'user'
    assert updated_history[1]['content'] == 'Test message'

# Test case for user function
def test_user_function(history):
    user_message = "Hello"
    _, updated_history = user(user_message, history)
    # Asserting the updated state of history after user message
    assert len(updated_history) == 2
    assert updated_history[1]['role'] == 'user'
    assert updated_history[1]['content'] == 'Hello'

# Test case for bot function
@patch('app.chatbot_message')
def test_bot_function(mock_chatbot_message, history):
    # Mocking the chatbot message response
    mock_chatbot_message.return_value = iter(["Hello"])
    # Calling the bot function and converting the generator to a list
    response = list(bot(history))
    # Asserting the updated state of history after bot response
    assert history[-1]['content'] == "Hello"