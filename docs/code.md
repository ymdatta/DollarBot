# About MyDollarBot's code.py file
code.py is the main file from where calls to the corresponding .py files for all features are sent. It contains a number of endpoints which redirect to function calls in the corresponding files. 

# Location of Code for this Feature
The code that implements this feature can be found [here](https://github.com/rrajpuro/DollarBot/blob/feature/setReminder/code/code.py)

# Code Description
## Functions

1. main()
The entire bot's execution begins here. It ensure the **bot** variable begins polling and actively listening for requests from telegram.

2. listener(user_requests):
Takes 1 argument **user_requests** and logs all user interaction with the bot including all bot commands run and any other issue logs.

3. start_and_menu_command(m):
Prints out the the main menu displaying the features that the bot offers and the corresponding commands to be run from the Telegram UI to use these features. Commands used to run this: commands=['start', 'menu']

4. command_add(message)
Takes 1 argument **message** which contains the message from the user along with the chat ID of the user chat. It then calls add.py to run to execute the add functionality. Commands used to run this: commands=['add']

5. command_add_recurring(message)
Takes 1 argument **message** which contains the message from the user along with the chat ID of the user chat. It then calls add_recurring.py to run to execute the functionality. Commands used to run this: commands=['add_recurring']

6. command_history(message):
Takes 1 argument **message** which contains the message from the user along with the chat ID of the user chat. It then calls history.py to run to execute the add functionality. Commands used to run this: commands=['history']

7. command_edit(message):
Takes 1 argument **message** which contains the message from the user along with the chat ID of the user chat. It then calls edit.py to run to execute the add functionality. Commands used to run this: commands=['edit']

8. command_display(message):
Takes 1 argument **message** which contains the message from the user along with the chat ID of the user chat. It then calls display.py to run to execute the add functionality. Commands used to run this: commands=['display']

9. command_delete(message):
Takes 1 argument **message** which contains the message from the user along with the chat ID of the user chat. It then calls delete.py to run to execute the add functionality. Commands used to run this: commands=['delete_all']

10. command_delete_expense(message):
Takes 1 argument **message** which contains the message from the user along with the chat ID of the user chat. It then calls delete_expense.py to run to execute the add functionality. Commands used to run this: commands=['delete']

11. command_reminder(message):
Takes 1 argument **message** which contains the message from the user along with the chat ID of the user chat. It then calls reminder.py to run to execute the add functionality. Commands used to run this: commands=['setReminder']

12. reminder_checker():
It operates in an infinite loop, periodically invoking the check_reminders function to ensure users receive their notifications.

# How to run this feature?
This file contains information on the main code.py file from where all features are run. Instructions to run this are the same as instructions to run the project and can be found in README.md.


# UI Improvement 
## MyDollarBot Command Handling

The MyDollarBot Telegram bot features command handling for user interactions. This documentation explains the key components of command handling in MyDollarBot.

## Start and Menu Commands
The /start and /menu commands are handled by the start_and_menu_command function. When a user sends either of these commands, the bot provides a menu with available options.

- /start or /menu command prompts the bot to send a menu to the user.
- The menu displays a list of available commands.

## Menu Option Handlers
Specific commands in the menu are handled by individual command handlers. When a user selects a command from the menu, the bot routes the user to the corresponding functionality.

Available menu commands include:

- /add: Allows users to add a new expense.
- /display: Displays expenses.
- /estimate: Provides an estimate of future expenses.
- /add_recurring: Lets users add recurring expenses.
- /delete_all: Deletes all expenses.
- /delete: Initiates the process to delete a specific expense.
- /budget: Allows users to set, remove, or display budgets.
- /edit: Enables users to edit existing expenses.
- /history: Displays expense history.
- /set_reminder: Configures spending reminders.

### Example:
- User selects /add.
- The bot routes the user to the "add" functionality.
- The add.run function is executed to handle the expense addition.