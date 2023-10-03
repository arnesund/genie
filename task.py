import streamlit as st
from datetime import date
from pydantic import BaseModel

from utils import get_worksheet

CATEGORIES = ["Goal", "Promise", "Responsibility"]

class Task:
    def __init__(self, description: str, category: str = None, priority: int = None, deadline: date = None):
        # Evaluate input
        if category and category not in CATEGORIES:
            raise ValueError(f"Invalid type specified, must be one of {', '.join(CATEGORIES)}")
        
        self.description: str = description
        self.category: str = category
        self.priority: int = priority
        self.deadline: date = deadline
        self.sheet = get_worksheet()

    def __getitem__(self, key):
        if key == "description":
            return self.description
        elif key == "priority":
            return self.priority
        elif key == "deadline":
            return self.deadline
        elif key == "category":
            return self.category
        else:
            raise KeyError(f"'{key}' is not a valid key for Task")

    def __setitem__(self, key, value):
        if key == "description":
            self.description = value
        elif key == "priority":
            self.priority = value
        elif key == "deadline":
            self.deadline = value
        elif key == "category":
            self.category = value
        else:
            raise KeyError(f"'{key}' is not a valid key for Task")

    def find_row(self):
        cell = self.sheet.find(self.description)
        self.row = cell.row if cell else None

    def save(self):
        if not self.sheet:
            raise ValueError(f"Unable to save! Spreadsheet storage not set.")
        
        # Find the current row, might have changed since last lookup
        self.find_row()
        if self.row:
            # Update the values that have changed
            current_values = self.sheet.row_values(self.row)
            if current_values[0] != self.description:
                self.sheet.update_cell(self.row, 1, self.description)
            if current_values[1] != self.category:
                self.sheet.update_cell(self.row, 2, self.category)
            if current_values[2] != self.priority:
                self.sheet.update_cell(self.row, 3, self.priority)
            if current_values[3] != self.deadline:
                self.sheet.update_cell(self.row, 4, self.deadline)
        else:
            # Add task
            self.sheet.insert_rows([[
                self.description,
                self.category if self.category else "",
                self.priority if self.priority else "",
                self.deadline if self.deadline else "",
            ]], 2)


@st.cache_data(ttl=60)
def get_all_tasks() -> list:
    """Fetch spreadsheet and parse it into a list of Task objects"""
    current_tasks = []
    sheet = get_worksheet()
    everything = sheet.get_all_records()
    for row in everything:
        if row["description"]:
            t = Task(
                row["description"],
                row["category"] if row["category"] in CATEGORIES else None,
                row.get("priority", None),
                row.get("deadline", None),
            )
            current_tasks.append(t)
    return current_tasks


@st.cache_data(ttl=60)
def get_all_tasks_as_text() -> str:
    """Get all tasks and format them as a text object for easy use by LLM"""
    res = ""
    for t in get_all_tasks():
        line = f"Task: {t['description']}"
        if t["category"]:
            line += f" which is a {t['category']}"
        if t["priority"]:
            line += f" with priority {t['priority']}"
        if t["deadline"]:
            line += f" and deadline {t['deadline']}"
        res += line + "\n"
    return res


def get_task_by_description(description: str) -> Task:
    """Search the task list for a task by description, return Task object or None"""
    for t in get_all_tasks():
        if t["description"] == description:
            return t
    return None


def change_priority(description: str, priority: int) -> str:
    """Update the priority for a task by description"""
    t = get_task_by_description(description)
    if t:
        t["priority"] = priority
        t.save()
        return f"Updated the priority of Task: {description} to {priority}"
    else:
        return f"Unable to find Task: {description}"
