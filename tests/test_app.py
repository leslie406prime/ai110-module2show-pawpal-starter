"""Exercise the UI-to-backend connection across Streamlit reruns."""

from pathlib import Path
from datetime import date, timedelta

from streamlit.testing.v1 import AppTest

from pawpal_system import Owner, Pet, Task


APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_pet_and_task_persist_across_reruns_and_schedule_all_pets():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    owner = app.session_state["owner"]
    assert isinstance(owner, Owner)

    app.text_input(key="pet_name").input("Mochi")
    app.button(key="add_pet").click().run()
    assert not app.exception
    assert isinstance(owner.pets[0], Pet)
    app.run()
    assert app.session_state["owner"] is owner
    assert len(owner.pets) == 1

    app.text_input(key="task_description").input("Morning walk")
    app.button(key="add_task").click().run()
    assert not app.exception
    assert isinstance(owner.pets[0].tasks[0], Task)

    app.text_input(key="pet_name").input("Luna")
    app.selectbox(key="species").select("cat")
    app.button(key="add_pet").click().run()
    app.selectbox(key="task_pet").select(1)
    app.text_input(key="task_description").input("Breakfast")
    app.number_input(key="task_duration").set_value(5)
    app.button(key="add_task").click().run()
    assert not app.exception
    assert len(owner.get_all_tasks()) == 2

    app.button(key="generate_schedule").click().run()
    assert not app.exception
    assert set(app.table[-1].value["Pet"]) == {"Mochi", "Luna"}
    app.run()
    assert len(owner.get_all_tasks()) == 2
    assert set(app.table[-1].value["Pet"]) == {"Mochi", "Luna"}


def test_invalid_forms_preserve_state_and_owner_edits_keep_pets():
    app = AppTest.from_file(APP, default_timeout=30).run()
    app.text_input(key="pet_name").input("   ")
    app.button(key="add_pet").click().run()
    assert app.error
    assert app.session_state["owner"].pets == []

    app.text_input(key="pet_name").input("Mochi")
    app.button(key="add_pet").click().run()
    app.text_input(key="task_description").input("   ")
    app.button(key="add_task").click().run()
    assert app.error
    assert app.session_state["owner"].get_all_tasks() == []

    app.text_input(key="owner_name").input("Alex")
    app.number_input(key="available_minutes").set_value(0)
    app.button(key="save_owner").click().run()
    owner = app.session_state["owner"]
    assert owner.name == "Alex"
    assert owner.available_minutes == 0
    assert owner.pets[0].name == "Mochi"
    assert not app.exception


def test_ui_completion_creates_one_next_occurrence():
    app = AppTest.from_file(APP, default_timeout=30)
    task = Task("Breakfast", "feeding", 5, time="08:00")
    owner = Owner("Jordan", 60, pets=[Pet("Mochi", "dog", [task])])
    app.session_state["owner"] = owner
    app.run()
    app.button(key="mark_complete").click().run()
    assert not app.exception
    assert task.completed
    assert len(owner.get_all_tasks()) == 2
    assert owner.pets[0].tasks[1].due_date == date.today() + timedelta(days=1)
    app.run()
    assert len(owner.get_all_tasks()) == 2
