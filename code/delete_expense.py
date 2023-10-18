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
            # Save the updated user_data back to your database
            with open('expense_record.json', 'w') as file:
                json.dump(user_data, file, indent=4)
            return f"Expense '{deleted_expense}' has been deleted."
    return "Expense deletion failed."

