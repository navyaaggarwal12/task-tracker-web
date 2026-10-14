
import streamlit as st
import json
import os
import html
from datetime import datetime

st.set_page_config(
    page_title="My Task Tracker",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------- THEME --------------------
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
FILTERS = [
    "All", "Today", "Upcoming", "Overdue",
    "Pending", "Completed", "High"
]
DATE_FORMAT = "%d-%m-%Y %I:%M %p"


# -------------------- STORAGE --------------------
def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
    except (OSError, json.JSONDecodeError):
        pass
    return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except OSError:
        st.error(f"Could not save {path}. Check storage permissions.")
        return False


if "tasks" not in st.session_state:
    data = load_json(TASK_FILE, [])
    st.session_state.tasks = data if isinstance(data, list) else []

if "username" not in st.session_state:
    user = load_json(USER_FILE, {"username": ""})
    st.session_state.username = (
        user.get("username", "") if isinstance(user, dict) else ""
    )

if "page" not in st.session_state:
    st.session_state.page = (
        "dashboard" if st.session_state.username else "login"
    )

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None

if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False


def save_tasks():
    return save_json(TASK_FILE, st.session_state.tasks)


def save_user(name):
    st.session_state.username = name
    save_json(USER_FILE, {"username": name})


# -------------------- DATE / STATUS HELPERS --------------------
def parse_due(task):
    value = task.get("due_date", "No deadline")
    if not value or value == "No deadline":
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (ValueError, TypeError):
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


def safe(value):
    return html.escape(str(value))


def priority_color(priority):
    return {
        "High": RED,
        "Medium": ORANGE,
        "Low": GREEN,
    }.get(priority, MUTED)


def status_color(task):
    if task.get("status") == "Completed":
        return GREEN
    if overdue(task):
        return RED
    return ORANGE


# -------------------- ORIGINAL-INSPIRED DESIGN --------------------
st.markdown(
    f"""
    <style>
    :root {{
        --primary: {PRIMARY};
        --background: {BG};
        --text: {TEXT};
        --muted: {MUTED};
    }}

    .stApp {{
        background: var(--background);
        color: var(--text);
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 1.7rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3 {{
        color: var(--text);
        letter-spacing: -0.4px;
    }}

    p, label, .stMarkdown {{
        color: var(--text);
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: white;
        border: 1px solid #E8EAF3;
        border-radius: 15px;
    }}

    .topbar {{
        background: linear-gradient(120deg, #6C63FF, #8179FF);
        color: white;
        padding: 25px 28px;
        border-radius: 17px;
        margin-bottom: 12px;
        box-shadow: 0 7px 22px rgba(108, 99, 255, 0.14);
    }}

    .topbar h1 {{
        color: white !important;
        font-size: 29px;
        margin: 0 0 7px 0;
    }}

    .topbar p {{
        color: #F0EEFF !important;
        margin: 0;
    }}

    .stat-card {{
        background: white;
        border: 1px solid #E9EAF3;
        border-left: 5px solid var(--accent);
        border-radius: 14px;
        padding: 19px 20px;
        min-height: 100px;
        box-shadow: 0 3px 12px rgba(37, 42, 61, 0.025);
    }}

    .stat-number {{
        font-size: 31px;
        font-weight: 750;
        color: var(--text);
        line-height: 1.3;
    }}

    .stat-label {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        color: var(--muted);
        margin-top: 5px;
    }}

    .welcome-card {{
        background: white;
        border: 1px solid #E8EAF3;
        border-top: 7px solid {PRIMARY};
        border-radius: 21px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 12px 35px rgba(37, 42, 61, 0.06);
    }}

    .welcome-icon {{
        color: {PRIMARY};
        font-size: 50px;
        font-weight: 800;
    }}

    .section-caption {{
        color: {MUTED};
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 16px;
    }}

    .task-heading {{
        font-size: 18px;
        font-weight: 750;
        color: {TEXT};
        overflow-wrap: anywhere;
    }}

    .task-meta {{
        font-size: 12px;
        color: {MUTED};
        line-height: 1.8;
        overflow-wrap: anywhere;
    }}

    .pill {{
        display: inline-block;
        padding: 4px 9px;
        margin: 5px 4px 0 0;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
    }}

    .stButton > button,
    .stFormSubmitButton > button {{
        border-radius: 9px;
        font-weight: 650;
        min-height: 40px;
        transition: all 0.15s ease;
    }}

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {{
        background: {PRIMARY};
        border-color: {PRIMARY};
        color: white;
    }}

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {{
        background: #554BE8;
        border-color: #554BE8;
        color: white;
    }}

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {{
        border-radius: 9px;
    }}

    div[data-testid="stProgressBar"] > div > div {{
        background-color: {PRIMARY};
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid #E8EAF3;
        border-radius: 10px;
        background: white;
    }}

    hr {{
        border-color: #E3E6F0;
    }}

    @media (max-width: 700px) {{
        .block-container {{
            padding: 1rem 0.8rem 2rem 0.8rem;
        }}
        .topbar {{
            padding: 20px;
        }}
        .topbar h1 {{
            font-size: 23px;
        }}
    }}
    
/* Light theme for form controls */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #F4F6FB !important;
}

input, textarea {
    background-color: #F4F5FA !important;
    color: #252A3D !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #F4F5FA !important;
    border: 1px solid #E6E8F0 !important;
    border-radius: 4px !important;
}

div[data-baseweb="select"] *,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: #252A3D !important;
}

.stRadio label,
.stCheckbox label {
    color: #252A3D !important;
}

/* Original-style square cards */
.stat-card {
    border-radius: 2px !important;
    box-shadow: none !important;
    min-height: 90px !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    border-radius: 3px !important;
    font-weight: 600 !important;
}

/* Progress bar */
div[data-testid="stProgressBar"] {
    background-color: #E6E8F0;
}

/* Mobile support */
@media (max-width: 700px) {
    .block-container {
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
}

    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- WELCOME / LOGIN --------------------
if not st.session_state.username or st.session_state.page == "login":
    st.markdown("<br><br>", unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown(
            f"""
            <div class="welcome-card">
                <div class="welcome-icon">✓</div>
                <h1>My Task Tracker</h1>
                <p style="color:{MUTED}">
                    Your personal productivity space
                </p>
                <h3 style="color:{PRIMARY}">Welcome 👋</h3>
                <p style="color:{MUTED}">
                    What should we call you?
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            name = st.text_input(
                "Your name",
                value=st.session_state.username,
                placeholder="Enter your name",
            )
            enter = st.form_submit_button(
                "Continue →", use_container_width=True, type="primary"
            )

        if enter:
            if name.strip():
                save_user(name.strip())
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.warning("Please enter your name.")

    st.stop()


# -------------------- DASHBOARD HEADER --------------------
left, right = st.columns([3, 1])

with left:
    st.markdown(
        f"""
        <div class="topbar">
            <h1>✓ My Task Tracker</h1>
            <p>Welcome, {safe(st.session_state.username)} 👋</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div style="text-align:right;padding:17px 2px;color:{MUTED}">
            {datetime.now().strftime("%A, %d %B %Y")}
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.button("↻ Change username"):
    st.session_state.page = "login"
    st.rerun()


# -------------------- STATISTICS --------------------
tasks = st.session_state.tasks
total = len(tasks)
completed = sum(t.get("status") == "Completed" for t in tasks)
pending = total - completed
percent = round(completed / total * 100) if total else 0

st.markdown("### Your Overview")

stats = [
    ("TOTAL TASKS", total, PRIMARY),
    ("PENDING", pending, ORANGE),
    ("COMPLETED", completed, GREEN),
]

columns = st.columns(3)

for col, (label, value, color) in zip(columns, stats):
    with col:
        st.markdown(
            f"""
            <div class="stat-card" style="--accent:{color}">
                <div class="stat-number">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

progress_left, progress_right = st.columns([3, 1])

with progress_left:
    st.markdown("**Your Progress**")

with progress_right:
    st.markdown(
        f"<div style='text-align:right;color:{PRIMARY};"
        f"font-weight:750'>{percent}% Completed</div>",
        unsafe_allow_html=True,
    )

st.progress(percent / 100)
st.divider()


# -------------------- CREATE TASK + TASK LIST --------------------
form_col, list_col = st.columns([1, 2], gap="large")

with form_col:
    st.subheader("＋ Create Task")
    st.markdown(
        '<div class="section-caption">Add details to your task.</div>',
        unsafe_allow_html=True,
    )

    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input(
            "TASK", placeholder="What do you need to do?"
        )
        category = st.selectbox("CATEGORY", CATEGORIES)
        priority = st.selectbox("PRIORITY", PRIORITIES, index=1)
        due_date = st.text_input(
            "DUE DATE & TIME",
            placeholder="10-10-2026 06:00 PM",
        )
        st.caption(
            "Format: DD-MM-YYYY HH:MM AM/PM. "
            "Leave blank for no deadline."
        )
        notes = st.text_area("NOTES", height=100)

        add = st.form_submit_button(
            "＋ Add Task", use_container_width=True, type="primary"
        )

    if add:
        if not title.strip():
            st.warning("Please enter a task first.")
        else:
            due_text = due_date.strip() or "No deadline"

            if due_text != "No deadline":
                try:
                    datetime.strptime(due_text, DATE_FORMAT)
                except ValueError:
                    st.error(
                        "Invalid date. Example: 10-10-2026 06:00 PM"
                    )
                    st.stop()

            new_task = {
                "title": title.strip(),
                "category": category,
                "priority": priority,
                "due_date": due_text,
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "status": "Pending",
                "notes": notes.strip(),
            }

            tasks.append(new_task)
            if save_tasks():
                st.success("Task added!")
                st.rerun()


# -------------------- SEARCH, FILTER & SORT --------------------
with list_col:
    st.subheader("Your Tasks")
    st.markdown(
        '<div class="section-caption">'
        'Search, filter and manage your tasks.'
        '</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "🔍 Search tasks",
        placeholder="Search title, notes, category...",
    )

    filter_choice = st.radio(
        "Filter tasks",
        FILTERS,
        horizontal=True,
    )

    sort_due = st.checkbox("Sort by due date")

    visible = []
    query = search.strip().lower()

    for idx, task in enumerate(tasks):
        searchable = " ".join([
            str(task.get("title", "")),
            str(task.get("category", "")),
            str(task.get("priority", "")),
            str(task.get("status", "")),
            str(task.get("notes", "")),
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

        visible.append((idx, task))

    if sort_due:
        visible.sort(key=lambda item: parse_due(item[1]) or datetime.max)

    st.caption(f"Showing {len(visible)} of {total} tasks")

    if not visible:
        st.info("No tasks found. Add a task or change the filter.")

    # -------------------- TASK CARDS --------------------
    for idx, task in visible:
        title_text = task.get("title", "Untitled Task")
        priority_value = task.get("priority", "Medium")
        current_status = status_text(task)
        due_value = task.get("due_date", "No deadline")
        category_value = task.get("category", "General")

        with st.container(border=True):
            a, b = st.columns([4, 1])

            with a:
                st.markdown(
                    f'<div class="task-heading">{safe(title_text)}</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="task-meta">
                        {safe(category_value)} &nbsp; • &nbsp;
                        {safe(due_value)}
                    </div>
                    <span class="pill"
                        style="background:{priority_color(priority_value)}20;
                        color:{priority_color(priority_value)}">
                        {safe(priority_value)} Priority
                    </span>
                    <span class="pill"
                        style="background:{status_color(task)}20;
                        color:{status_color(task)}">
                        {safe(current_status)}
                    </span>
                    """,
                    unsafe_allow_html=True,
                )

            with b:
                if task.get("status") == "Completed":
                    st.button(
                        "✓ Done",
                        key=f"done_{idx}",
                        disabled=True,
                        use_container_width=True,
                    )
                elif st.button(
                    "✓ Complete",
                    key=f"complete_{idx}",
                    use_container_width=True,
                ):
                    tasks[idx]["status"] = "Completed"
                    if save_tasks():
                        st.rerun()

            with st.expander("👁 Details / ✏ Edit"):
                st.write("**Category:**", category_value)
                st.write("**Priority:**", priority_value)
                st.write("**Due date:**", due_value)
                st.write("**Status:**", task.get("status", "Pending"))
                st.write("**Created:**", task.get("date", "Unknown"))
                st.write("**Notes:**", task.get("notes", "") or "No notes added.")

                with st.form(f"edit_{idx}"):
                    new_title = st.text_input(
                        "Task", value=title_text
                    )

                    cat_index = (
                        CATEGORIES.index(category_value)
                        if category_value in CATEGORIES else 6
                    )
                    new_category = st.selectbox(
                        "Category", CATEGORIES, index=cat_index
                    )

                    pri_index = (
                        PRIORITIES.index(priority_value)
                        if priority_value in PRIORITIES else 1
                    )
                    new_priority = st.selectbox(
                        "Priority", PRIORITIES, index=pri_index
                    )

                    new_due = st.text_input(
                        "Due date & time", value=due_value
                    )
                    new_notes = st.text_area(
                        "Notes", value=task.get("notes", "")
                    )

                    save_edit = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                        type="primary",
                    )

                if save_edit:
                    if not new_title.strip():
                        st.error("Task name cannot be empty.")
                    else:
                        date_text = new_due.strip() or "No deadline"
                        valid = date_text == "No deadline"

                        if not valid:
                            try:
                                datetime.strptime(date_text, DATE_FORMAT)
                                valid = True
                            except ValueError:
                                st.error(
                                    "Use DD-MM-YYYY HH:MM AM/PM "
                                    "or No deadline."
                                )

                        if valid:
                            tasks[idx].update({
                                "title": new_title.strip(),
                                "category": new_category,
                                "priority": new_priority,
                                "due_date": date_text,
                                "notes": new_notes.strip(),
                            })

                            if save_tasks():
                                st.success("Task updated!")
                                st.rerun()

                d1, d2 = st.columns(2)

                with d1:
                    if st.button(
                        "🗑 Delete",
                        key=f"delete_{idx}",
                        use_container_width=True,
                    ):
                        st.session_state.confirm_delete = idx

                with d2:
                    if st.button(
                        "❌ Clear All Tasks",
                        key=f"clear_{idx}",
                        use_container_width=True,
                    ):
                        st.session_state.confirm_clear = True


# -------------------- DELETE CONFIRMATION --------------------
delete_idx = st.session_state.confirm_delete

if delete_idx is not None:
    if 0 <= delete_idx < len(tasks):
        st.warning(
            f"Delete '{tasks[delete_idx].get('title', 'this task')}'?"
        )
        yes, no = st.columns(2)

        with yes:
            if st.button("Yes, delete", type="primary"):
                tasks.pop(delete_idx)
                if save_tasks():
                    st.session_state.confirm_delete = None
                    st.rerun()

        with no:
            if st.button("Cancel delete"):
                st.session_state.confirm_delete = None
                st.rerun()
    else:
        st.session_state.confirm_delete = None


# -------------------- CLEAR ALL CONFIRMATION --------------------
if st.session_state.confirm_clear:
    st.warning("Are you sure you want to delete ALL tasks?")
    yes, no = st.columns(2)

    with yes:
        if st.button("Yes, clear all", type="primary"):
            st.session_state.tasks.clear()
            if save_tasks():
                st.session_state.confirm_clear = False
                st.session_state.confirm_delete = None
                st.rerun()

    with no:
        if st.button("Cancel clear"):
            st.session_state.confirm_clear = False
            st.rerun()


# -------------------- FOOTER --------------------
st.divider()

st.markdown(
    f"""
    <div style="text-align:center;color:{MUTED};font-size:12px;padding:10px">
        ✓ My Task Tracker • Stay organized, one task at a time.
    </div>
    """,
    unsafe_allow_html=True,
)
