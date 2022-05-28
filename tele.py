import os
import telebot
import main as hltv
import datetime
import time
import config
import re
import threading
from pymongo import MongoClient
from bson.objectid import ObjectId

cluster = MongoClient(config.connect_mongodb())
bot = telebot.TeleBot(config.get_api())

#Project Created by Michael May

def get_team_name(id):
    team_name = str(hltv.get_team_info(id)['team-name'])
    team_name = string_format(team_name)
    return team_name    

def string_format(income_str):
    income_str = income_str.replace("b'", '')
    income_str = income_str.replace("'", '')
    return income_str


def check_followers():
    mydb = cluster.telebot_db

    while True:
        # sleep until 8AM
        t = datetime.datetime.today()
        future = datetime.datetime(t.year,t.month,t.day,4, 0)
        if t.timestamp() >= future.timestamp():
            future += datetime.timedelta(days=1)
        time.sleep((future-t).total_seconds())
        for document in mydb.follow_data.find():
            message_string = ""
            for team in document["team_id"]:
                match_list = hltv.get_matches()
                team_name = get_team_name(team)
                for i in match_list:
                    if (i['date'] == str(datetime.date.today())) or i['date'] == str(datetime.date.today() + datetime.timedelta(days=1)) or i['date'] == str(datetime.date.today() + datetime.timedelta(days=2)):
                        if team_name == string_format(str(i['team1'])):
                            message_string += team_name + " plays against " + string_format(str(i['team2'])) + " on " + string_format(str(i['date'])) + " at " + string_format(str(i['time'])) + " CET\n"
                        elif team_name == string_format(str(i['team2'])):
                            message_string += team_name + " plays against " + string_format(str(i['team1'])) + " on " + string_format(str(i['date'])) + " at " + string_format(str(i['time'])) + " CET\n"
            if message_string != "":
                bot.send_message(int(document["group_id"]), "@" + str(document["user_at"]) + "\n " + message_string)

@bot.message_handler(commands=['upcomingmatches'])
def upcomingmatches(message):
    match_info = hltv.get_matches()
    match_upcoming = []
    match_string = ""
    #Match information stored in match_upcoming array
    #Match_string used to create message bot sends to user

    for i in match_info:
        if (i['date'] == str(datetime.date.today())) or i['date'] == str(datetime.date.today() + datetime.timedelta(days=1)):
            match_upcoming.append(i)
    #Adds all matches on current day or next day to upcoming matches list
    if len(match_upcoming) != 0:
        for j in match_upcoming:
            match_string += str(j['date']) + " | " + str(j['event']) + ": " + str(j['team1']) + " vs. " + str(j['team2']) + " " + str(j['time']) + " CET\n\n"
    match_string = match_string.replace("b'", '')
    match_string = match_string.replace("'", '')
    #Removes unnecessary characters from string
    bot.reply_to(message, match_string)

@bot.message_handler(commands=['getresults'])
def todaysresults(message):
    results_info = hltv.get_results()
    results_string = ""
    x = 0
    for j in results_info:
        if x > 10:
            break
        #inexperienced with python just using x to track placement in array and take
        #the 10 most recent matches to apply
        
        results_string += str(j['team1']) + ": " + str(j['team1score']) + " - " + str(j['team2score']) + " " + str(j['team2']) + " \n\n"
        x = x + 1
    results_string = results_string.replace("b'", '')
    results_string = results_string.replace("'", '')
    #Removes unnecessary characters from string
    bot.reply_to(message, results_string)
@bot.message_handler(commands=['getteams'])
def getteams(message):
    teams_list = hltv.top30teams()
    teams_string = ""

    for team in teams_list:
        teams_string += "ID: (" + str(team['team-id']) + ")  | " + team['name'] + " |  Rank #" + str(team['rank']) + "\n"
    bot.reply_to(message, teams_string)

@bot.message_handler(commands=['getteaminfo'])
def getteaminfo(message):
    team_selected = message.text.replace("/getteaminfo", '')
    check_id = "[0-9]{3,}[0-9]"
    team_data = ""
    team_string = ""

    if team_selected == '':
        bot.reply_to(message, "Invalid Input: Please input an ID or team name following the command.")
        #Checks if user added a message alongside the command
    elif re.search(check_id, team_selected):
        #Using regex to check if input is an id or team name
        team_data = hltv.get_team_info(int(team_selected))
        team_string += "Team: " + str(team_data['team-name']) + " | ID (" + str(team_selected) + ")  |  " + "Roster: \n"
        for player in team_data['current-lineup']:
            team_string += player['nickname'] + "\n"

        team_string = team_string.replace("b'", '')
        team_string = team_string.replace("'", '')
        #Clean up string remove unnecessary characters
        bot.reply_to(message, team_string)
    else:
        team_selected = team_selected.replace(" ", "")
        team_selected = team_selected.lower()
        #make sure message is formatted correctly
        team_collection = cluster.telebot_db.team_list
        team_collection = team_collection.find_one({"name": team_selected})
        #query the name
        if team_collection == None:
            bot.reply_to(message, "Team not found. Make sure name was entered correctly if it was the team might not yet be added to the database.")
        else:
            team_data = hltv.get_team_info(team_collection['_id'])
            team_string += "Team: " + str(team_data['team-name']) + " | ID (" + str(team_collection['_id']) + ")  |  " + "Roster: \n"
            for player in team_data['current-lineup']:
                team_string += player['nickname'] + "\n"

            team_string = team_string.replace("b'", '')
            team_string = team_string.replace("'", '')
            #Clean up string remove unnecessary characters
            bot.reply_to(message, team_string)

@bot.message_handler(commands=['followteam'])
def followteam(message):
    user_at = message.from_user.username
    chat_id = message.chat.id
    user_id = message.from_user.id
    follow_col = cluster.telebot_db.follow_data
    team_data = cluster.telebot_db.team_list
    team_id = -1
    team_name = ""
    #collect user data from message

    #team data and check if team entered is valid
    team_selected = message.text.replace("/followteam ", '')
    check_id = "[0-9]{3,}[0-9]"

    if team_selected == '':
        bot.reply_to(message, "Invalid Input: Please input an ID or team name following the command.")
        #Checks if user added a message alongside the command
    elif re.search(check_id, team_selected):
        #Using regex to check if input is an id or team name
        team_id = team_selected
    else:
        team_selected = team_selected.replace(" ", "")
        team_selected = team_selected.lower()
        #make sure message is formatted correctly
        team_collection = cluster.telebot_db.team_list
        team_collection = team_collection.find_one({"name": team_selected})
        #query the name
        if team_collection == None:
            bot.reply_to(message, "Team not found. Make sure name was entered correctly if it was the team might not yet be added to the database.")
        else:
            team_id = team_collection['_id']
            #assign id to team id


    #New user data; #If team data is valid team_id will not equal negative one 
    if team_id != -1:
        if (follow_col.find_one({"user_id": int(user_id)}) == None) or (follow_col.find_one({"group_id": int(chat_id)}) == None):
            follow_col.insert_one({"user_id": int(user_id), "group_id": int(chat_id), "user_at": user_at, "team_id": [int(team_id)]})
            team_name = get_team_name(team_id)
            bot.reply_to(message, "You are now following " + team_name)
        else:
            if follow_col.find_one({"user_id": int(user_id), "group_id": int(chat_id), "team_id": int(team_id)}) == None:
                follow_col.update_one({"user_id": int(user_id), "group_id": int(chat_id)}, {"$push": {"team_id": int(team_id)}})
                team_name = get_team_name(team_id)
                bot.reply_to(message, "You are now following " + team_name)
            else:
                bot.reply_to(message, "You are already following this team.")

@bot.message_handler(commands=['helpcsgo'])
def help(message):
    bot.reply_to(message, ("Hello Welcome to the CS:GO HLTV Bot for Telegram this app\n" 
                          "is powered by the pyTelegramBot API and HLTV-API.\n\n\n"
                             
                          "Currently functioning commands are\n\n"
                          "/upcomingmatches(Displays matches upcoming today and tomorrow)\n\n"
                          "/getresults(Displays last 10 match results)\n\n"
                          "/getteams(Displays a list of the top 30 teams and their rankings)\n\n"
                          "/getteaminfo TeamID/TeamName  (Insert name or ID following command and get the roster of the team you searched)\n\n"
                          "/followteam TeamID/TeamName (Insert team name or ID to follow team)\n\n\n"

                          "Follow this project on github here:\n\n"
                          "https://github.com/mm2023git/Telegram-HLTV-Bot\n\n"
                           ))

follow_thread = threading.Thread(target=check_followers)

follow_thread.start()

bot.polling()

