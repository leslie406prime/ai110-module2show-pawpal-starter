"""Core task and scheduling acceptance tests; see tests/TEST_PLAN.md."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion():
    task = Task("Breakfast", "feeding", 5)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    pet = Pet("Mochi", "dog")
    task = Task("Morning walk", "exercise", 20)
    original_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == original_count + 1
    assert pet.tasks[-1] is task


def test_sorting_correctness_at_day_boundaries():
    tasks = [
        Task("Bedtime", "feeding", 5, time="23:59"),
        Task("Breakfast", "feeding", 5, time="09:05"),
        Task("Midnight medicine", "health", 5, time="00:00"),
        Task("Lunch", "feeding", 5, time="12:00"),
    ]
    scheduler = Scheduler(Owner("Jordan", 60, pets=[Pet("Mochi", "dog", tasks)]))

    result = scheduler.sort_by_time()

    assert [task.time for task in result] == ["00:00", "09:05", "12:00", "23:59"]
    assert tasks[0].description == "Bedtime"


def test_daily_completion_creates_next_day_for_correct_pet():
    today = date(2026, 10, 22)
    task = Task("Medicine", "health", 10, "high", "daily",
                time="08:00", due_date=today)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat", [task])
    scheduler = Scheduler(Owner("Jordan", 60, pets=[mochi, luna]))

    next_task = scheduler.mark_task_complete(task, today=today)

    assert task.completed is True
    assert next_task is not task
    assert next_task.due_date == date(2026, 10, 23)
    assert next_task.completed is False
    assert (next_task.description, next_task.category, next_task.duration_minutes,
            next_task.priority, next_task.frequency, next_task.time) == (
                "Medicine", "health", 10, "high", "daily", "08:00"
            )
    assert luna.tasks[1] is next_task
    assert mochi.tasks == []


def test_conflict_detection_groups_three_duplicate_times():
    today = date(2026, 10, 22)
    mochi = Pet("Mochi", "dog", [
        Task("Walk", "exercise", 20, time="08:00", due_date=today),
        Task("Medicine", "health", 5, time="08:00", due_date=today),
    ])
    luna = Pet("Luna", "cat", [
        Task("Breakfast", "feeding", 5, time="08:00", due_date=today)
    ])
    scheduler = Scheduler(Owner("Jordan", 60, pets=[mochi, luna]))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "2026-10-22 at 08:00" in warnings[0]
    for label in ["Mochi: Walk", "Mochi: Medicine", "Luna: Breakfast"]:
        assert label in warnings[0]
    assert len(scheduler.owner.get_all_tasks()) == 3


def test_pet_with_no_tasks_has_empty_results():
    scheduler = Scheduler(Owner("Jordan", 60, pets=[Pet("Mochi", "dog")]))

    assert scheduler.sort_by_time() == []
    assert scheduler.filter_tasks(pet_name="Mochi", completed=False) == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.generate_plan(today=date(2026, 10, 22)) == []
    assert scheduler.get_total_duration() == 0


def test_duration_overlap_is_outside_exact_start_conflict_rule():
    today = date(2026, 10, 22)
    pet = Pet("Mochi", "dog", [
        Task("Walk", "exercise", 30, time="08:00", due_date=today),
        Task("Feed", "feeding", 5, time="08:15", due_date=today),
    ])
    scheduler = Scheduler(Owner("Jordan", 60, pets=[pet]))

    # Record the documented limitation rather than claiming overlap protection.
    assert scheduler.detect_conflicts() == []
