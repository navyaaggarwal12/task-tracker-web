import streamlit as st

st.set_page_config(page_title="Task Tracker", page_icon="✅")

st.title("✅ My Task Tracker")
st.write("Manage your daily tasks easily!")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

task = st.text_input("Enter your task")

if st.button("Add Task"):
    if task.strip():
        st.session_state.tasks.append({
            "name": task.strip(),
            "done": False
        })
        st.rerun()

st.subheader("My Tasks")

for i, item in enumerate(st.session_state.tasks):
    col1, col2 = st.columns([4, 1])

    with col1:
        checked = st.checkbox(
            item["name"],
            value=item["done"],
            key=f"task_{i}"
        )
        st.session_state.tasks[i]["done"] = checked

    with col2:
        if st.button("Delete", key=f"delete_{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()

total = len(st.session_state.tasks)
completed = sum(t["done"] for t in st.session_state.tasks)

st.divider()
st.write(f"Total tasks: {total}")
st.write(f"Completed: {completed}")
st.write(f"Pending: {total - completed}")