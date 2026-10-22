# PawPal+ test plan

Five core behaviors guide the tests:

| Behavior | Happy path | Important edge cases |
|----------|------------|----------------------|
| Task lifecycle and ownership | Add a task to a pet and complete it | Independent lists, identity-based removal, duplicate additions, foreign tasks |
| Sorting and filtering | Chronological HH:MM ordering and combined pet/status filters | Midnight, 23:59, equal times, untimed tasks, invalid times, unknown pet, empty pet |
| Recurrence | Daily and weekly completion create a new pending occurrence for the same pet | Preserve all task details, repeated completion, year/leap-day boundaries, early/late completion, one-off tasks |
| Conflict warnings | Duplicate date/start times produce warnings across pets | Three tasks in one group, same-pet conflicts, different dates, completed tasks, no tasks; duration overlaps remain outside scope |
| Daily plan and UI persistence | Budgeted multi-pet plan survives widget reruns | Zero time, exact budget, long tasks skipped, future occurrences excluded, repeated generation, invalid forms, UI completion |

`tests/test_pawpal.py` contains the core acceptance cases. More detailed algorithm
cases live in `tests/test_algorithms.py`; `test_pawpal_system.py` checks the core
backend and `tests/test_app.py` exercises Streamlit interactions.

Tests use fixed dates for recurrence calculations and literal expected times and
dates, rather than reproducing the implementation's sorting or date arithmetic.
`is` verifies object identity where equal-looking tasks could hide a wrong-pet
assignment. Explicit assertions check both the completed record and its successor.
No network service is required for these tests.

Stretch tests in `tests/test_extensions.py` cover priority-then-time ordering,
the earliest duration-sized gap across pets (overlaps, exact boundaries, no room,
completed/untimed tasks), JSON round trips with recurring history, missing/corrupt
files, schema validation, and failed atomic saves. UI tests isolate their data
files in temporary directories and verify a fresh session restores saved pets.

Run all checks from the repository root with the virtual environment active:

```bash
python -m pytest
```

Confidence target: 4/5 for the documented rules, not a claim that all possible
inputs or production workflows are covered. Duration overlaps, timezone-aware
appointments and automatic twice-daily recurrence remain outside the implemented
behavior. JSON persistence is local and single-user; concurrent writer coordination
is not covered or supported.
