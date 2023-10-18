import helper
import json

def delete_expense(chat_id, expense_index):
    user_data = helper.read_json()
    if str(chat_id) in user_data:
        user_info = user_data[str(chat_id)]
        if "data" in user_info and expense_index < len(user_info["data"]):
            deleted_expense = user_info["data"].pop(expense_index)
            print(user_data)
            print(deleted_expense)
            with open('expense_record.json', 'w') as file:
                json.dump(user_data, file, indent=4)
            return f"Expense '{deleted_expense}' has been deleted."
    return "Expense deletion failed."


def run(message, bot):
    chat_id = message.chat.id
    user_data = helper.read_json()
    print(chat_id)
    # print(user_data)

    if str(chat_id) not in user_data:
        bot.send_message(chat_id, "You don't have any expenses to delete.")
        return

    user_info = user_data[str(chat_id)]
    # print("\n\n",user_info)

    if "data" not in user_info or not user_info["data"]:
        bot.send_message(chat_id, "You don't have any expenses to delete.")
        return

    expenses = user_info["data"]
    expense_text = "Select the expense you want to delete:\n"

    for i, expense in enumerate(expenses):
        expense_text += f"{i + 1}. {expense}\n"

    bot.send_message(chat_id, expense_text)
    bot.register_next_step_handler(message, confirm_deletion, chat_id, bot)


def confirm_deletion(message, chat_id, bot):
    if message.text.isdigit():
        expense_index = int(message.text) - 1
        result_message = delete_expense(chat_id, expense_index)
        bot.send_message(chat_id, result_message)
    else:
        bot.send_message(chat_id, "Please enter a valid expense number to delete.")