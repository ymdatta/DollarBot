# About MyDollarBot's /add Feature
This feature enables the user to add a new expense to their expense tracker.
Currently we have the following expense categories set by default:

- Food
- Groceries
- Utilities
- Transport
- Shopping
- Miscellaneous

The user can choose a category and add the amount they have spent to be stored in the expense tracker.

# Location of Code for this Feature
The code that implements this feature can be found [here](https://github.com/sak007/MyDollarBot-BOTGo/blob/main/code/add.py)

# Code Description
## Functions

1. run(message, bot):
This is the main function used to implement the add feature. It pop ups a menu on the bot asking the user to choose their expense category, after which control is given to post_category_selection(message, bot) for further proccessing. It takes 2 arguments for processing - **message** which is the message from the user, and **bot** which is the telegram bot object from the main code.py function.

2. post_category_selection(message, bot):
 It takes 2 arguments for processing - **message** which is the message from the user, and **bot** which is the telegram bot object from the run(message, bot): function in the add.py file. It requests the user to select the currency in which they want to enter the amount in and then passes control to post_currency_selection(message, bot, selected_category): for further processing.

3. post_currency_selection(message, bot, selected_category):
 It takes 3 arguments for processing - **message** which is the message from the user, **bot** which is the telegram bot object from the run(message, bot) : function in the add.py file and the selected category by the user. It requests the user to enter the amount they have spent on the expense category chosen and then passes control to post_amount_input(message, bot): for further processing.

4. post_amount_input(message, bot, selected_category, selected_currency):
 It takes 4 arguments for processing - **message** which is the message from the user, **bot** which is the telegram bot object from the post_category_selection(message, bot): function in the add.py file, the selected category and selected currency by the user. It takes the amount entered by the user, validates it with helper.validate() and then calls add_user_record to store it.

5. add_user_record(chat_id, record_to_be_added):
 Takes 2 arguments - **chat_id** or the chat_id of the user's chat, and **record_to_be_added** which is the expense record to be added to the store. It then stores this expense record in the store.

# How to run this feature?
Once the project is running(please follow the instructions given in the main README.md for this), please type /add into the telegram bot.

Below you can see an example in text format:

Krodhit Balak, [22-11-2023 20:11]
/add

SEproj3test_bot, [22-11-2023 20:11]
Select Category

Krodhit Balak, [22-11-2023 20:11]
Groceries

SEproj3test_bot, [22-11-2023 20:11]
Select Currency

Krodhit Balak, [22-11-2023 20:11]
INR

SEproj3test_bot, [22-11-2023 20:11]
How much did you spend on Groceries? 
(Enter numeric values only)

Krodhit Balak, [22-11-2023 20:12]
200

SEproj3test_bot, [22-11-2023 20:12]
The following expenditure has been recorded: You have spent $2.4 for Groceries on 22-Nov-2023 20:12 from Checking account
