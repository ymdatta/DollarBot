<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Money Manager](#money-manager)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Money Manager
<div align="center">
  <img src="docs/logo/logo.png" alt="Project Logo" width="300"/>
</div>


A REST API application for managing expenses. Build your own automation—be it a Telegram bot 🤖, Discord bot, or your own app 📱!

🚨 Spoiler Alert! 🚨 We have built a Telegram bot as a proof of concept! 🤖🎉

<div align="center">
  <img src="http://ForTheBadge.com/images/badges/built-with-love.svg" alt="built_with_love"/>
</div>




---

### Project Overview

https://github.com/user-attachments/assets/91fdf9e0-9489-4e05-ab61-a7599e5463e1

#### Quality

[![badge_pytest_status](https://img.shields.io/badge/PyTest-passing-brightgreen?style=plastic&logo=pytest&logoColor=white)](https://github.com/gitsetgopack/MoneyManager/actions/runs/11639575982)
[![badge_code_coverage](https://img.shields.io/badge/coverage-95%25-brightgreen?style=plastic)](https://github.com/gitsetgopack/MoneyManager/actions/runs/11639575982)
[![badge_total_tests](https://img.shields.io/badge/tests-111-blue?style=plastic&logo=pytest&logoColor=white)](https://github.com/gitsetgopack/hw2/tree/main/tests)
[![badge_pylint](https://img.shields.io/badge/pylint-10.00-brightgreen?style=plastic)](https://github.com/gitsetgopack/MoneyManager/actions/runs/11639575982)
[![badge_black](https://img.shields.io/badge/black_formatter-passing-brightgreen?style=plastic&labelColor=black)](https://github.com/gitsetgopack/MoneyManager/actions/runs/11639575982)
[![badge_mypy](https://img.shields.io/badge/mypy-passing-brightgreen?style=plastic)](https://github.com/gitsetgopack/MoneyManager/actions/runs/11639575982)
[![badge_bandit](https://img.shields.io/badge/bandit-passing-brightgreen?style=plastic)](https://github.com/gitsetgopack/MoneyManager/actions/runs/11639575982)

#### Standards

![black](https://img.shields.io/badge/code%20style-black-black?style=plastic&)
![license](https://img.shields.io/github/license/gitsetgopack/MoneyManager?style=plastic&)
![maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=plastic&)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14027400.svg)](https://doi.org/10.5281/zenodo.14027400)


#### Stats

![pr_open](https://img.shields.io/github/issues-pr/gitsetgopack/MoneyManager?style=plastic&)
![pr_close](https://img.shields.io/github/issues-pr-closed/gitsetgopack/MoneyManager?style=plastic&)
![issue_open](https://img.shields.io/github/issues/gitsetgopack/MoneyManager.svg?style=plastic&)
![issue_close](https://img.shields.io/github/issues-closed/gitsetgopack/MoneyManager.svg?style=plastic&)

![commits_since_last_project](https://img.shields.io/github/commits-since/gitsetgopack/MoneyManager/v2023.f.3.svg?style=plastic&)
![repo_size](https://img.shields.io/github/repo-size/gitsetgopack/MoneyManager?style=plastic&)
![forks](https://img.shields.io/github/forks/gitsetgopack/MoneyManager?style=plastic&)
![stars](https://img.shields.io/github/stars/gitsetgopack/MoneyManager?style=plastic&)
![downloads](https://img.shields.io/github/downloads/gitsetgopack/MoneyManager/total?style=plastic&)

#### Tools & Technologies

[![Python](https://img.shields.io/badge/python%203.12-3670A0?logo=python&logoColor=ffdd54)](https://www.python.org/downloads/release/python-3121/)
[![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](https://www.docker.com/)
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?logo=github&logoColor=white)](https://github.com/)
[![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)](https://www.linux.org/)
[![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/)
[![Zoom](https://img.shields.io/badge/Zoom-2D8CFF?logo=zoom&logoColor=white)](https://www.zoom.com/)
[![DigitalOcean](https://img.shields.io/badge/DigitalOcean-%230167ff.svg?logo=digitalOcean&logoColor=white)]([#](https://www.digitalocean.com/))
[![ChatGPT](https://img.shields.io/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](https://chatgpt.com/)

---

## Installation

### Pre-requisite Tasks

To get started, you'll need to create a Telegram bot through BotFather:

1. Open the Telegram app (desktop or mobile), search for "BotFather," and click on "Start."
2. Send the following command to BotFather:
```bash
/newbot
``` 
4. Follow the instructions to:
- Choose a name for your bot.
- Select a username ending with "bot" (required by Telegram).
5. BotFather will confirm your bot's creation and provide an HTTP API access token—save this token for later.

### Actual Installation

These instructions guide you through setting up the bot's communication and running it:

1. Clone this repository to your local system.
2. Open a terminal session in the directory where the project was cloned and install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```
3. In the same directory, execute the following bash script to start the Telegram Bot:
  ```bash
  ./run.sh
  ```
  OR
  ```bash
  bash run.sh
  ```
4. When prompted, paste the API token you received from BotFather in step 4 of the pre-requisites.

  A successful run will display the message: "TeleBot: Started polling."

5. In the Telegram app, search for your bot using its username, open it, and type /start or /menu to begin using DollarBot for expense tracking!

### Testing

This project uses pytest to test all functionalities of the bot:

Run the following command from the project's root directory to execute all unit tests:
  ```bash
  python -m pytest test/
  ```
Currently, the project includes 100+ tests covering all bot functions.

### Code Coverage

Code coverage is assessed as part of each build. Every time new code is pushed, a build runs, and code coverage is computed.

To check code coverage locally:
  ```bash
  coverage run -m pytest test/
  coverage report
  ```
