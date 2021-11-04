# TrackMyDollar V2.0 - Budget On The Go(BOTGo)
<hr>
<p align="center">
<a><img  height=360 width=550 
  src="https://github.com/deekay2310/MyDollarBot/blob/c56b4afd4fd5bbfffea0d0a4aade58596a5cb678/docs/0001-8711513694_20210926_212845_0000.png" alt="Expense tracking made easy!"></a>
</p>
<hr>

![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
[![Platform](https://img.shields.io/badge/Platform-Telegram-blue)](https://desktop.telegram.org/)
![GitHub](https://img.shields.io/badge/Language-Python-blue.svg)

![GitHub contributors](https://img.shields.io/github/contributors/sak007/MyDollarBot-BOTGo)

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

## New Features and Delta

- Budgeting: Overall
- Budgeting: Category-wise
- Display: Bar graphs
- Edit Feature: Improved to use calendar
- Expense Estimator
- Code Refactoring: Modularization
- Code Coverage: Test Cases

## Work for the upcoming iteration

- Display: Add pie charts
- New Feature: Custom Categories -  Lets the user add their own categories which can then be used to add expenses.
- Display: Add budgeting information inside display to show which categories are exceeding budget
- Recurring expense: Add a recurring expense that adds a certain amount every week to the user's spending. 
- Web hosting: host the project on Heroku or any other cloud provider for high availability.
- UI beautification: beautify the UI and the messages sent to the user to improve user experience and readability.

## Demo
https://user-images.githubusercontent.com/15325746/135395315-e234dc5e-d891-470a-b3f4-04aa1d11ed45.mp4

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
