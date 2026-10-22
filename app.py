"""Streamlit interface for the PawPal+ backend."""

import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.write("Manage your pets' care tasks and build a daily plan.")
st.caption("Your data stays available during this session. Reloading the browser may reset it.")

# Initialize once; subsequent widget interactions reuse the same object graph.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=60)
if "show_schedule" not in st.session_state:
    st.session_state.show_schedule = False
owner = st.session_state.owner

st.subheader("Owner")
with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value=owner.name, key="owner_name")
    available_minutes = st.number_input(
        "Available time (minutes)", min_value=0, value=owner.available_minutes,
        step=1, key="available_minutes",
    )
    preferences = st.multiselect(
        "Preferred categories", ["exercise", "feeding", "health", "enrichment", "grooming", "other"],
        default=owner.preferred_categories, key="preferences",
    )
    if st.form_submit_button("Save owner", key="save_owner"):
        if not owner_name.strip():
            st.error("Enter an owner name.")
        else:
            owner.name = owner_name.strip()
            owner.set_available_time(int(available_minutes))
            owner.set_preferences(preferences)
            st.success("Owner details saved.")

st.subheader("Pets")
with st.form("pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", key="pet_name")
    species = st.selectbox("Species", ["dog", "cat", "other"], key="species")
    if st.form_submit_button("Add pet", key="add_pet"):
        if not pet_name.strip():
            st.error("Enter a pet name.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species))
            st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.table([{"Pet": pet.name, "Species": pet.species, "Tasks": len(pet.tasks)}
              for pet in owner.pets])
else:
    st.info("Add a pet to start creating care tasks.")

st.subheader("Tasks")
if owner.pets:
    with st.form("task_form", clear_on_submit=True):
        pet_index = st.selectbox(
            "Pet", range(len(owner.pets)),
            format_func=lambda index: f"{index + 1}. {owner.pets[index].name} ({owner.pets[index].species})",
            key="task_pet",
        )
        description = st.text_input("Task description", key="task_description")
        category = st.selectbox(
            "Category", ["exercise", "feeding", "health", "enrichment", "grooming", "other"],
            key="task_category",
        )
        duration = st.number_input("Duration (minutes)", min_value=1, value=20, step=1, key="task_duration")
        priority = st.selectbox("Priority", ["high", "medium", "low"], key="task_priority")
        frequency = st.selectbox("Frequency", ["daily", "twice daily", "weekly", "as needed"], key="task_frequency")
        due_date = st.date_input("Due date", value=date.today(), key="task_due_date")
        start_time = st.text_input("Start time (HH:MM, optional)", key="task_time")
        if st.form_submit_button("Add task", key="add_task"):
            try:
                task = Task(description.strip(), category, int(duration), priority, frequency,
                            time=start_time.strip() or None, due_date=due_date)
                owner.pets[pet_index].add_task(task)
            except ValueError as error:
                st.error(str(error))
            else:
                st.success(f"Added task for {owner.pets[pet_index].name}.")

    task_rows = [
        {"Pet": pet.name, "Task": task.description, "Minutes": task.duration_minutes,
         "Priority": task.priority, "Frequency": task.frequency,
         "Due date": task.due_date.isoformat(), "Time": task.time or "Anytime",
         "Status": "Complete" if task.completed else "Pending"}
        for pet in owner.pets for task in pet.tasks
    ]
    if task_rows:
        st.table(task_rows)
    else:
        st.info("No tasks yet. Add one above.")

    scheduler = Scheduler(owner)
    pending = scheduler.filter_tasks(completed=False)
    if pending:
        pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
        with st.form("completion_form"):
            complete_index = st.selectbox(
                "Task to complete", range(len(pending)),
                format_func=lambda index: (
                    f"{pet_names[id(pending[index])]}: {pending[index].description} "
                    f"({pending[index].due_date})"
                ), key="complete_task_index",
            )
            if st.form_submit_button("Mark complete", key="mark_complete"):
                scheduler.mark_task_complete(pending[complete_index])
                st.rerun()
    st.caption("Daily and weekly tasks create their next occurrence on completion. Other frequencies are descriptive.")

st.subheader("Today's Schedule")
if st.button("Generate schedule", key="generate_schedule", disabled=not owner.get_all_tasks()):
    st.session_state.show_schedule = True

if st.session_state.show_schedule:
    # Recompute after edits so a displayed plan always reflects current data.
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
    if plan:
        st.table([
            {"Order": index, "Pet": pet_names[id(task)], "Task": task.description,
             "Time": task.time or "Anytime",
             "Minutes": task.duration_minutes, "Priority": task.priority}
            for index, task in enumerate(plan, start=1)
        ])
    else:
        st.info("No pending tasks fit the available time.")
    st.write(f"Total scheduled: {scheduler.get_total_duration()} / {owner.available_minutes} minutes")
    for warning in scheduler.detect_conflicts(plan):
        st.warning(warning)
    with st.expander("Why this plan?"):
        st.text(scheduler.explain_plan())
