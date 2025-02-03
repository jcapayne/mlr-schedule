#!/usr/bin/env python3


# make sure we're running under the virtual environment
import os

my_path = os.path.abspath(os.path.dirname(__file__))

activate_this_file = "%s/bin/activate_this.py" % my_path

exec(open(activate_this_file).read(), {'__file__': activate_this_file})


import requests
import cssutils
from bs4 import BeautifulSoup
import sys
import traceback
import datetime
import json
from six.moves.html_parser import HTMLParser
from pprint import pprint
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta
import pytz
from pytz import timezone
 


if __name__ == "__main__":
    
    teams = ('mlr','New England Free Jacks','Old Glory DC','Anthem Rugby Carolina','Chicago Hounds','NOLA Gold','Miami Sharks','San Diego Legion','Utah Warriors','Rugby LA','Houston SaberCats', 'Seattle Seawolves')

    cal={}
    
    for team in teams:
        cal[team] = Calendar()
        cal[team].add('prodid', '-//Ranger Picks//rangerpicks.rugby//')
        cal[team].add('version', '2.0')
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    session=requests.Session()
    html=session.get('https://www.majorleague.rugby/schedule/',headers=headers)
    soup=BeautifulSoup(html.text, features="html.parser")
    
    
    # check for an error and hard abort if there is one
    error=soup.find_all('div','common-section')
    for err in error:
        if 'Error fetching match data' in err.text:
            raise SystemExit(err.text)


    allmatches=soup.find_all('div',class_='list')
    

    
    for match in allmatches:
        matchsoup=BeautifulSoup(str(match), features="html.parser")
        matchdate=matchsoup.findAll('div','match-date')[0].string
        matchtime=matchsoup.findAll('div','match-time')[0].string
        try:
            matchdatetime=datetime.strptime("%s %s" % (matchdate.string, matchtime.string), '%B %d, %Y %H:%M PM EST')
            matchdatetime =  matchdatetime + timedelta(hours=12)
        except:
            matchdatetime=datetime.strptime("%s %s" % (matchdate.string, matchtime.string), '%B %d, %Y %H:%M AM EST')
            
        matchenddatetime = matchdatetime + timedelta(hours=2)
        
        matchlocation=matchsoup.findAll('div','match-details')[0].string
        matchtickets=matchsoup.findAll('div','buy-tickets')[0].a['href']
        matchhome=matchsoup.findAll('div','team-name-result-left')[0].h3.string
        matchaway=matchsoup.findAll('div','team-name-result-right')[0].h3.string
        if matchlocation == "Veterans Memorial Stadium":
            matchlocation = "Fort Quincy"

        if matchaway == "Anthem RC":
            matchaway = "Anthem Rugby Carolina"

        if matchhome == "Anthem RC":
            matchhome = "Anthem Rugby Carolina"
            
        event = Event()
        event.add('summary', "%s @ %s" % (matchaway,matchhome))
        event.add('description', "Buy tickets: %s" % matchtickets)
        event.add('dtstart', datetime(matchdatetime.year, matchdatetime.month, matchdatetime.day, matchdatetime.hour, matchdatetime.minute, 0, tzinfo=timezone('US/Eastern')))
        event.add('dtend', datetime(matchenddatetime.year, matchenddatetime.month, matchenddatetime.day, matchenddatetime.hour, matchenddatetime.minute, 0, tzinfo=timezone('US/Eastern')))
        event['location'] = vText(matchlocation)
        
        cal['mlr'].add_component(event)
        cal[matchhome].add_component(event)
        cal[matchaway].add_component(event)
        
        
    for team in teams:
        f = open("%s/%s.ics" % (my_path, team.replace(" ", "").lower()), 'wb')
        f.write(cal[team].to_ical())
        f.close()
