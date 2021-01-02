from __future__ import division
from datetime import date
from StringIO import StringIO

import datetime
import os
import requests, pickle
import re
import sys
import urllib
import urllib2
import xml.etree.ElementTree as ET
import gzip


COOKIES_FILENAME = "cookies.txt"
MAX = 9
DEFAULT_PRICE = str(91)


def save_cookies(requests_cookiejar):
    with open(COOKIES_FILENAME, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies():
    with open(COOKIES_FILENAME, 'rb') as f:
        return pickle.load(f)

def get_url(checkin, checkout):
  checkin_date =  checkin.strftime("%Y-%m-%d")
  checkout_date = checkout.strftime("%Y-%m-%d")

  url = "https://www.orbitz.com/Tulum-Hotels-Cacao-Tulum-Luxury-Condos.h53803244.Hotel-Information?chkin=" + checkin_date + "&chkout=" + checkout_date + "&daysInFuture=&destType=CURRENT_LOCATION&destination=Tulum%2C%20Tulum%2C%20Quintana%20Roo%2C%20Mexico&group=&guestRating=&hotelName=&latLong=&misId=&neighborhoodId=553248633981716254&poi=&pwa_ts=1591930302534&referrerUrl=aHR0cHM6Ly93d3cub3JiaXR6LmNvbS9Ib3RlbC1TZWFyY2g%3D&regionId=182189&rm1=a2&roomIndex=&selected=53803244&sort=RECOMMENDED&stayLength=&theme=&useRewards=true&userIntent=&x_pwa=1"

  return url


def get_response(checkin, checkout):
  # user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
  # accept = "*/*"
  # host = "https://www.orbitz.com"
  # accept_encoding = "gzip, deflate"
  # headers = {'User-agent': user_agent, 'Accept': accept, 'Host': host, 'Accept-encoding': accept_encoding, 'Cookie': load_cookies()}
  headers = {}
  # print 'Going to ' + url
  url = get_url(checkin, checkout)
  # req = urllib2.Request(url, {}, headers)
  # print req.headers
  # response = urllib2.urlopen(req)
  print url
  response = requests.get(url, headers).text
  # return requests.get(url).text
  # result = None
  # if response.headers.get('Content-Encoding') == 'gzip':
  #  stringbuffer = StringIO(response.text)
  #  gzipbuffer = gzip.GzipFile(fileobj = stringbuffer)
  #  result = gzipbuffer.read()
  if response[:2] == '\x1f\x8b': # assume it's gzipped data
    with GzipFile(mode='rb', fileobj=StringIO(s)) as ifh:
      response = ifh.read()
  
  #else:
  #result = response
  # print response
  return response


def search_occupancy(checkin, length):
  occupancy = open("Occupancy/occupancy_" + date.today().strftime("%Y-%m-%d") + ".txt", "w")
  
  occupancy_array = []
  price_array = []
  price = DEFAULT_PRICE
  
  for index in range(0, 1):
    availabilty_index = MAX
    studio_room_index = MAX
    checkout = checkin + datetime.timedelta(length)
    full_hotel = False
    html = get_response(checkin, checkout)
    try:
      studio_room_index = re.search("Superior Studio, Private Pool", html).start()
    except:
      print("No Studio Found. Setting to Not Available")

    x = re.search("We have (\d+) left", html)
    try:
      availabilty_index = x.start()
    except:
      full_hotel = True
      print("Yayy full hotel on " + str(checkin))
    
#   if "Superior Studio, Private Pool" in html:
    if x and studio_room_index <= availabilty_index:
      rooms_left = x.group(1)
      occupancy_array.append(MAX - int(rooms_left))
      x = re.search(">\$(\d+) average per night</div>", html)
#        x = re.search('<span class=\"uitk-cell loyalty-display-price all-cell-shrink\" data-stid="content-hotel-lead-price" aria-hidden=\"true\">\$(\d+)</span>', html)
      price = x.group(1)
      price_array.append(int(price))
      occupancy.write(str(checkin) + ": " + rooms_left + " left. Price: $" + price + "\n")
    else:
      occupancy_array.append(MAX)
      price_array.append(int(price))
      if full_hotel:
        occupancy.write(str(checkin) + ": Full Hotel! Price: $" + price + "\n")
      else:
        occupancy.write(str(checkin) + ": Not Available. Price: $" + price + "\n")

    checkin = checkout

#  print(price_array)
  average_occupancy = round(sum(occupancy_array) / len(occupancy_array), 2)
  average_price = round(sum(price_array) / len(occupancy_array), 2)
  average_earnings = round(average_price*average_occupancy/MAX, 2)
  occupancy.write("\nAverage Occupancy: " + str(round(average_occupancy*100/MAX, 2)) + "%\n")
  occupancy.write("Average Price: $" + str(round(average_price, 2)) + "\n")
  occupancy.write("Average Earnings: $" + str(round(average_earnings, 2)) + "\n")
  occupancy.write("\nToday's Gross Earnings: $" + str(round(price_array[0]*occupancy_array[0]/MAX, 2)) + "\n")
  occupancy.write("Today's Net Earnings: $" + str(round(price_array[0]*occupancy_array[0]/MAX*0.7, 2)) + "\n")

  occupancy.close()




#save cookies
r = requests.get("https://www.orbitz.com")
save_cookies(r.cookies)

# checkin = date.today()
checkin = datetime.date(2021, 01, 10)
search_occupancy(checkin, 2)