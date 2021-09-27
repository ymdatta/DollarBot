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
    'menu'    : 'Display the menu',
    'add'  : 'Record/Add a new spending',
    'display' : 'Show sum of spendings',
    'history' : 'Display spending history',
    'delete': 'Clear/Erase all your records',
    'edit': 'Edit/Change spending details'
}
