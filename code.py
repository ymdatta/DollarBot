#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import logging
import time
import re
import os
import telebot
import sched, time
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

API_TOKEN = "<API_KEY>"

commands = {  # command description used in the "help" command
    'menu'    : 'Display this menu',
    'add'  : 'Record new spending',
    'display' : 'Show sum spendings',
    'history' : 'Show spending history',
    'delete': 'debugger: clear all your records',
    'edit': 'Edit spendings'
    'feedback': 'Yay or Nay? Tell me how I can be better!'
}
