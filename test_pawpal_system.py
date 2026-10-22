"""Core scheduling behavior, including the Owner-to-Scheduler boundary."""

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_scheduler_uses_owner_task_access_across_pets(monkeypatch):
    walk = Task("Walk", "exercise", 20, "high")
    feed = Task("Feed cat", "feeding", 5, "high")
    owner = Owner("Jordan", 25, pets=[
        Pet("Mochi", "dog", [walk]), Pet("Luna", "cat", [feed])
    ])
    original = owner.get_all_tasks
    calls = []

    def retrieve():
        calls.append(True)
        return original()

    monkeypatch.setattr(owner, "get_all_tasks", retrieve)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    assert calls == [True]
    assert plan[0] is walk
    assert plan[1] is feed
    assert scheduler.get_total_duration() == 25
    assert "Selected Feed cat" in scheduler.explain_plan()


def test_priority_preferences_and_stable_ties():
    ordinary = Task("Groom", "grooming", 5)
    preferred = Task("Feed", "feeding", 5)
    preferred_second = Task("Refill water", "feeding", 5)
    urgent = Task("Medicine", "health", 5, "high")
    owner = Owner("Jordan", 20, ["feeding"], [
        Pet("Mochi", "dog", [ordinary, preferred, preferred_second, urgent])
    ])
    assert Scheduler(owner).generate_plan() == [
        urgent, preferred, preferred_second, ordinary
    ]


def test_skip_long_tasks_and_regenerate_after_completion():
    long_task = Task("Long walk", "exercise", 30, "high")
    short_task = Task("Feed", "feeding", 5)
    owner = Owner("Jordan", 10, pets=[Pet("Mochi", "dog", [long_task, short_task])])
    scheduler = Scheduler(owner)
    assert scheduler.generate_plan() == [short_task]
    assert scheduler.skipped_tasks == [long_task]
    assert "Skipped Long walk" in scheduler.explain_plan()
    short_task.mark_complete()
    owner.set_available_time(30)
    assert scheduler.generate_plan() == [long_task]
    assert scheduler.skipped_tasks == []
    assert scheduler.get_total_duration() == 30
    # Owner exposes completed tasks too; filtering belongs to the scheduler.
    assert owner.get_all_tasks() == [long_task, short_task]


def test_empty_and_zero_time_plans():
    owner = Owner("Jordan", 0)
    scheduler = Scheduler(owner)
    assert scheduler.generate_plan() == []
    assert "No pending tasks" in scheduler.explain_plan()
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Feed", "feeding", 5))
    owner.add_pet(pet)
    assert scheduler.generate_plan() == []
    assert scheduler.skipped_tasks == pet.tasks


@pytest.mark.parametrize("minutes", [0, -1, 1.5, True])
def test_task_rejects_invalid_durations(minutes):
    with pytest.raises(ValueError):
        Task("Feed", "feeding", minutes)


def test_invalid_edits_leave_existing_values_unchanged():
    task = Task("Feed", "feeding", 5, frequency="twice daily")
    with pytest.raises(ValueError):
        task.update_details("Walk", "exercise", -2, "high")
    assert task.description == "Feed"
    assert task.duration_minutes == 5
    task.update_details("Dinner", "feeding", 10, "high")
    assert task.description == "Dinner"
    assert task.frequency == "twice daily"
    with pytest.raises(ValueError):
        Task("Feed", "feeding", 5, "urgent")
    with pytest.raises(ValueError):
        Owner("Jordan", -1)


def test_independent_lists_and_identity_based_removal():
    pet = Pet("Mochi", "dog")
    other = Pet("Luna", "cat")
    task = Task("Feed", "feeding", 5)
    equal_task = Task("Feed", "feeding", 5)
    pet.add_task(task)
    pet.add_task(equal_task)
    assert other.tasks == []
    pet.remove_task(equal_task)
    assert pet.tasks[0] is task
    assert pet.get_pending_tasks() == [task]
    task.mark_complete()
    assert pet.get_pending_tasks() == []
    with pytest.raises(ValueError):
        pet.add_task(task)
    with pytest.raises(ValueError):
        pet.remove_task(equal_task)


def test_returned_lists_do_not_mutate_owner_or_scheduler():
    task = Task("Feed", "feeding", 5)
    owner = Owner("Jordan", 10, pets=[Pet("Mochi", "dog", [task])])
    owner.get_all_tasks().clear()
    scheduler = Scheduler(owner)
    scheduler.generate_plan().clear()
    assert scheduler.selected_tasks == [task]
    assert owner.get_all_tasks() == [task]
