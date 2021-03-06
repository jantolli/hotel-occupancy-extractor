from __future__ import division
from datetime import date
from ftplib import FTP

try:
    from urllib.request import Request, urlopen  # Python 3
except ImportError:
    from urllib2 import Request, urlopen  # Python 2

import datetime
import io
import os
import re
import requests, pickle
import sys
import urllib
import xml.etree.ElementTree as ET
import gzip

MAX = 9
DEFAULT_PRICE = str(91)
FTP_HOST = 'joseantollini.no-ip.org'
FTP_USERNAME = 'guest1'
FTP_PASSWORD = '12guest34'
FTP_DIR = '/WD1TB/Public/'
FTP_FILENAME = 'occupancy_' + date.today().strftime('%Y-%m-%d') + '.txt'
COOKIES = dict()


def get_url(checkin, checkout):
  checkin_date =  checkin.strftime("%Y-%m-%d")
  checkout_date = checkout.strftime("%Y-%m-%d")

  url = "https://www.orbitz.com/Tulum-Hotels-Cacao-Tulum-Luxury-Condos.h53803244.Hotel-Information?chkin=" + checkin_date + "&chkout=" + checkout_date + "&daysInFuture=&destType=CURRENT_LOCATION&destination=Tulum%2C%20Tulum%2C%20Quintana%20Roo%2C%20Mexico&group=&guestRating=&hotelName=&latLong=&misId=&neighborhoodId=553248633981716254&poi=&pwa_ts=1591930302534&referrerUrl=aHR0cHM6Ly93d3cub3JiaXR6LmNvbS9Ib3RlbC1TZWFyY2g%3D&regionId=182189&rm1=a2&roomIndex=&selected=53803244&sort=RECOMMENDED&stayLength=&theme=&useRewards=true&userIntent=&x_pwa=1"

  return url

def get_headers():
  user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
  accept = "*/*"
  host = "www.orbitz.com"
  accept_encoding = "deflate"
  return {'User-agent': user_agent, 'Accept': accept, 'Host': host, 'Accept-encoding': accept_encoding}


def get_response(checkin, checkout):
  user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
  accept = "*/*"
  host = "www.orbitz.com"
  accept_encoding = "deflate"
  url = get_url(checkin, checkout)
  response = requests.get(url, headers=get_headers(), cookies=dict(COOKIES))
  return response.text

def search_occupancy(checkin, length):
  
  occupancy = ''
  occupancy_array = []
  price_array = []
  price = DEFAULT_PRICE
  
  for index in range(0, 7):
    availabilty_index = MAX
    studio_room_index = MAX
    luxury_suite_room_index = MAX
    one_bedroom_room_index = MAX
    two_bedroom_room_index = MAX
    checkout = checkin + datetime.timedelta(length)
    full_hotel = False
    html = get_response(checkin, checkout)
    # print(html)

    try:
      studio_room_index = re.search("Superior Studio, Private Pool", html).start()
    except:
      print("No Studio Found. Setting to Not Available")
      
    try:
      luxury_suite_room_index = re.search("Luxury Suite, Private Pool", html).start()
    except:
      print("No Luxury Suite Room Found. Setting to Not Available")

    try:
      one_bedroom_room_index = re.search("Luxury Apartment, 1 Bedroom, Private Pool", html).start()
    except:
      print("No One Bedroom Apartment Found. Setting to Not Available")
      
    try:
      two_bedroom_room_index = re.search("Family Penthouse, 2 Bedrooms, Private Pool", html).start()
    except:
      print("No Two Bedroom Apartment Found. Setting to Not Available")

    x = re.search("We have (\d+) left", html)
    try:
      availabilty_index = x.start()
    except:
      full_hotel = True
      print("Yayy full hotel on " + str(checkin))
    
    # if "Superior Studio, Private Pool" in html:
    # Checking Full Hotel or studio not available
    if studio_room_index > availabilty_index or full_hotel:
      occupancy_array.append(MAX)
      price_array.append(int(price))
      if full_hotel:
        occupancy += str(checkin) + ": Full Hotel! Price: $" + price + "\n"
      else:
        occupancy += str(checkin) + ": Not Available. Price: $" + price + "\n"
    # Checking for not available occupancy information for the studio
    elif luxury_suite_room_index <= availabilty_index or one_bedroom_room_index <= availabilty_index or two_bedroom_room_index <= availabilty_index:
      print('No indication of rooms left. Setting it to maximum unfortnately')   
      occupancy_array.append(0)
      x = re.search('{\\\\"price\\\\":\\\\"\$(\d+)\\\\",\\\\"qualifier\\\\":\\\\" per night\\\\"', html)
      price = x.groups()[0]
      price_array.append(int(price))
      occupancy += str(checkin) + ": " + str(MAX) + " left. Price: $" + price + "\n"
    # There is occupancy information for the studio
    else:
      rooms_left = x.groups()[0]
      occupancy_array.append(MAX - int(rooms_left))
      x = re.search('{\\\\"price\\\\":\\\\"\$(\d+)\\\\",\\\\"qualifier\\\\":\\\\" per night\\\\"', html)
      price = x.groups()[0]
      price_array.append(int(price))
      occupancy += str(checkin) + ": " + rooms_left + " left. Price: $" + price + "\n"

    checkin = checkout

#  print(price_array)
  average_occupancy = (round(sum(occupancy_array) / len(occupancy_array), 2))
  average_price = round(sum(price_array) / len(occupancy_array), 2)
  average_earnings = round(average_price*average_occupancy/MAX, 2)
  occupancy += "\nAverage Occupancy: " + str(round(average_occupancy*100/MAX, 2)) + "%\n"
  occupancy += "Average Price: $" + str(round(average_price, 2)) + "\n"
  occupancy += "Average Earnings: $" + str(round(average_earnings, 2)) + "\n"
  occupancy += "\nToday's Gross Earnings: $" + str(round(price_array[0]*(occupancy_array[0])/MAX, 2)) + "\n"
  occupancy += "Today's Net Earnings: $" + str(round(price_array[0]*(occupancy_array[0])/MAX*0.7, 2)) + "\n"


  print('Opening FTP Connection ' + FTP_HOST)
  ftp = FTP(FTP_HOST)
  ftp.login(FTP_USERNAME, FTP_PASSWORD)
  ftp.cwd(FTP_DIR)
  ftp.storbinary('STOR ' + FTP_FILENAME, io.BytesIO(occupancy.encode('utf-8')))
  print("Search Results saved to file " + FTP_DIR + "/" + FTP_FILENAME)


def main():
  print("Current Working Dir: " + os.getcwd())
  r = requests.get('https://www.orbitz.com', headers=get_headers())
  cookies = r.cookies
  temp = []
  for key, val in cookies.items(): 
    if val not in temp: 
      temp.append(val) 
      COOKIES[key] = val

  print("Starting search...")
  checkin = date.today()
  # checkin = datetime.date(2021, 1, 29)
  search_occupancy(checkin, 2)


if __name__ == "__main__":
    main()
