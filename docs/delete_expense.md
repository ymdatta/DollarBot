# About MyDollarBot's /delete Feature
The Expense Deletion feature in MyDollarBot allows users to delete specific expenses from their expense records. This feature involves multiple functions to handle the process.

# Location of Code for this Feature
The code that implements this feature can be found [here](https://github.com/rrajpuro/DollarBot/blob/main/code/delete_expense.py)

## delete_expense(chat_id, expense_index)
This function handles the deletion of a user's expense. It takes two arguments, chat_id (the user's chat ID) and expense_index (the index of the expense to be deleted). The process includes reading the user's data from a JSON file, removing the specified expense, and saving the updated data back to the database. If the deletion is successful, it returns a confirmation message; otherwise, it returns a failure message.

## run(message, bot)
The run function initiates the process of deleting an expense. It takes two parameters, message (the user's message) and bot (the Telegram bot object). This function checks if the user has expenses to delete. If the user exists in the data and has expenses, it proceeds to list the expenses for the user to choose from.

## confirm_deletion(message, chat_id, bot)
The confirm_deletion function confirms the user's choice of an expense for deletion. It takes three arguments: message (the user's message), chat_id (the user's chat ID), and bot (the Telegram bot object). If the user provides a valid expense number, the function calls delete_expense to perform the deletion and sends a confirmation message. If the user's input is not valid, it prompts them to enter a valid expense number.

To use this feature:
1. Start the MyDollarBot project.
2. Open a chat with the bot in Telegram.
3. Type /delete to initiate the expense deletion process.
4. Follow the prompts to select the expense to delete.
