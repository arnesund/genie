import streamlit as st
from datetime import date
from utils import get_task_index

TASK_TYPES = ["Goal", "Promise", "Responsibility"]


class Task:
    def __init__(self, description: str, priority: int, deadline: date, task_type: str):
        # Evaluate input
        if task_type not in TASK_TYPES:
            raise ValueError(f"Invalid type specified, must be one of {', '.join(TASK_TYPES)}")
        
        self.description = description
        self.priority = priority
        self.deadline = deadline
        self.task_type = task_type

    def save(self, sheet):
        row = get_task_index(sheet, self.description)
        if row:
            # Update task
            st.write(f"About to update {row}")
            #sheet.update(row, self.description, ...)
        else:
            # Add task
            sheet.insert_rows([[
                self.description,
                self.task_type if self.task_type else "",
                self.priority if self.priority else "",
                self.deadline if self.deadline else "",
            ]], 2)
