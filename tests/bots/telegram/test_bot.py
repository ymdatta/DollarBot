# from unittest.mock import AsyncMock, MagicMock

# import pytest
# from aioresponses import aioresponses
# from telegram import Update

# from bots.telegram.bot import (
#     handle_message,
#     login_command,
#     signup_command,
#     start_command,
# )

# API_BASE_URL = "http://localhost:8000"


# @pytest.fixture
# def update_mock():
#     """Mock an update message with specific content for testing."""
#     update = Update(
#         update_id=12345,
#         message=type(
#             "obj",
#             (object,),
#             {
#                 "chat_id": 6387422040,
#                 "reply_text": AsyncMock(),
#                 "text": "Mocked text",
#             },
#         )(),
#     )
#     return update


# @pytest.fixture
# def context_mock():
#     """Mock context without actual API calls."""

#     class MockContext:
#         def __init__(self):
#             self.args = []

#     return MockContext()


# @pytest.mark.asyncio
# async def test_start_command(update_mock, context_mock):
#     """Test the /start command."""
#     update_mock.message.reply_text = AsyncMock()
#     await start_command(update_mock, context_mock)
#     update_mock.message.reply_text.assert_called_once_with(
#         "Welcome to MoneyHandler! Please log in using /login <username> <password>"
#     )


# # @pytest.mark.asyncio
# # async def test_signup_command(update_mock, context_mock):
# #     """Test the /signup command."""
# #     update_mock.message.reply_text = AsyncMock()
# #     await signup_command(update_mock, context_mock)
# #     update_mock.message.reply_text.assert_called_once_with(
# #         "Please sign up using /login command before adding expenses."
# #     )


# # @pytest.mark.asyncio
# # async def test_login_command_username_prompt(update_mock, context_mock):
# #     """Test the /login command prompts for the username."""
# #     update_mock.message.reply_text = AsyncMock()
# #     await login_command(update_mock, context_mock)
# #     update_mock.message.reply_text.assert_called_once_with(
# #         "Please enter your username:"
# #     )


# # @pytest.mark.asyncio
# # async def test_login_command_password_prompt(update_mock, context_mock):
# #     """Test the login process prompts for the password after receiving the username."""
# #     # First, simulate the username prompt by calling the /login command
# #     update_mock.message.reply_text = AsyncMock()
# #     await login_command(update_mock, context_mock)

# #     # Set the state to 'awaiting_password' to simulate that the username has been received
# #     user_id = update_mock.message.chat_id
# #     context_mock.USERNAMES = {user_id: "testuser"}  # mock username storage
# #     context_mock.LOGIN_STATE = {user_id: "awaiting_password"}

# #     # Simulate the password prompt
# #     update_mock.message.text = "password123"
# #     await handle_message(update_mock, context_mock)

# #     # Check if the bot prompts for a password
# #     update_mock.message.reply_text.assert_called_with("Please enter your password:")


# # @pytest.mark.asyncio
# # async def test_handle_response_signup(update_mock, context_mock):
# #     """Test handle_response behavior for signup task."""
# #     with aioresponses() as m:
# #         m.post(f"{API_BASE_URL}/users/", status=200, payload={"message": "User created"})
# #         context_mock.args = ["testuser", "testpass"]
# #         update_mock.message.reply_text = AsyncMock()
# #         await handle_response(update_mock, "testuser testpass")
# #         update_mock.message.reply_text.assert_called_once_with(
# #             "User created successfully! You can now log in using /login."
# #         )


# # @pytest.mark.asyncio
# # async def test_handle_response_login(update_mock, context_mock):
# #     """Test handle_response behavior for login task."""
# #     with aioresponses() as m:
# #         m.post(f"{API_BASE_URL}/token/", status=200, payload={"access_token": "mocked_token"})
# #         context_mock.args = ["testuser", "testpass"]
# #         update_mock.message.reply_text = AsyncMock()
# #         await handle_response(update_mock, "testuser testpass")
# #         update_mock.message.reply_text.assert_called_once_with("Login successful!")
