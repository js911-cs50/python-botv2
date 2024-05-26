from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

# Your Flask application routes and logic here

def run():
  port = int(os.environ.get('PORT', 8080))  # Use environment variable or default to 8080
  app.run(host='0.0.0.0', port=port)  # Remove this line (development server)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == '__main__':
    keep_alive()
