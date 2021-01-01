# Python 3 server example

import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/html")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        # Extract query param
        name = 'World'
        query_components = parse_qs(urlparse(self.path).query)
        if 'name' in query_components:
            name = query_components["name"][0]

        # Some custom HTML code, possibly generated by another function
        html = "<html><head></head><body><h1>Hello " + name + "!</h1></body></html>"

        # Writing the HTML contents with UTF-8
        self.wfile.write(bytes(html, "utf8"))

        return

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8080
my_server = socketserver.TCPServer(("", PORT), handler_object)

# Star the server
my_server.serve_forever()