from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import threading
import ssl
import warnings
from urllib3.exceptions import InsecureRequestWarning
from tensorkube.helpers import verify_user, save_user_credentials
import click

# Suppress only the specific InsecureRequestWarning
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

class OAuthHandler(BaseHTTPRequestHandler):
    server_should_shutdown = False
    def log_message(self, format, *args):
        # Override to prevent any logs from being printed
        return
    
    def do_GET(self):
        # Parse the query string
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        # Extract the token (you may need to adjust the key based on the OAuth provider)
        token = params.get('logged_in_token', [''])[0]
        session_id = params.get('session_id', [''])[0]

        # Respond to the browser
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Save the token to a file
        user_email, _ = verify_user(session_id=session_id, token=token)
        if user_email:
            self.wfile.write(b"Login successful! You can close this window now.")
            save_user_credentials(session_id=session_id, token=token)
            click.echo("Logged in successfully.")
        else:
            self.wfile.write(b"Login Failed! Please try again.")
            click.echo("Failed to log in. Error while verifying user credentials.")

        # Shut down the server
        OAuthHandler.server_should_shutdown = True

def run_server(server_class=HTTPServer, handler_class=OAuthHandler, port=8147):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    # print(f"Starting server on port {port}...")

    try:
        while not handler_class.server_should_shutdown:
            httpd.handle_request()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
