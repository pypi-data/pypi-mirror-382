import os
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.environ.get('GLPI_BASE_URL')
USER_TOKEN = os.environ.get('GLPI_USER_TOKEN')
APP_TOKEN = os.environ.get('GLPI_APP_TOKEN')
TICKET_STATUS = os.environ.get('GLPI_TICKET_STATUS')