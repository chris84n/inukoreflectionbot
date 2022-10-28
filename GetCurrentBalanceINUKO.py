#!/usr/bin/python

# GetCurrentBalanceINUKO.py
# Script connects to BSCScan API to get current balance of INUKO wallet for reflection holder.
# It checks, if current value is lower than last saved value and notify registered telegram 
# chats by Telegram Bot API about payout of reflections 
# To get notified a registration with help of the bot ist required. 


##################
#Imports
#################
from operator import truediv
import requests
import json
from decimal import Decimal
from pathlib import Path
import sqlite3
from sqlite3 import Error
import telebot

##############
#Telegram Bot
##############

#Definition of telegram bot with API created by BotFather in Telegram
bot = telebot.TeleBot('API-KEY-HERE')


############
#SQLLite DB
############
#Path to SQLite3 database file where chatids are saved
inuko_db_file="/srv/inuko_reflections/inuko_reflections.db"

####################
#BSCScan API Infos
####################

#Contract Address of INUKO Finance
contract_address="0xEa51801b8F5B88543DdaD3D1727400c15b209D8f"

#Holder address for filter wallet for reflections
holder_address="0xEa51801b8F5B88543DdaD3D1727400c15b209D8f"

#BSCScan API Key
api_key="API-KEY-BSCScan-HERE"

#BSCScan API URL
bscscan_api="https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress="+contract_address+"&address="+holder_address+"&tag=latest&apikey="+api_key

###################
#Other definitions
##################
filename_last_balance="/srv/inuko_reflections/current_balance_inuko.json"


#Get Current Date in UTC
#current_time=strftime("%Y-%m-%d %H:%M:%S",gmtime())

####################
# Functions
####################

#################################
#    File Operation functions
#################################

#Read current value from file
def read_current_value(filename):
    my_file = Path(filename)
    if my_file.is_file():
       with open(filename,'r') as f:
         data = json.load(f)
         return data["Balance"]
    else:
       return None


#Write to file
def write_file(filename,temp_dict):
     with open(filename,'w') as json_file:
       json.dump(temp_dict,json_file)



###########################################
#   SQLite3 functions to query chatids info
###########################################

#Function to create connection to database
def create_connection(db_file):
  """ create database connection to SQLite database specified by db_file """
  conn = None
  try:
   conn = sqlite3.connect(db_file)
  except Error as e:
   print(e)

  return conn


#Get ChatIDs and from DB
def getall_chatid_in_db():
 conn = create_connection(inuko_db_file)
 cur = conn.cursor()
 cur.execute("SELECT chatid FROM t_inuko_registered_chatids")
 rows = cur.fetchall()
 if len(list(rows)) > 0:
  return list(rows)
 else:
  return None


########################################################
#   Telegram function to send message to telegram chats
########################################################

#Send message to telegram
def SendMessageToTelegram(message):
 chatids=getall_chatid_in_db()
 if(chatids != None):
  for chatid_row in chatids:
   chatid = chatid_row
   bot.send_message(chatid, message)
 else:
  print("No chat ids in DB found")

#######################################################################################
# Start of process
#######################################################################################

#Get Data from BSCScan API
response = requests.get(bscscan_api)
response_out =  response.json()

balance = response_out["result"]
balance_dec = Decimal(balance)/1000000000000000000
balance=float(balance_dec)


#Check balance current vs saved
curr_balance = {"Balance":balance}
if(read_current_value(filename_last_balance) == None):
 #If file was not found or file empty, then create file and save value
 write_file(filename_last_balance,curr_balance)
else:
 #Check if current balance is lower than last saved value
 if(curr_balance["Balance"] < read_current_value(filename_last_balance)):
   #Send Message to registered Telegram Chats
   SendMessageToTelegram("INUKO Reflection Bot - Information - Rewards where payed out")
   # Save current value
   write_file(filename_last_balance,curr_balance)
 else:
   # Just save current value to file
   write_file(filename_last_balance,curr_balance)

