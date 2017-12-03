from pprint import pprint
from typing import List

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import dateutil.parser

import datetime

from utils.activity import Activity

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = '../api_keys/client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-agendamaker.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_events(calendarId: str, start_date: datetime.date, end_date: datetime.date) -> List[Activity]:
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    print('Getting the events')
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print(now)
    start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time()).isoformat() + 'Z'
    end_date = datetime.datetime.combine(end_date, datetime.datetime.min.time()).isoformat() + 'Z'

    eventsResult = service.events().list(
        calendarId=calendarId, timeMin=start_date, timeMax=end_date, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    activities = []
    # begin_time = "21:00"
    # end_time = "23:00"
    # begin_date = datetime.date(2017, 11, 7)
    # end_date = datetime.date(2017, 11, 1)
    # descriptor = "Descriptor"
    # location = "USC studio 2"
    # price = "€0/€3"
    #
    # activity = Activity(begin_time, end_time, begin_date, end_date, name, descriptor, location, price)
    # activities.append(activity)
    if not events:
        print('No events found.')
    for event in events:
        # pprint(event)
        start_dateTime = dateutil.parser.parse(event['start'].get('dateTime', event['start'].get('date')))
        start_date = start_dateTime.date()
        start_time = start_dateTime.strftime('%H:%M')
        end_dateTime = dateutil.parser.parse(event['end'].get('dateTime', event['end'].get('date')))
        end_date = end_dateTime.date()
        end_time = end_dateTime.strftime('%H:%M')
        description = event.get('description', "").strip()
        location = event.get('location', "")
        title = event['summary'].strip()
        activity = Activity(start_time, end_time, start_date, end_date, title, description, location)
        activities.append(activity)
        # start = event['start'].get('dateTime', event['start'].get('date'))
        # # print(start, event['summary'])

    return activities


def get_calendars():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print(calendar_list_entry['summary'], calendar_list_entry, "\n")
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

