# 💰 TrackMyDollar V2.0 - Budget On The Go(BOTGo) 💰
<hr>
<p align="center">
<a><img  height=360 width=550 
  src="https://github.com/deekay2310/MyDollarBot/blob/c56b4afd4fd5bbfffea0d0a4aade58596a5cb678/docs/0001-8711513694_20210926_212845_0000.png" alt="Expense tracking made easy!"></a>
</p>
<hr>

![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
[![Platform](https://img.shields.io/badge/Platform-Telegram-blue)](https://desktop.telegram.org/)
![GitHub](https://img.shields.io/badge/Language-Python-blue.svg)
[![GitHub contributors](https://img.shields.io/github/contributors/sak007/MyDollarBot-BOTGo)](https://github.com/sak007/MyDollarBot-BOTGo/graphs/contributors)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5542548.svg)](https://doi.org/10.5281/zenodo.5542548)
[![Build Status](https://app.travis-ci.com/sak007/MyDollarBot.svg?branch=backlogs)](https://app.travis-ci.com/github/sak007/MyDollarBot-BOTGo)
[![codecov](https://codecov.io/gh/sak007/MyDollarBot-BOTGo/branch/main/graph/badge.svg?token=5AYMR8MNMP)](https://codecov.io/gh/sak007/MyDollarBot-BOTGo)
[![GitHub issues](https://img.shields.io/github/issues/sak007/MyDollarBot-BOTGo)](https://github.com/sak007/MyDollarBot-BOTGo/issues?q=is%3Aopen+is%3Aissue)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/sak007/MyDollarBot-BOTGo)](https://github.com/sak007/MyDollarBot-BOTGo/issues?q=is%3Aissue+is%3Aclosed)
![Lines of code](https://img.shields.io/tokei/lines/github/sak007/MyDollarBot-BOTGo)

<hr>

## About TrackMyDollar

TrackMyDollar is an easy-to-use Telegram Bot that assists you in recording your daily expenses on a local system without any hassle.  
With simple commands, this bot allows you to:
- Add/Record a new spending
- Show the sum of your expenditure for the current day/month
- Display your spending history
- Clear/Erase all your records
- Edit/Change any spending details if you wish to

## What's new? (Delta, New Features)

- Code Refactoring: Modularization
  The codebase was inside a single file containing more than 1000 lines of code when we began our work. To make it modular, easier to understand, and easier to contribute to, we have performed a complete modularization of the codebase into 13 separate files, modularizing for functionality. 

- Budgeting: Overall
  We have introduced a new feature to allow users to create a budget to track their expenses across categories. Using this, after adding a budget, whenever the user adds a new expense, this gets deducted from the budget and the remaining amount is shown to the user.

- Budgeting: Category-wise
  We have introduced a new categorical budget feature to allow users to create a budget to track their expenses for each categories they require it for. Using this, after adding a budget for a particular category, whenever the user adds a new expense to that category, this gets deducted from the budget and the remaining amount is shown to the user for that budget category.
  
- Display: Bar graphs
  This features allows for a bar graph showing the expenditures made across categories through a bar graph. This allows users to understand their better. 

- Edit Feature: Improved to show dates for deletion
  The edit feature now shows a list of expenses and dates for the user to choose from and delete. The user can choose the ones they would like to delete instead of manually typing in the date of the expense.

- Expense Estimator
  To allow for user to estimate their expenses for the future, we have implemented a estimator which employs the user's historical data to predict their next month's expenses. 

- Code Coverage: Test Cases
  The project only had a single test case when we took over the project. From there, we have added test cases for both existing and new features. Our code coverage now stands at 90%, with over 110+ test cases.

## Work for the upcoming iteration

- Display: Add pie charts
- New Feature: Custom Categories -  Lets the user add their own categories which can then be used to add expenses.
- Display: Add budgets inside display function's output so user can see budget alongside spending.
- Recurring expense: Add a recurring expense that adds a certain amount every week to the user's spending. 
- Web hosting: host the project on Heroku or any other cloud provider for high availability.
- Add: Add calendar in UI to allow user to choose dates to add expenses.
- UI beautification: beautify the UI and the messages sent to the user to improve user experience and readability.

## Demo

https://app.animaker.com/animo/fXrA8Oa8bGfiD4ft/

## Installation guide

The below instructions can be followed in order to set-up this bot at your end in a span of few minutes! Let's get started:

1. Clone this repository to your local system.

2. Start a terminal session in the directory where the project has been cloned. Run the following command to install the required dependencies:
```
  pip install -r requirements.txt
```

3. In Telegram, search for "BotFather". Click on "Start", and enter the following command:
```
  /newbot
```
Follow the instructions on screen and choose a name for your bot. After this, select a username for your bot that ends with "bot".

4. BotFather will now confirm the creation of your bot and provide a TOKEN to access the HTTP API - copy and save this token for future use.

5. In the directory where this repo has been cloned, please run the below command to execute a bash script to run the Telegram Bot:
```
   ./run.sh
```
(OR)
```
   bash run.sh
```
Please note that it will ask you to paste the API token you received from Telegram in step 4.
A successful run will generate a message on your terminal that says "TeleBot: Started polling." 

6. In the Telegram app, search for your newly created bot by entering the username and open the same. Now, on Telegram, enter the "/start" or "/menu" command, and you are all set to track your expenses!

## Testing

We use pytest to perform testing on all unit tests together. The command needs to be run from the home directory of the project. The command is:
```
python run -m pytest test/
```

## Code Coverage

Code coverage is part of the build. Every time new code is pushed to the repository, the build is run, and along with it, code coverage is computed. This can be viewed by selecting the build, and then choosing the codecov pop-up on hover.

Locally, we use the coverage package in python for code coverage. The commands to check code coverage in python are as follows:

```
coverage run -m pytest test/
coverage report
```

## Notes:
You can download and install the Telegram desktop application for your system from the following site: https://desktop.telegram.org/


<hr>
<p>Title:'Track My Dollar'</p>
<p>Version: '1.5'</p>
<p>Description: 'An easy to use Telegram Bot to track everyday expenses'</p>
<p>Authors(Iteration 1.5):'Athithya, Subramanian, Ashok, Zunaid, Rithik'</p>
<p>Authors(Iteration 1):'Dev, Prakruthi, Radhika, Rohan, Sunidhi'</p>
