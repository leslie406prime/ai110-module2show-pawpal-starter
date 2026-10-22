# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation summary

The backend in `pawpal_system.py` uses four dataclasses. `Task` describes a care
activity and tracks completion. `Pet` manages its tasks, and `Owner.get_all_tasks()`
combines tasks from all of the owner's pets. `Scheduler` calls that method,
filters completed tasks, and selects activities by priority and preferences
within one shared daily time budget. It also explains selected and skipped tasks.

`main.py` demonstrates the system with two pets and readable terminal output.
The tests cover basic task actions, multi-pet scheduling, and Streamlit form
interactions. Daily and weekly completion creates the next dated occurrence.

`app.py` imports the backend classes and keeps one `Owner` in
`st.session_state`. Pet and task forms call `Owner.add_pet()` and `Pet.add_task()`;
the schedule uses `Scheduler` to plan across all pets. Data survives widget
reruns within the session, but is not saved permanently across browser reloads
or server restarts.

Run the browser app with the virtual environment active:

```bash
python -m streamlit run app.py
```

Save owner details, add pets, select a pet when adding each task, and click
**Generate schedule** to see the daily plan and its explanation.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Sample Output

Run `python main.py` with the virtual environment active. The demo uses a fixed
2026-10-22 date for reproducible output:

```text
Today's Schedule (demo date: 2026-10-22)
Owner: Jordan | Available time: 60 min
08:00 | Mochi: Morning walk | 20 min | high priority
08:00 | Luna: Breakfast | 5 min | high priority
12:00 | Luna: Play session | 10 min | medium priority
18:00 | Mochi: Brush coat | 15 min | low priority
Total scheduled: 50 / 60 min

Pending tasks for Mochi (sorted by time):
- 08:00: Morning walk
- 18:00: Brush coat

Conflict warnings:
WARNING: Conflict on 2026-10-22 at 08:00: Mochi: Morning walk; Luna: Breakfast

Completed: Mochi's Morning walk
Next daily occurrence: 2026-10-23 at 08:00
Completed tasks: 1
Pending tasks: 4
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run just the two quick tests:
python -m pytest tests/test_pawpal.py
```

Sample test output:

```
................................                                         [100%]
32 passed in 4.75s
```

## Smarter Scheduling

| Feature | Method | Behavior |
|---------|--------|----------|
| Time sorting | `Scheduler.sort_by_time()` | Uses a lambda key on validated HH:MM strings; stable ties and untimed tasks last; returns a new list. |
| Filtering | `Scheduler.filter_tasks()` | Combines optional case-insensitive pet name and completion status filters using `Owner.get_all_tasks()`. |
| Daily planning | `Scheduler.generate_plan()` | Selects pending tasks due today or earlier by priority/preferences within the shared budget, then displays chosen tasks by time. |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns warnings for pending tasks with the same date and exact start time, across the same or different pets. |
| Recurrence | `Scheduler.mark_task_complete()` | Completes once and attaches a fresh daily/weekly task to the same pet using `timedelta(days=1)` or `timedelta(days=7)`. |

Use `Scheduler.mark_task_complete(task)` for recurring workflows.
`Task.mark_complete()` only changes the task's status. A repeated scheduler
completion does not create duplicates. Late completion advances from today;
early completion advances from the future due date. New instances preserve time,
duration, priority, category, and frequency. Other frequencies, including twice
daily, remain descriptive and do not generate new occurrences.

Dates default to the server's local date. Optional `today` arguments make demos
and tests reproducible. Conflict checks do not detect duration overlaps, resolve
conflicts, or reject tasks. Pet name filters include all pets with that name.
The browser form also accepts due dates/start times and supports recurring
completion; conflict warnings appear alongside generated plans.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
