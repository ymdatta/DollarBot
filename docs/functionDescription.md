## Edit Functionality
This function is used to edit any expenses which was recorded earlier

edit1 - This function is triggered when the user types '/edit' in telegram bot chat. It will ask user to enter date and the category of the transaction they want to update. Once user gives the correct details, function edit2 is triggered

edit2 - Based on user's input from edit1, this function checks the field the user wants to update (Date, Category or Cost). The choice selected by the user is passed to edit3

edit3 - Based on the information received from edit2, one of the following function is triggered: edit_cat, edit_date or edit_cost

edit_cat - This function is triggered if user inputs Category in edit2 function. It will ask user for new category and update the record accordingly

edit_date - This function is triggered if user inputs Date in edit2 function. It will ask user for new date and update the record accordingly

edit_cost - This function is triggered if user inputs Cost in edit2 function. It will ask user for new cost and update the record accordingly
