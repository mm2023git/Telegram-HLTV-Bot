import os
import telebot
import main as hltv
import datetime
import config
import re
from pymongo import MongoClient
from bson.objectid import ObjectId

cluster = MongoClient(config.connect_mongodb())
bot = telebot.TeleBot(config.get_api())
#Project Created by Michael May

@bot.message_handler(commands=['upcomingmatches'])
def upcomingmatches(message):
    match_info = hltv.get_matches()
    match_upcoming = []
    match_string = ""
    #Match information stored in match_upcoming array
    #Match_string used to create message bot sends to user
    for i in match_info:
        if i['date'] == str((datetime.date.today() + datetime.timedelta(days=1))) or i['date'] == str(datetime.date.today):
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

@bot.message_handler(commands=['helpcsgo'])
def help(message):
    bot.reply_to(message, """Hello Welcome to the CS:GO HLTV Bot for Telegram this app\n 
                             is powered by the pyTelegramBot API and HLTV-API\n
                             
                             Currently functioning commands are\n
                             /upcomingmatches(Displays matches upcoming today and tomorrow)\n
                             /getresults(Displays last 10 match results)\n
                             /getteams(Displays a list of the top 30 teams and their rankings)\n
                             /getteaminfo TeamID/TeamName  (Insert name or ID following command and get the roster of the team you searched)\n\n

                             Follow this project on github here:
                             https://github.com/mm2023git/Telegram-HLTV-Bot
                             \n """)


bot.polling()

