import requests
a_session = requests.Session()
a_session.get('https://www.orbitz.com/')
session_cookies = a_session.cookies
print(session_cookies.get_dict())