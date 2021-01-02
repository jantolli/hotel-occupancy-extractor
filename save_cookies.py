import requests, pickle
import urllib

REQUEST = "https://www.orbitz.com/Tulum-Hotels-Cacao-Tulum-Luxury-Condos.h53803244.Hotel-Information?chain=&chkin=01%2F06%2F2021&chkout=01%2F07%2F2021&daysInFuture=&destType=CURRENT_LOCATION&destination=Tulum%2C%20Tulum%2C%20Quintana%20Roo%2C%20Mexico&group=&guestRating=&hotelName=&latLong=&misId=&neighborhoodId=553248633981716254&poi=&pwa_ts=1591930302534&referrerUrl=aHR0cHM6Ly93d3cub3JiaXR6LmNvbS9Ib3RlbC1TZWFyY2g%3D&regionId=182189&rm1=a2&roomIndex=&selected=53803244&sort=RECOMMENDED&stayLength=&theme=&useRewards=true&userIntent=&x_pwa=1"
COOKIES_FILENAME = "cookies.txt"

COOKIES = ""

def save_cookies(requests_cookiejar):
    with open(COOKIES_FILENAME, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies():
    with open(COOKIES_FILENAME, 'rb') as f:
        return pickle.load(f)


user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
accept = "*/*"
host = "www.orbitz.com"
# accept_encoding = "gzip, deflate"
accept_encoding = "deflate"
headers = {'User-agent': user_agent, 'Accept': accept, 'Host': host, 'Accept-encoding': accept_encoding, 'Cookie': ''}

r = requests.get('https://www.orbitz.com', headers=headers)
COOKIES = r.cookies
print(r.status_code)

lala = [dict(t) for t in {tuple(d.items()) for d in COOKIES}]

r = requests.get(REQUEST, headers=headers, cookies=lala)
print(r.status_code)
