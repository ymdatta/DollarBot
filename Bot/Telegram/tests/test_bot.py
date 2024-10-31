import pytest
from aioresponses import aioresponses
from unittest.mock import AsyncMock, MagicMock
from telegram import Update
from Bot.Telegram.bot import start_command, signup_command, login_command, handle_response

API_BASE_URL = "http://localhost:8000"


@pytest.fixture
def update_mock():
    """Mock an update message with specific content for testing."""
    update = Update(
        update_id=12345,
        message=type('obj', (object,), {
            'chat_id': 6387422040,
            'reply_text': AsyncMock(),
            'text': "Mocked text",
        })()
    )
    return update


@pytest.fixture
def context_mock():
    """Mock context without actual API calls."""
    class MockContext:
        def __init__(self):
            self.args = []

    return MockContext()


@pytest.mark.asyncio
async def test_start_command(update_mock, context_mock):
    """Test the /start command."""
    update_mock.message.reply_text = AsyncMock()
    await start_command(update_mock, context_mock)
    update_mock.message.reply_text.assert_called_once_with(
        "Welcome to MoneyHandler! Please log in using /login <username> <password>"
    )


@pytest.mark.asyncio
async def test_signup_command(update_mock, context_mock):
    """Test the /signup command."""
    update_mock.message.reply_text = AsyncMock()
    await signup_command(update_mock, context_mock)
    update_mock.message.reply_text.assert_called_once_with(
        "Please sign up using /login command before adding expenses."
    )


@pytest.mark.asyncio
async def test_login_command(update_mock, context_mock):
    """Test the /login command."""
    update_mock.message.reply_text = AsyncMock()
    await login_command(update_mock, context_mock)
    update_mock.message.reply_text.assert_called_once_with(
        "Please enter your username and password in the format: <username> <password>"
    )


# @pytest.mark.asyncio
# async def test_handle_response_signup(update_mock, context_mock):
#     """Test handle_response behavior for signup task."""
#     with aioresponses() as m:
#         m.post(f"{API_BASE_URL}/users/", status=200, payload={"message": "User created"})
#         context_mock.args = ["testuser", "testpass"]
#         update_mock.message.reply_text = AsyncMock()
#         await handle_response(update_mock, "testuser testpass")
#         update_mock.message.reply_text.assert_called_once_with(
#             "User created successfully! You can now log in using /login."
#         )


# @pytest.mark.asyncio
# async def test_handle_response_login(update_mock, context_mock):
#     """Test handle_response behavior for login task."""
#     with aioresponses() as m:
#         m.post(f"{API_BASE_URL}/token/", status=200, payload={"access_token": "mocked_token"})
#         context_mock.args = ["testuser", "testpass"]
#         update_mock.message.reply_text = AsyncMock()
#         await handle_response(update_mock, "testuser testpass")
#         update_mock.message.reply_text.assert_called_once_with("Login successful!")
