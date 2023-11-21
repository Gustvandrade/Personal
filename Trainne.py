import win32com.client
from time import time
import os
import pandas as pd
from openpyxl import load_workbook
import datetime
import pandas as pd
from datetime import datetime, timedelta
import sys

# Get username PC
us = os.getlogin()

# SAP Conection test
try:
    SapGuiAuto = win32com.client.GetObject("SAPGUI")
    application = SapGuiAuto.GetScriptingEngine
    connection = application.Children(0)
    session = connection.Children(0)
    print("SAP successfully connected.")
except:
    print("SAP não está conectado, verifique!")