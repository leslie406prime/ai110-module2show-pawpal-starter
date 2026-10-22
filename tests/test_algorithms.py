"""Scheduling algorithms and recurrence edge cases."""

from datetime import date

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


TODAY = date(2026, 12, 31)


def make_task(description="Feed", time="08:00", frequency="daily", due_date=TODAY):
    return Task(description, "feeding", 5, frequency=frequency, time=time, due_date=due_date)


def make_scheduler(*tasks):
    return Scheduler(Owner("Jordan", 60, pets=[Pet("Mochi", "dog", list(tasks))]))


def test_time_sorting_is_stable_nonmutating_and_puts_untimed_last():
    late, early, tie, untimed = (
        make_task("Late", "18:00"), make_task("Early", "08:00"),
        make_task("Tie", "08:00"), make_task("Anytime", None)
    )
    scheduler = make_scheduler(late, untimed, early, tie)
    assert scheduler.sort_by_time() == [early, tie, late, untimed]
    assert scheduler.owner.get_all_tasks() == [late, untimed, early, tie]
    assert scheduler.sort_by_time([]) == []


@pytest.mark.parametrize("time", ["8:00", "24:00", "12:60", "bad", "", 800])
def test_invalid_start_times(time):
    with pytest.raises(ValueError, match="HH:MM"):
        make_task(time=time)


def test_pet_and_status_filters_combine_without_mutating_owner():
    pending, completed, cat_task = make_task(), make_task(), make_task()
    completed.mark_complete()
    scheduler = make_scheduler(pending, completed)
    scheduler.owner.add_pet(Pet("Luna", "cat", [cat_task]))
    assert scheduler.filter_tasks(" moCHI ", False) == [pending]
    assert scheduler.filter_tasks(completed=True) == [completed]
    assert scheduler.filter_tasks("missing") == []
    assert len(scheduler.filter_tasks()) == 3


@pytest.mark.parametrize("frequency, expected", [
    ("daily", date(2027, 1, 1)), ("weekly", date(2027, 1, 7))
])
def test_recurring_completion_preserves_pet_details_and_is_idempotent(frequency, expected):
    task = make_task(frequency=frequency)
    scheduler = make_scheduler(task)
    next_task = scheduler.mark_task_complete(task, today=TODAY)
    assert task.completed
    assert next_task is not task
    assert not next_task.completed
    assert next_task.due_date == expected
    assert next_task.time == task.time
    assert next_task.frequency == frequency
    assert scheduler.owner.pets[0].tasks[-1] is next_task
    assert scheduler.mark_task_complete(task, today=TODAY) is None
    assert len(scheduler.owner.get_all_tasks()) == 2
    assert scheduler.generate_plan(today=TODAY) == []
    assert scheduler.generate_plan(today=expected) == [next_task]


def test_late_completion_and_one_off_tasks():
    task = make_task(due_date=date(2026, 1, 1))
    scheduler = make_scheduler(task)
    assert scheduler.mark_task_complete(task, today=TODAY).due_date == date(2027, 1, 1)
    one_off = make_task(frequency="as needed")
    scheduler.owner.pets[0].add_task(one_off)
    assert scheduler.mark_task_complete(one_off, today=TODAY) is None
    assert one_off.completed
    with pytest.raises(ValueError):
        scheduler.mark_task_complete(make_task(), today=TODAY)


def test_conflicts_across_pets_ignore_completed_and_different_dates():
    first, second = make_task("Walk"), make_task("Breakfast")
    scheduler = make_scheduler(first)
    scheduler.owner.add_pet(Pet("Luna", "cat", [second]))
    scheduler.owner.pets[0].add_task(make_task(due_date=date(2027, 1, 1)))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Mochi: Walk" in warnings[0]
    assert "Luna: Breakfast" in warnings[0]
    assert "08:00" in warnings[0]
    second.mark_complete()
    assert scheduler.detect_conflicts() == []


def test_priority_selection_then_time_within_priority():
    late = make_task("Late high", "18:00")
    late.priority = "high"
    early = make_task("Early low", "08:00")
    early.priority = "low"
    scheduler = make_scheduler(late, early)
    scheduler.owner.set_available_time(5)
    assert scheduler.generate_plan(today=TODAY) == [late]
    scheduler.owner.set_available_time(10)
    assert scheduler.generate_plan(today=TODAY) == [late, early]


@pytest.mark.parametrize("base, expected", [
    (date(2028, 2, 28), date(2028, 2, 29)),
    (date(2027, 2, 28), date(2027, 3, 1)),
])
def test_daily_recurrence_handles_calendar_boundaries(base, expected):
    task = make_task(due_date=base)
    assert make_scheduler(task).mark_task_complete(task, today=base).due_date == expected


def test_early_completion_advances_from_due_date_and_same_pet_conflicts():
    task = make_task(due_date=date(2027, 1, 5))
    scheduler = make_scheduler(task, make_task("Another task", due_date=task.due_date))
    assert len(scheduler.detect_conflicts()) == 1
    assert scheduler.mark_task_complete(task, today=TODAY).due_date == date(2027, 1, 6)
