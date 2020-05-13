from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from itertools import chain

#my own imports
import string
import telegram
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler


#Alphabet strings for looping new entries
alphabet = list(string.ascii_lowercase)
print(alphabet)



# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
EXPENSES_SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'
Initial_RANGE_NAME = 'Sheet1!C4'


"""Shows basic usage of the Sheets API.
Prints values from a sample spreadsheet.
"""
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

print('Setting to bot')
tok = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telegram.Bot(token = tok)



updater = Updater(token=tok)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Budget and Expenses Bot")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def expenseCollector(bot, update):
    user = update.message.from_user
    expense_text = update.message.text
    expense_date = update.message.date.strftime("%m/%d/%Y")


##################################
    expense_values = expense_text.split()
    c = 2
    #put values
    range_names = Initial_RANGE_NAME
    result = service.spreadsheets().values().batchGet(
        spreadsheetId=EXPENSES_SPREADSHEET_ID, ranges=range_names).execute()
    ranges = result.get('valueRanges', [])


    while ranges[0].get('values', 0) != 0:
        c += 1
#         range_names_old = range_names
        range_string = list(range_names)
        range_string[-2] = alphabet[c]
        range_names = "".join(range_string)
#         result_old = service.spreadsheets().values().batchGet(
#             spreadsheetId=EXPENSES_SPREADSHEET_ID, ranges=range_names_old).execute()
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=EXPENSES_SPREADSHEET_ID, ranges=range_names).execute()
#         ranges_old = result_old.get('valueRanges', [])
        ranges = result.get('valueRanges', [])
#         if ranges[0].get('values', 0) == ranges_old[0].get('values', 0):
#             ranges = result.get('valueRanges', [])
        print(range_names)

        print(expense_date)
        print(ranges[0].get('values', 0))

        turn = 0

        if ranges[0].get('values', 0) != 0:
            if ranges[0].get('values', 0)[0][0] == expense_date.strip():
                print("ok")
                turn = 1
                break


    print(expense_date)

    print(range_names)

    values = [
        [
            expense_date
        ],
        # Additional rows ...
    ]
    body = {
        'values': values
    }


    result = service.spreadsheets().values().update(
        spreadsheetId=EXPENSES_SPREADSHEET_ID, range=range_names,
        valueInputOption="RAW", body=body).execute()

    if expense_values[0].lower() == "mobile":
        range_string = list(range_names)
        range_string[-1] = "5"
        range_names = "".join(range_string)

    elif expense_values[0].lower() == "food":
        range_string = list(range_names)
        range_string[-1] = "6"
        range_names = "".join(range_string)

    elif expense_values[0].lower() == "invest":
        range_string = list(range_names)
        range_string[-1] = "7"
        range_names = "".join(range_string)

    elif expense_values[0].lower() == "house":
        range_string = list(range_names)
        range_string[-1] = "8"
        range_names = "".join(range_string)

    elif expense_values[0].lower() == "other":
        range_string = list(range_names)
        range_string[-1] = "9"
        range_names = "".join(range_string)
    print("value ", range_names)

    print(expense_values[1])
    new_value = int(expense_values[1])

    if turn == 1:
        result = service.spreadsheets().values().batchGet(
                spreadsheetId=EXPENSES_SPREADSHEET_ID, ranges=range_names).execute()
        ranges = result.get('valueRanges', [])
        past_value = 0
        if ranges[0].get('values', 0) != 0:
            past_value = ranges[0].get('values', 0)[0][0]
        print(type(past_value), past_value)
        print(type(expense_values[1]),expense_values[1])
        new_value = int(expense_values[1]) + int(past_value)
        print(new_value)

    values = [
        [
            new_value
        ],
        # Additional rows ...
    ]
    body = {
        'values': values
    }



    result = service.spreadsheets().values().update(
        spreadsheetId=EXPENSES_SPREADSHEET_ID, range=range_names,
        valueInputOption="RAW", body=body).execute()

    update.message.reply_text("Expense added sucessfully")


###############################
msg_handler = MessageHandler(Filters.text, expenseCollector)
dispatcher.add_handler(msg_handler)

def others(bot, update):
    update.message.reply_text("Wrong type, please use this message format: Category Amount")

oth_handler = MessageHandler(Filters.video | Filters.document | Filters.photo, others)
dispatcher.add_handler(oth_handler)

updater.start_polling()
