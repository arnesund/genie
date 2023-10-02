import gspread
import pandas as pd
import streamlit as st

from datetime import date
from google.oauth2 import service_account


def get_worksheet():
    """Connect to Google Sheet with tasklist and return Worksheet object"""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    gc = gspread.authorize(credentials)
    sheet_url = st.secrets["private_gsheets_url"]
    return gc.open_by_url(sheet_url).sheet1

@st.cache_data(ttl=60)
def get_all_tasks(_sheet):
    """Fetch all tasks, cache results and return as a Pandas DataFrame"""
    return pd.DataFrame.from_records(_sheet.get_all_records())

def get_task_index(sheet, task_description):
    """Search for a task with a given description and return the task index (row number) or None if not found"""
    cell = sheet.find(task_description)
    return cell.row if cell else None

def add_task(task_description, sheet):
    """Add a new task description to the list"""
    # Add new entry in row 2 (at the top of the list)
    sheet.insert_rows([[task_description]], 2)

