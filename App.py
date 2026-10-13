
import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="My Task Tracker",
    page_icon="✓",
    layout="wide"
)

# Original project colors
BG = "#F4F6FB"
PRIMARY = "#6C63FF"
TEXT = "#252A3D"
MUTED = "#7A8198"
GREEN = "#20C879"
RED = "#EF476F"
ORANGE = "#F4A51C"
BLUE = "#3B82F6"

TASK_FILE = "tasks.json"
USER_FILE = "user.json"

CATEGORIES = [
    "Study", "Work", "Personal", "College",
    "Health", "Shopping", "General"
]
PRIORITIES = ["High", "Medium", "Low"]


def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError):
        pass
    return default


if "tasks" not in st.session_state:
    st.session_state.tasks = load_json(TASK_FILE, [])

if "username" not in st.session_state:
    saved_user = load_json(USER_FILE, {"username": ""})
    st.session_state.username = saved_user.get("username", "")

if "page" not in st.session_state:
    st.session_state.page = "login"


def save_tasks():
    try:
        with open(TASK_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.tasks, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def save_user(name):
    st.session_state.username = name
    try:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": name}, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def parse_due(task):
    text = task.get("due_date", "No deadline")
    if not text or text == "No deadline":
        return None
    try:
        return datetime.strptime(text, "%d-%m-%Y %I:%M %p")
    except ValueError:
        return None


def overdue(task):
    due = parse_due(task)
    return (
        task.get("status", "Pending") != "Completed"
        and due is not None
        and due < datetime.now()
    )


def due_today(task):
    due = parse_due(task)
    return due is not None and due.date() == datetime.now().date()


def upcoming(task):
    due = parse_due(task)
    return (
        task.get("status", "Pending") != "Completed"
        and due is not None
        and due > datetime.now()
    )


def status_text(task):
    if task.get("status") == "Completed":
        return "✓ Completed"
    if overdue(task):
        return "⚠ Overdue"
    return "○ Pending"


# Styling
st.markdown(f"""
<style>
.stApp {{ background: {BG}; color: {TEXT}; }}
.block-container {{ padding-top: 1.5rem; }}
.topbar {{
    background: {PRIMARY}; color: white; padding: 22px 26px;
    border-radius: 14px; margin-bottom: 20px;
}}
.stat {{
    background: white; padding: 16px; border-radius: 12px;
    border-left: 5px solid {PRIMARY}; margin-bottom: 8px;
}}
.stat-num {{ font-size: 28px; font-weight: 700; color: {TEXT}; }}
.stat-label {{ font-size: 12px; color: {MUTED}; }}
.panel {{
    background: white; padding: 18px; border-radius: 12px;
}}
</style>
""", unsafe_allow_html=True)


# Welcome screen
if not st.session_state.username or st.session_state.page == "login":
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown(
            f"""<div style="background:white;padding:35px;border-radius:18px;
            text-align:center;border-top:7px solid {PRIMARY}">
            <div style="font-size:44px;color:{PRIMARY}">✓</div>
            <h1 style="color:{TEXT}">My Task Tracker</h1>
            <p style="color:{MUTED}">Your personal productivity space</p>
            <h3 style="color:{PRIMARY}">Welcome 👋</h3>
            <p style="color:{MUTED}">What should we call you?</p>
            </div>""",
            unsafe_allow_html=True
        )
        with st.form("login_form"):
            name = st.text_input(
                "Your name",
                value=st.session_state.username,
                placeholder="Enter your name"
            )
            enter = st.form_submit_button(
                "Continue →", use_container_width=True,
                type="primary"
            )
        if enter:
            if name.strip():
                save_user(name.strip())
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.warning("Please enter your name.")
    st.stop()


# Dashboard header
left_head, right_head = st.columns([3, 1])
with left_head:
    st.markdown(
        f"""<div class="topbar">
        <h1 style="margin:0">✓ My Task Tracker</h1>
        <div>Welcome, {st.session_state.username} 👋</div>
        </div>""",
        unsafe_allow_html=True
    )
with right_head:
    st.markdown(
        f"""<div style="text-align:right;padding-top:16px;color:{MUTED}">
        {datetime.now().strftime("%A, %d %B %Y")}
        </div>""",
        unsafe_allow_html=True
    )

if st.button("Change username"):
    st.session_state.page = "login"
    st.rerun()

tasks = st.session_state.tasks
total = len(tasks)
completed = sum(t.get("status") == "Completed" for t in tasks)
pending = total - completed
percent = int(completed / total * 100) if total else 0

c1, c2, c3 = st.columns(3)
for col, label, value, color in [
    (c1, "TOTAL TASKS", total, PRIMARY),
    (c2, "PENDING", pending, ORANGE),
    (c3, "COMPLETED", completed, GREEN),
]:
    with col:
        st.markdown(
            f"""<div class="stat" style="border-left-color:{color}">
            <div class="stat-num">{value}</div>
            <div class="stat-label">{label}</div></div>""",
            unsafe_allow_html=True
        )

p1, p2 = st.columns([3, 1])
p1.markdown("**Your Progress**")
p2.markdown(f"**:violet[{percent}% Completed]**")
st.progress(percent / 100)

st.divider()
form_col, list_col = st.columns([1, 2], gap="large")

# Create task panel
with form_col:
    st.subheader("＋ Create Task")
    st.caption("Add details to your task.")

    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("TASK", placeholder="What do you need to do?")
        category = st.selectbox("CATEGORY", CATEGORIES)
        priority = st.selectbox("PRIORITY", PRIORITIES, index=1)
        due_date = st.text_input(
            "DUE DATE & TIME",
            placeholder="10-10-2026 06:00 PM"
        )
        st.caption("Format: DD-MM-YYYY HH:MM AM/PM. Leave blank for no deadline.")
        notes = st.text_area("NOTES", height=100)
        add = st.form_submit_button(
            "＋ Add Task", use_container_width=True, type="primary"
        )

    if add:
        if not title.strip():
            st.warning("Please enter a task first.")
        elif due_date.strip() and due_date.strip() != "No deadline":
            try:
                datetime.strptime(due_date.strip(), "%d-%m-%Y %I:%M %p")
            except ValueError:
                st.error("Invalid date. Example: 10-10-2026 06:00 PM")
                st.stop()
            tasks.append({
                "title": title.strip(), "category": category,
                "priority": priority, "due_date": due_date.strip(),
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "status": "Pending", "notes": notes.strip()
            })
            save_tasks()
            st.success("Task added!")
            st.rerun()
        else:
            tasks.append({
                "title": title.strip(), "category": category,
                "priority": priority, "due_date": "No deadline",
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "status": "Pending", "notes": notes.strip()
            })
            save_tasks()
            st.success("Task added!")
            st.rerun()

# Task list panel
with list_col:
    st.subheader("Your Tasks")
    st.caption("Search, filter and manage your tasks.")

    search = st.text_input("🔍 Search tasks", placeholder="Search title, notes, category...")
    filter_choice = st.radio(
        "Filter tasks",
        ["All", "Today", "Upcoming", "Overdue", "Pending", "Completed", "High"],
        horizontal=True
    )
    sort_due = st.checkbox("Sort by due date")

    visible = []
    for task in tasks:
        query = search.strip().lower()
        searchable = " ".join([
            str(task.get("title", "")),
            str(task.get("category", "")),
            str(task.get("priority", "")),
            str(task.get("status", "")),
            str(task.get("notes", ""))
        ]).lower()

        if query and query not in searchable:
            continue
        if filter_choice == "Today" and not due_today(task):
            continue
        if filter_choice == "Upcoming" and not upcoming(task):
            continue
        if filter_choice == "Overdue" and not overdue(task):
            continue
        if filter_choice == "Pending" and task.get("status") != "Pending":
            continue
        if filter_choice == "Completed" and task.get("status") != "Completed":
            continue
        if filter_choice == "High" and task.get("priority") != "High":
            continue
        visible.append(task)

    if sort_due:
        visible.sort(key=lambda t: parse_due(t) or datetime.max)

    if not visible:
        st.info("No tasks found. Add a task or change the filter.")

    for task in visible:
        idx = tasks.index(task)
        title_text = task.get("title", "Untitled Task")
        priority = task.get("priority", "Medium")
        status = status_text(task)

        with st.container(border=True):
            a, b = st.columns([4, 1])
            with a:
                st.markdown(f"**{title_text}**")
                st.caption(
                    f"{task.get('category', 'General')}  •  "
                    f"{priority} Priority  •  "
                    f"{task.get('due_date', 'No deadline')}"
                )
                st.write(status)
            with b:
                st.write("")
                if task.get("status") == "Completed":
                    st.button("✓ Done", key=f"done_{idx}", disabled=True,
                              use_container_width=True)
                elif st.button("✓ Complete", key=f"complete_{idx}",
                               use_container_width=True):
                    tasks[idx]["status"] = "Completed"
                    save_tasks()
                    st.rerun()

            with st.expander("👁 Details / ✏ Edit"):
                st.write("**Category:**", task.get("category", "General"))
                st.write("**Priority:**", priority)
                st.write("**Due date:**", task.get("due_date", "No deadline"))
                st.write("**Status:**", task.get("status", "Pending"))
                st.write("**Created:**", task.get("date", "Unknown"))
                st.write("**Notes:**", task.get("notes", "") or "No notes added.")

                with st.form(f"edit_{idx}"):
                    new_title = st.text_input("Task", value=title_text)
                    cat_index = CATEGORIES.index(task.get("category", "General")) if task.get("category", "General") in CATEGORIES else 6
                    new_category = st.selectbox("Category", CATEGORIES, index=cat_index)
                    pri_index = PRIORITIES.index(priority) if priority in PRIORITIES else 1
                    new_priority = st.selectbox("Priority", PRIORITIES, index=pri_index)
                    new_due = st.text_input(
                        "Due date & time",
                        value=task.get("due_date", "No deadline")
                    )
                    new_notes = st.text_area(
                        "Notes", value=task.get("notes", "")
                    )
                    save_edit = st.form_submit_button("Save Changes")

                if save_edit:
                    if not new_title.strip():
                        st.error("Task name cannot be empty.")
                    else:
                        date_text = new_due.strip() or "No deadline"
                        valid = date_text == "No deadline"
                        if not valid:
                            try:
                                datetime.strptime(date_text, "%d-%m-%Y %I:%M %p")
                                valid = True
                            except ValueError:
                                st.error("Use DD-MM-YYYY HH:MM AM/PM or No deadline.")
                        if valid:
                            tasks[idx].update({
                                "title": new_title.strip(),
                                "category": new_category,
                                "priority": new_priority,
                                "due_date": date_text,
                                "notes": new_notes.strip()
                            })
                            save_tasks()
                            st.success("Task updated!")
                            st.rerun()

                d1, d2 = st.columns(2)
                with d1:
                    if st.button("🗑 Delete", key=f"delete_{idx}",
                                 use_container_width=True):
                        st.session_state.confirm_delete = idx
                with d2:
                    if st.button("❌ Clear All Tasks", key=f"clear_{idx}",
                                 use_container_width=True):
                        st.session_state.confirm_clear = True

if "confirm_delete" in st.session_state:
    idx = st.session_state.confirm_delete
    if idx < len(tasks):
        st.warning(f"Delete '{tasks[idx].get('title', 'this task')}'?")
        yes, no = st.columns(2)
        with yes:
            if st.button("Yes, delete", type="primary"):
                tasks.pop(idx)
                save_tasks()
                del st.session_state["confirm_delete"]
                st.rerun()
        with no:
            if st.button("Cancel delete"):
                del st.session_state["confirm_delete"]
                st.rerun()

if st.session_state.get("confirm_clear"):
    st.warning("Are you sure you want to delete ALL tasks?")
    yes, no = st.columns(2)
    with yes:
        if st.button("Yes, clear all", type="primary"):
            tasks.clear()
            save_tasks()
            del st.session_state["confirm_clear"]
            st.rerun()
    with no:
        if st.button("Cancel clear"):
            del st.session_state["confirm_clear"]
            st.rerun()

st.divider()
st.caption("My Task Tracker • Stay organized, one task at a time.")
