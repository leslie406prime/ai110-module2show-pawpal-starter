"""Streamlit interface for the PawPal+ backend."""

import streamlit as st
from datetime import date
import os
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.write("Manage your pets' care tasks and build a daily plan.")
DATA_PATH = Path(os.environ.get("PAWPAL_DATA_PATH", str(Path(__file__).with_name("data.json"))))
st.caption("Changes are saved locally to data.json and restored when the app restarts.")


def persist_owner() -> bool:
    """Save the current owner and report filesystem failures without losing session data."""
    try:
        st.session_state.owner.save_to_json(DATA_PATH)
        return True
    except (OSError, ValueError) as error:
        st.error(f"Could not save data. Your changes remain in this session: {error}")
        return False

# Initialize once; subsequent widget interactions reuse the same object graph.
if "owner" not in st.session_state:
    try:
        st.session_state.owner = Owner.load_from_json(DATA_PATH)
    except FileNotFoundError:
        st.session_state.owner = Owner("Jordan", available_minutes=60)
    except (OSError, ValueError) as error:
        st.error(f"Could not load data.json: {error}. Fix or restore the file before continuing; it has not been overwritten.")
        st.stop()
if "show_schedule" not in st.session_state:
    st.session_state.show_schedule = False
owner = st.session_state.owner
if st.button("Save data now", key="save_data"):
    if persist_owner():
        st.success("Saved pets and tasks to data.json.")

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
            persist_owner()
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
            persist_owner()
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
        priority = st.selectbox("Priority", ["high", "medium", "low"], format_func=str.title, key="task_priority")
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
                persist_owner()
                st.success(f"Added task for {owner.pets[pet_index].name}.")

    scheduler = Scheduler(owner)
    pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
    pet_filter = st.selectbox(
        "Filter by pet", [None] + list(dict.fromkeys(pet.name for pet in owner.pets)),
        format_func=lambda name: "All pets" if name is None else name, key="filter_pet",
    )
    status_filter = st.selectbox("Filter by status", ["All", "Pending", "Complete"], key="filter_status")
    completion_filter = {"All": None, "Pending": False, "Complete": True}[status_filter]
    visible_tasks = scheduler.sort_by_time(scheduler.filter_tasks(pet_filter, completion_filter))
    st.caption("Tasks sorted by start time; anytime tasks appear last. Filters affect this table only.")
    task_rows = [
        {"Pet": pet_names[id(task)], "Task": task.description, "Minutes": task.duration_minutes,
         "Priority": task.priority, "Frequency": task.frequency,
         "Due date": task.due_date.isoformat(), "Time": task.time or "Anytime",
         "Status": "✅ Complete" if task.completed else "⏳ Pending"}
        for task in visible_tasks
    ]
    if task_rows:
        st.table(task_rows)
    else:
        st.info("No tasks match these filters. Change the filters or add a task above.")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.write("**Care tasks needing your attention**")
        for warning in conflicts:
            st.warning(warning + ". Arrange separate start times for these activities before following the plan.")
        st.caption("Warnings check identical dates and start times across all pending tasks, including tasks hidden by filters. Times are not adjusted automatically.")
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
                if persist_owner():
                    st.rerun()
    st.caption("Daily and weekly tasks create their next occurrence on completion. Other frequencies are descriptive.")

st.subheader("Find a free slot")
with st.form("slot_form"):
    slot_date = st.date_input("Day", value=date.today(), key="slot_date")
    slot_duration = st.number_input("Time needed (minutes)", min_value=1, value=15, step=1, key="slot_duration")
    slot_start = st.text_input("Window start (HH:MM)", value="08:00", key="slot_start")
    slot_end = st.text_input("Window end (HH:MM)", value="20:00", key="slot_end")
    if st.form_submit_button("Find next available slot", key="find_slot"):
        try:
            slot = Scheduler(owner).next_available_slot(int(slot_duration), slot_date, slot_start, slot_end)
        except ValueError as error:
            st.error(str(error))
        else:
            if slot is None:
                st.warning("No gap fits inside that window. Try another day or a wider window.")
            else:
                st.success(f"Next available slot: {slot} on {slot_date} for {slot_duration} minutes.")
st.caption("Checks full durations across all pets. Untimed and completed tasks do not reserve a slot; suggestions do not move tasks.")

st.subheader("Today's Schedule")
if st.button("Generate schedule", key="generate_schedule", disabled=not owner.get_all_tasks()):
    st.session_state.show_schedule = True

if st.session_state.show_schedule:
    # Recompute after edits so a displayed plan always reflects current data.
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
    if plan:
        st.success(f"Daily plan ready: {len(plan)} tasks, ordered by priority then start time.")
        st.table([
            {"Order": index, "Pet": pet_names[id(task)], "Task": task.description,
             "Time": task.time or "Anytime",
             "Minutes": task.duration_minutes, "Priority": task.priority}
            for index, task in enumerate(plan, start=1)
        ])
    else:
        st.info("No pending tasks fit the available time.")
    st.write(f"Total scheduled: {scheduler.get_total_duration()} / {owner.available_minutes} minutes")
    if scheduler.skipped_tasks:
        st.warning(f"{len(scheduler.skipped_tasks)} pending task(s) did not fit the time budget. Review the explanation below.")
    with st.expander("Why this plan?"):
        st.text(scheduler.explain_plan())
