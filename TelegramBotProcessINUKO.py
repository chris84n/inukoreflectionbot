#!/usr/bin/python3
#############
# Description
#############
# Process for Telegram Bot - INUKO Finance Reflection Bot
# Bot checks messages which send in groups, private chats where bot is member of
# It looks for special commands for registration, deregistration of groups/private chats chatids
# Also it is possible for users in groups / private chats to get the last saved balance
# of script GetCurrentBalanceINUKO.py on demand
#
####################################################################################################


###########
# Imports
###########
import sqlite3
from sqlite3 import Error
from telebot.async_telebot import AsyncTeleBot
import asyncio
from decimal import Decimal
from pathlib import Path
import json
#Import inuko_config.py file with API keys for Telegram Bot and BSCScan
import inuko_config

################################
# Balance Info
################################

################
#    Definitions
################
filename_last_balance="/srv/inuko_reflections/current_balance_inuko.json"
filename_last_payout="/srv/inuko_reflections/last_payout.json"

###############
#    Functions
################
def read_current_value(filename,key):
    my_file = Path(filename)
    if my_file.is_file():
       with open(filename,'r') as f:
         data = json.load(f)
         return data[key]
    else:
       return None

################################
# SQLIte database
################################

#####################
#      Definitions
#####################

#Path to SQLite DB file
inuko_db_file="/srv/inuko_reflections/inuko_reflections.db"

################
#    Functions
###############

#Create Database connection
def create_connection(db_file):
  """ create database connection to SQLite database specified by db_file """
  conn = None
  try:
   conn = sqlite3.connect(db_file)
   print("DB connection successfully")
  except Error as e:
   print(e)

  return conn

# Register Chat in DB
def register_chatid_in_db(chatid,conn):
 sql='''INSERT INTO t_inuko_registered_chatids (chatid) VALUES (?) '''
 cur = conn.cursor()
 cur.execute(sql,(chatid,));
 conn.commit()
 return cur.lastrowid

# Unregister Chat in DB
def unregister_chatid_in_db(chatid,conn):
 sql='''DELETE FROM t_inuko_registered_chatids WHERE chatid=?'''
 cur = conn.cursor()
 cur.execute(sql,(chatid,));
 conn.commit()

# Check if chatid already in database (chat id registered)
def check_chatid_in_db(chatid,conn):
 cur = conn.cursor()
 cur.execute("SELECT * FROM t_inuko_registered_chatids WHERE chatid=?",(chatid,))
 rows = cur.fetchall()
 if len(list(rows)) == 1:
  print("chatid found in db")
  return True
 else:
  print("chatid not found in db")
  return False

######################################################
# TELEGRAM BOT
######################################################

###################
#      Definitions
###################

# Telegram Bot definition with API Key
bot = AsyncTeleBot(inuko_config.telegram_bot_api)

##################
# Bot handlers
##################

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am Inuko Reflection Bot.
I am here to give you informations as soon as reflections in Inuko Finance project where deployed!\
You can register this group/private chat at the bot and get messages with /register_inukoreflection_bot and \
unregister with /unregister_inukoreflection_bot \
In Addition you can get the current value of balance for reflections with /balance_inukoreflection_bot
""")

#Handle '/register_inukoreflection_bot'
@bot.message_handler(commands=['register_inukoreflection_bot'])
async def send_register(message):
    conn = create_connection(inuko_db_file)
    with conn:
     chatid=message.json["chat"]["id"]
     if(check_chatid_in_db(chatid,conn)):
      print("Send to telegram: already registered")
      await bot.reply_to(message,"""Already registered""")
     else:
      print("Register chat in database")
      register_chatid_in_db(chatid,conn)
      print("Check if registration was ok")
      if(check_chatid_in_db(chatid,conn)):
       print("Send registration message to telegram bot")
       await bot.reply_to(message,"""Registered successfully""")
      else:
       print("Send failed registration message to telegram bot")
       await bot.reply_to(message,"""Failed to register""")

#Handle '/unregister_inukoreflection_bot'
@bot.message_handler(commands=['unregister_inukoreflection_bot'])
async def send_unregister(message):
    conn = create_connection(inuko_db_file)
    with conn:
     chatid=message.json["chat"]["id"]
     if(check_chatid_in_db(chatid,conn)):
      unregister_chatid_in_db(chatid,conn)
      if(check_chatid_in_db(chatid,conn)):
       await bot.reply_to(message,"""Failed to unregister""")
      else:
       await bot.reply_to(message,"""Successfully unregistered""")
     else:
       await bot.reply_to(message,"""Not registered, can not get unregistered! """)

#Handle '/balance_inukoreflection_bot'
@bot.message_handler(commands=['balance_inukoreflection_bot'])
async def send_current_balance(message):
  print("Send current balance")
  if(read_current_value(filename_last_balance,"Balance") == None):
   await bot.reply_to(message,"Current balance is currently not available")
  else:
   cur_balance=read_current_value(filename_last_balance,"Balance")
   last_payout=read_current_value(filename_last_payout,"LastPayout")
   rest=25000.0-cur_balance
   cur_balance=str(cur_balance)
   last_payout=str(last_payout)
   await bot.reply_to(message,"Current balance is "+cur_balance+" INUKO!\nRequired to next reflection payout: "+str(rest)+ " INUKO.\nLast payout:\n"+last_payout)

# Any other message send in groups / private chats will be ignored, because no handler defined!

#########################################################
# Start of process
########################################################
#Start async polling process of Telegram Bot

#########################################################
# MAIN
########################################################

def main():
 asyncio.run(bot.polling())

######################################################
# START
#####################################################

if __name__ == '__main__':
 main()


