import pandas as pd
import pygsheets
import sys
####KEYS = './files/ticketmaster-scrapper-809f5ae8ed35.json'

USERNAME = 'ilucash25@gmail.com'
PASS = 'I23sa57y'

LOGGING_BUTTON = '//a[contains(@class, "nav__button-secondary")]'
USERNAME_INPUT = '//input[@id="username"]'
PASSWORD_INPUT = '//input[@id="password"]'
SIGNIN_BUTTON = '//button[text()="Iniciar sesión"]'


def save_db_to_gsheets(db: pd.DataFrame):
    try:
        g_account = pygsheets.authorize(service_file=KEYS)
        g_sheet = g_account.open('scraper_db')
        g_worksheet = g_sheet[1]
        g_worksheet.set_dataframe(db, start=(1,1), extend=True)

    except Exception:
        # log (Access to google sheet failed)
        sys.exit(1)