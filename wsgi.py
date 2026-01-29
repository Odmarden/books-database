import sys
import os

sys.path.insert(0, '/var/www/bokdatabas')
os.chdir('/var/www/bokdatabas')
# Ändra detta i web_app.py
DB_NAMN = "/var/www/bokdatabas/bibliotek.db"

from web_app import app as application

