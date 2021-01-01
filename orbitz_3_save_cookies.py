from __future__ import division
from datetime import date
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
  user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
  accept = "*/*"
  host = "www.orbitz.com"
  # accept_encoding = "gzip, deflate"
  accept_encoding = "deflate"
  # print 'Going to ' + url
  url = get_url(checkin, checkout)
  req = Request(url)
  req.add_header('User-agent', user_agent)
  req.add_header('Accept', accept)
  req.add_header('Host', host)
  req.add_header('Accept-encoding', accept_encoding)
  req.add_header('Cookie', 'CRQS=t|70201`s|70201`l|en_US`c|USD')
  req.add_header('Cookie', 'CRQSS=e|0')
  req.add_header('Cookie', 'DUAID=4f1ef321-e04d-45a5-aabe-eeffc5d6395d')
  req.add_header('Cookie', 'HMS=aa7e3045-4eea-4b20-950e-539d6b55619a')
  req.add_header('Cookie', 'MC1=GUID=4f1ef321e04d45a5aabeeeffc5d6395d')
  req.add_header('Cookie', 'accttype=')
  req.add_header('Cookie', 'cesc=%7B%22marketingClick%22%3A%5B%22false%22%2C1609242441541%5D%2C%22hitNumber%22%3A%5B%221%22%2C1609242441541%5D%2C%22visitNumber%22%3A%5B%221%22%2C1609242441541%5D%2C%22entryPage%22%3A%5B%22page.Recaptcha%22%2C1609242441541%5D%7D')
  req.add_header('Cookie', 'currency=USD')
  req.add_header('Cookie', 'iEAPID=0')
  req.add_header('Cookie', 'linfo=v.4,|0|0|255|1|0||||||||1033|0|0||0|0|0|-1|-1')
  req.add_header('Cookie', 'minfo=')
  req.add_header('Cookie', 'tpid=v.1,70201')
  req.add_header('Cookie', 'user=')
  req.add_header('Cookie', 'JSESSIONID=1D1B478D98EF35EAE16D6DF9E446B630')

  # req.add_header('Cookie', load_cookies())
  response = urlopen(req)
  # req = urllib.request(url, {}, headers)
  # print req.headers
  #result = None
  #if response.info().get('Content-Encoding') == 'gzip':
  #  stringbuffer = io.StringIO(response.read())
  #  gzipbuffer = gzip.GzipFile(fileobj = stringbuffer)
  # result = gzipbuffer.read()
  return response.read().decode('utf-8')


def search_occupancy(checkin, length):
  occupancy = open("Occupancy/occupancy_" + date.today().strftime("%Y-%m-%d") + ".txt", "w")
  
  occupancy_array = []
  price_array = []
  price = DEFAULT_PRICE
  
  for index in range(0, 15):
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

checkin = date.today()
# checkin = datetime.date(2020, 12, 18)
search_occupancy(checkin, 2)
