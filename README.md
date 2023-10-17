<hr>
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
![GitHub Actions](https://github.com/username/repo/workflows/CI/badge.svg)
[![Platform](https://img.shields.io/badge/Platform-Telegram-blue)](https://desktop.telegram.org/)
![GitHub](https://img.shields.io/badge/Language-Python-blue.svg)
[![GitHub contributors](https://img.shields.io/github/contributors/prithvish-doshi-17/MyDollarBot-BOTGo)](https://github.com/prithvish-doshi-17/MyDollarBot-BOTGo/graphs/contributors)
[![DOI](https://zenodo.org/badge/414661894.svg)](https://zenodo.org/badge/latestdoi/414661894)
[![Build Status](https://app.travis-ci.com/sak007/MyDollarBot-BOTGo.svg?branch=main)](https://app.travis-ci.com/github/sak007/MyDollarBot-BOTGo)
[![codecov](https://codecov.io/gh/sak007/MyDollarBot-BOTGo/branch/main/graph/badge.svg?token=5AYMR8MNMP)](https://codecov.io/gh/sak007/MyDollarBot-BOTGo)
[![GitHub issues](https://img.shields.io/github/issues/prithvish-doshi-17/MyDollarBot-BOTGo)](https://github.com/prithvish-doshi-17/MyDollarBot-BOTGo/issues?q=is%3Aopen+is%3Aissue)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/prithvish-doshi-17/MyDollarBot-BOTGo)](https://github.com/prithvish-doshi-17/MyDollarBot-BOTGo/issues?q=is%3Aissue+is%3Aclosed)

![Fork](https://img.shields.io/github/forks/deekay2310/MyDollarBot?style=social)
<hr>

# 💰 DollarBot - Budgeting	 On The Go 💰

DollarBot is an easy-to-use Telegram Bot that assists you in recording your daily expenses on a local system without any hassle 
With simple commands. This bot helps you you maintain and manage your expenses. This bot allows you to:
- Add/Record a new spending
- Calculate the sum of your expenditure for the current day/month
- Display your spending history
- Clear/Erase all your records
- Edit/Change any spending details if you wish to
- Recurring expense:
  Add a recurring expense that adds a certain amount every month to the user's spending, for any given category.
- Custom category:
  User can add a new category and delete an existing category as per the needs
- Budgeting:
  User can see the budget value for the total expense and/or for each of the existing categories in the /display function
- Better visualization:
  Added pie charts, bar graphs with and without budget lines for the user to have a look at the spending history in a better manner
  Added bar graph in the /history command to see spending across different categories
  User can see the daily and monthly expenses for spending history

<hr>
<p align="center">
<a><img  height=360 width=550 
  src="https://github.com/deekay2310/MyDollarBot/blob/c56b4afd4fd5bbfffea0d0a4aade58596a5cb678/docs/0001-8711513694_20210926_212845_0000.png" alt="Expense tracking made easy!"></a>
</p>

## Table of Contents

- [Demo](#demo)
- [Installation](#installation)
  - [Pre-requisites](#pre-requisites)
  - [Actual installation](#actual-installation)
  - [Testing](#testing)
  - [Code Coverage](#code-coverage)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Support](#support)
- [FAQs](#faq)
- [Changelogs](#changelogs)
- [Code of Conduct](#code-of-conduct)



## Installation

### Pre-requisites

Here are some pre-requisites that you'll have to take care of before starting installation:
1. In Telegram App/Desktop, search for "BotFather". Click on "Start", and enter the following command:
```
  /newbot
```
2. Follow the instructions on screen:
    a. Choose a name for your bot. 
    b. Select a username for your bot that ends with "bot". (this is a rule from Telegram's side)

3. BotFather will confirm the creation of your bot and provide a HTTP API access token.
4. Copy and save this token for future use.

### Actual Installation

The below instructions can be followed in order to set-up this bot at your end in a span of few minutes! Let's get started:
1. Clone this repository to your local system.
2. Start a terminal session in the directory where the project has been cloned. Run the following command to install the required dependencies:
```
  pip install -r requirements.txt
```
3. In the directory where this repo has been cloned, please run the below command to execute a bash script to run the Telegram Bot:
```
   ./run.sh
```
(OR)
```
   bash run.sh
```
4. It will ask you to paste the API token you received from Telegram in pre-requisites step 4.
5. A successful run will generate a message on your terminal that says "TeleBot: Started polling." 

6. In the Telegram app, search for your newly created bot by entering the username and open the same. Now, on Telegram, enter the "/start" or "/menu" command, and you are all set to track your expenses!

### Testing

We use pytest to perform testing on all unit tests together. The command needs to be run from the home directory of the project. The command is:
```
python run -m pytest test/
```
(OR)
```
python -m pytest test/
```

### Code Coverage

Code coverage is part of the build. Every time new code is pushed to the repository, the build is run, and along with it, code coverage is computed. This can be viewed by selecting the build, and then choosing the codecov pop-up on hover.

Locally, we use the coverage package in python for code coverage. The commands to check code coverage in python are as follows:

```
coverage run -m pytest test/
coverage report
```

## Usage

We have tried to make this application (bot) as easy as possible. It's pretty self explanatory. You can use this bot to manage and track you daily expenses and not worry about loosing track of your expenses. As we also have given in a functionality of graphing and plotting and history of expenses, it becomes easy for the user to track expenses.

## Configuration

As a user, there's no need to configure any parameters
As a contributor, we have tried to make the system as decoupled as possible so that changes to one module/program doesn't affect other ones. With this being said, here are some configuration knobs that we have exposed for contributors:
1. Adding categories,
2. Removing categories,
3. Graphing changes,
4. Changing Telegram bot names etc.

## Contributing

Thank you for your interest in contributing to DollarBot! Your contributions are highly valued, and this document will help you get started with the process.
We have a fully detailed comprehensive document to look out for if you're looking into contributing towards this project!
Please refer this [CONTRIBUTING.md](CONTRIBUTING.md) file.

## LICENSE

By contributing to DollarBot, you agree that your contributions will be licensed under the project's open-source license. It's important to understand and respect the licensing terms before contributing. The specific license terms for this project can be found in the [LICENSE](LICENSE) file.

## Acknowledgements

Here is a part where we will acknowledge the contributors for this project (sorted alphabetically)
- Ajay
- Jainam
- Keerthana
- Rahul

## Support

[Add here]

## FAQs

1. Will we need a Telegram account to run this?
    A. Yes

2. Will we have to run multiple instances of the server for multiple clients?
    A. No

3. How can we reach out to the developers/contributors?
    A. Look out for the contributors/active developers and contact them.

4. What if I encounter a bug/have a feature request?
    A. File in an Issue and then we can discuss further!

## Changelogs

[Add here]

## Code of Conduct

Please note that we have a [Code of Conduct](CODE_OF_CONDUCT.md) that all contributors are expected to follow. It ensures that our community is welcoming and inclusive.


## What more can be done?
Please refer to the issue list available [here](https://github.com/prithvish-doshi-17/MyDollarBot-BOTGo/issues) to see what more can be done to make MyDollarBot better. Please refer to the MyDollarBot project present [here](https://github.com/prithvish-doshi-17/MyDollarBot-BOTGo/projects) to have a look at the tasks to be done, tasks currently in progress and tasks already done.

## Demo

https://user-images.githubusercontent.com/72677919/140454147-f879010a-173b-47b9-9cfb-a389171924de.mp4

<hr>
<p>Title:'DollarBot'</p>
<p>Version: </p>
<p>Description: 'An easy to use Telegram bot to track everyday expenses'</p>
<p>Authors:'Ajay, Jainam, Keerthana, Rahul'</p>
