import gspread
import streamlit as st

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
