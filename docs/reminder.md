# About MyDollarBot's /set_reminder Feature
The /setReminder feature allows users to configure daily or monthly reminders for tracking expenses with MyDollarBot. Users can specify the frequency (daily or monthly) and the exact time at which they wish to receive reminders about their expenditures.

# Location of Code for this Feature
The code that implements this feature can be found [here](https://github.com/rrajpuro/DollarBot/blob/main/code/reminder.py)

## Code Description
### Functions

1. run(message, bot):
   - This function initiates the process of setting reminders. It prompts the user to select a category for which they want to set a reminder. Once the user chooses a category, control is passed to post_operation_selection(message, bot) for further processing.
   - It takes two arguments, message (the user's message) and bot (the Telegram bot object).

2. post_operation_selection(message, bot):
   - This function handles the selected category from the user and prompts them to input the time for the reminder. Once the user provides the time, control is passed to process_reminder_time(message, chat_id, selected_type, bot) for further processing.
   - It takes three arguments, message (the user's message), chat_id (the user's chat ID), and bot (the Telegram bot object).

3. process_reminder_time(message, chat_id, selected_type, bot):
   - This function processes the user's input for the reminder time and validates the time format (HH:MM). If the time is in the correct format, it updates the user's reminder settings in the JSON database.
   - It takes four arguments: message (the user's message), chat_id (the user's chat ID), selected_type (the reminder frequency, e.g., "Day" or "Month"), and bot (the Telegram bot object).

4. send_expenses_reminder(chat_id, dayormonth, bot):
   - This function is responsible for sending reminders to users. It retrieves the user's expense history and relevant budget data. Depending on whether the reminder is set for the day or month, it fetches the corresponding data and composes a reminder message. This message is sent to the user to help them track their spending.
   - It takes three arguments: chat_id (the user's chat ID), dayormonth (reminder frequency, e.g., "Day" or "Month"), and bot (the Telegram bot object).

5. send_reminder(chat_id, message, bot):
   - This function sends a reminder message to the user with the specified chat ID. It also prints a confirmation message to the console.
   - It takes three arguments: chat_id (the user's chat ID), message (the reminder message to send), and bot (the Telegram bot object).

6. check_reminders(bot):
   - This function is responsible for periodically checking and sending reminders to users. It reads user-specific reminder settings from the JSON database and compares the current time to the configured reminder time. If they match, it sends the daily reminder to the user.
   - It takes one argument, bot (the Telegram bot object).

## How to Use This Feature
1. Start the MyDollarBot project.
2. Open the Telegram chat with MyDollarBot.
3. Select /set_reminder from menu to configure reminders for tracking daily or monthly expenses.
4. Follow the prompts to select a category and enter the time for the reminder.



