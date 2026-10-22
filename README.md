# PawPal+

PawPal+ helps one owner manage care for multiple pets, prioritize daily activities,
spot simultaneous commitments, and find a free slot. A Streamlit UI and terminal
demo share the same tested Python backend.

## Features

- Manage pets and tasks with descriptions, durations, priorities, categories, dates, and optional HH:MM start times.
- Browse tasks chronologically and filter by pet or completion status.
- Generate a daily plan by **High → Medium → Low**, then by time within each priority.
- Select due/overdue tasks within one shared time budget and explain skipped tasks.
- Warn about matching start times across pets.
- Find the earliest gap long enough for an activity, checking full durations across all pets.
- Complete daily/weekly tasks and create the next occurrence for the same pet.
- Save pets, tasks, completion history, and owner preferences to local `data.json`.
- Read status icons and structured tables in the UI and a portable ASCII CLI table.

## Setup and run

Requires Python 3.10 or newer. In Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Skip environment creation if `.venv` already exists. On macOS/Linux/WSL use
`source .venv/bin/activate`. Run `python main.py` for the reproducible CLI demo.

## Architecture

| Class | Responsibility |
|-------|----------------|
| `Task` | Validates activity details and stores completion, due date, and optional time. |
| `Pet` | Holds tasks and supports addition/removal. |
| `Owner` | Holds pets, time budget, preferences, all-task access, and JSON persistence. |
| `Scheduler` | Retrieves owner tasks, sorts/filters, selects plans, finds free slots, warns about conflicts, and creates recurring successors. |

`app.py` keeps an owner in session state and calls the backend from forms.
See [final UML](diagrams/uml_final.mmd), [algorithm plan](diagrams/algorithm_plan.md),
[test plan](tests/TEST_PLAN.md), [AI interactions](ai_interactions.md), and
[reflection](reflection.md). Optional UML list parameters contain Task objects.

## Persistence workflow

On startup, the UI calls `Owner.load_from_json()` if `data.json` exists next to
`app.py`; otherwise it starts with an empty owner. Owner edits, pet additions,
task additions, and completion automatically call `Owner.save_to_json()`. **Save
data now** retries saving the current session. Restarting the app restores pets,
tasks, preferences, completion history, and recurring occurrences.

Custom conversion uses Python's standard `dataclasses.asdict`, `json`, and
`date.isoformat`/`date.fromisoformat`. The versioned JSON contains nested owner,
pet, and task dictionaries, which are reconstructed into validated dataclasses.
No marshmallow dependency is needed for these four simple classes. Saves write
an adjacent temporary file and replace the destination only after validation and
successful serialization. Invalid files cause a visible error and are not silently
replaced; fix or restore the file before continuing.

```python
from pawpal_system import Owner

owner.save_to_json("data.json")  # owner is your current Owner instance
restored = Owner.load_from_json("data.json")
```

Back up `data.json` to preserve your records. It is excluded from Git. The path
can be overridden with `PAWPAL_DATA_PATH` (also used for isolated tests). Local
JSON supports one owner/workspace, not concurrent multi-user writers; separate
sessions can overwrite each other's latest changes. There is no automatic reload
into an already-open session. The CLI demo uses a temporary file for its storage
check so it never overwrites the browser's data.

Persistence changed `pawpal_system.py`, `app.py`, `.gitignore`,
`tests/test_extensions.py`, and `tests/test_app.py`. Supporting changes also
updated `main.py`, both UML files, the test/algorithm plans, this README,
`reflection.md`, and `ai_interactions.md`.

## Smarter Scheduling

| Feature | Method | Behavior |
|---------|--------|----------|
| Time sorting | `Scheduler.sort_by_time()` | Stable HH:MM ordering; untimed tasks last; original list unchanged. |
| Priority scheduling | `Scheduler.sort_by_priority()` / `generate_plan()` | High, Medium, Low; then time; then category preferences and entry order. Both budget selection and plan display use this order. |
| Filtering | `Scheduler.filter_tasks()` | Optional case-insensitive pet name and completion status; combines every pet's tasks through Owner. |
| Free-slot search | `Scheduler.next_available_slot()` | Earliest duration-sized gap in a same-day window, across all pets; overlapping busy intervals are skipped. Returns HH:MM or None and never moves tasks. |
| Conflict warnings | `Scheduler.detect_conflicts()` | Pending tasks with identical dates/start times, including tasks across pets. |
| Recurrence | `Scheduler.mark_task_complete()` | One new daily/weekly occurrence on the same pet, preserving details; repeated completion creates no duplicate. |

The free-slot search is the extra algorithm beyond sorting, filtering, recurrence,
and exact-start warnings. It sorts busy intervals, scans once, and advances a
candidate past occupied time: O(n log n) overall. Completed/untimed tasks and other
dates do not reserve time. The window must start and end on the same day; overnight
windows are unsupported. Suggestions are independent of the daily minute budget.

Daily/weekly completion advances from `max(today, due_date)` by one/seven days.
Other frequency labels, including twice daily, remain descriptive. Use the
Scheduler method for recurring workflows; `Task.mark_complete()` only changes
status. Dates default to the server's local date, with optional fixed dates for
tests. Exact-start warnings do not detect duration overlaps or automatically
reschedule tasks; the slot finder checks durations when suggesting a gap.

## Formatting

The UI uses `st.table` for structured data, **✅ Complete / ⏳ Pending** labels,
`st.success` for successful actions and slot suggestions, `st.warning` for
conflicts/no-space results, and `st.error` for invalid data or storage failures.
Labels include text so color is not the only signal. The task browser stays
chronological; the generated plan explicitly says priority then time.

`main.format_schedule()` uses Python string padding (`str.ljust`) to align
PRIORITY, TIME, PET, ACTIVITY, MIN, and STATUS columns. Uppercase priorities and
TODO/DONE statuses work in terminals without color or emoji support. No tabulate
or other formatting dependency is required.

## Demo Walkthrough

1. Save the owner's name, available minutes, and preferred categories.
2. Add Mochi (dog) and Luna (cat), then add tasks to each with **Add task**.
3. Add a low-priority task at 07:00 and high-priority tasks at 08:00. Browse the chronological table and filter by pet/status.
4. Give two pending tasks the same due date and 08:00 start. The warning names pets and activities, including tasks hidden by filters. Arrange separate times before relying on the plan.
5. Enter a day, duration, and window under **Find a free slot**. The suggested gap accounts for full activity durations without changing existing tasks.
6. Click **Generate schedule**. High-priority care comes first, even when a low-priority activity has an earlier time. Read **Why this plan?** for selection and budget explanations.
7. Mark a daily/weekly task complete. The successor is attached to the same pet and waits until its due date to enter daily plans. Filter by Complete to inspect history.
8. Restart the app to restore the saved data.json. The final CLI line below independently verifies a temporary JSON round trip.

Actual output from `python main.py` (fixed demo date):

```text
Today's Schedule (demo date: 2026-10-22)
Owner: Jordan | Available time: 60 min
PRIORITY | TIME  | PET   | ACTIVITY     | MIN | STATUS
---------+-------+-------+--------------+-----+-------
HIGH     | 08:00 | Mochi | Morning walk | 20  | TODO
HIGH     | 08:00 | Luna  | Breakfast    | 5   | TODO
MEDIUM   | 12:00 | Luna  | Play session | 10  | TODO
LOW      | 07:00 | Mochi | Brush coat   | 15  | TODO
Total scheduled: 50 / 60 min

Pending tasks for Mochi (sorted by time):
- 07:00: Brush coat
- 08:00: Morning walk

Conflict warnings:
WARNING: Conflict on 2026-10-22 at 08:00: Mochi: Morning walk; Luna: Breakfast

Next free 15-minute slot (08:00-20:00): 08:20

Completed: Mochi's Morning walk
Next daily occurrence: 2026-10-23 at 08:00
Completed tasks: 1
Pending tasks: 4
JSON round-trip: restored 2 pets and 5 tasks
```

## Testing PawPal+

```bash
python -m pytest
```

Tests cover lifecycle, multi-pet access, sorting/filtering, priority budgets,
recurrence/calendar boundaries, conflict warnings, free-slot overlap/boundary
cases, JSON round trips/invalid files/failed saves, and Streamlit forms and
restoration in a new session. Tests use temporary data paths and do not touch
real data.json. Actual successful output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\lesli\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 51 items

test_pawpal_system.py ...........                                        [ 21%]
tests\test_algorithms.py ................                                [ 52%]
tests\test_app.py .....                                                  [ 62%]
tests\test_extensions.py ............                                    [ 86%]
tests\test_pawpal.py .......                                             [100%]

============================= 51 passed in 8.06s ==============================
```

**Confidence Level: 4/5 stars (★★★★☆)** for the documented behavior. Concurrent
storage, timezone appointments, overnight windows, automatic twice-daily
recurrence, and general duration-overlap warnings remain outside scope.
