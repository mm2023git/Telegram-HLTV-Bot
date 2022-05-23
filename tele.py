import os
import telebot
import main as hltv
import datetime
import config

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

@bot.message_handler(commands=['helpcsgo'])
def help(message):
    bot.reply_to(message, """Hello Welcome to the CS:GO HLTV Bot for Telegram this app\n 
                             is powered by the pyTelegramBot API and HLTV-API found here\n
                             https://github.com/SocksPls/hltv-api\n
                             https://github.com/eternnoir/pyTelegramBotAPI\n
                             
                             Currently functioning commands are\n
                             /upcomingmatches(Displays matches upcoming today and tomorrow)\n
                             /getresults(Displays last 10 match results)\n
                             \n """)


bot.polling()

