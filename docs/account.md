# About MyDollarBot's /add Feature
This feature enables the app to have inflow of money. Currently, inflow of money
is supported for two accounts:

- Checking
- Savings

The user can:

-   Add balance to any account.
-   Change account before registering an expense.
-   Download expense record in csv, pdf format that includes account information.
-   Send a csv expenses record via email to any specified address. 
-   If an expense exceeds balance amount in an account, the expense is denied and a error is shown.
-   If an expense leads to low balance in the account (<100$), a warning is shown indicating low balance in the account.

# Location of Code for this Feature
The code that implements this feature can be found [here](https://github.com/ymdatta/DollarBot/blob/main/code/account.py)

# Code Description
## Functions

1. run(message, bot):

    This function takes 2 arguments for processing.

    - **message** which is the message from the user on Telegram.
    - **bot** which is the telegram bot object from the main code.py function.

    This is the starting function in the implementation of account feature. It pops up a menu on the telegram asking the user to chose from two different account types, after which control is given to post_category_selection(message, bot) for further processing.

2. post_category_selection(message, bot):

    This function takes 2 arguments for processing.

    - **message** which is the message from the user on Telegram.
    - **bot** which is the telegram bot object from the run(message, bot) function.

    This is the function which gets executed once an account type is selected. It changes current account used for expenses to the one input by the user.

    If an invalid account is selected, it erros out raising an exception indicating that the right category needs to be selected and it provides list of commands to start the next iteration.

4. add_account_record(chat_id, type):

    This function takes 2 arguments for processing.

    - **chat_id** which is the unique ID for a user provided by Telegram.
    - **type** which is the account type user selected for future purchases.

    This function is a helper function, which creates user record if it's a new user. It then updates the account type for expenses based on the inputs from the user.

# How to run this feature?

Once the project is running(please follow the instructions given in the main README.md for this), please type /select_expense_type into the telegram bot.

Below you can see an example in text format:

```
Mohan Y, [11/27/23 3:42 PM]
/select_expenses_account

Bot, [11/27/23 3:42 PM]
Select Category

Mohan Y, [11/27/23 3:42 PM]
Checking

Bot, [11/27/23 3:42 PM]
Expenses account changed to: Checking.
```