import streamlit as st
from utils import get_worksheet, add_task

sheet = get_worksheet()

new_task = st.text_input("New task:")
if st.button("Add"):
    add_task(new_task, sheet)

st.write("# Most important task right now")

