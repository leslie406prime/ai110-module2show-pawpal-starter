# PawPal+ building blocks

This draft uses four classes inferred from the starter app requirements.

| Object | Attributes (information it holds) | Methods (actions it performs) |
|--------|----------------------------------|--------------------------------|
| Owner | Name, available minutes per day, preferred task categories, pets | Add a pet, change available time, change preferences, get all pets' tasks |
| Pet | Name, species, care tasks | Add a task, remove a task, get incomplete tasks |
| Task | Description, frequency, category, duration in minutes, priority, completion status, due date, optional start time | Edit task details, mark a task complete |
| Scheduler | Owner, selected tasks in order, skipped tasks | Generate a plan, sort by time, filter by pet/status, complete recurring tasks, warn about conflicts, total duration, explain choices |

## Draft scheduling rules

- Plan for one day using the owner's available minutes across all their pets.
- Consider incomplete tasks due today or earlier only. Each task belongs to one pet.
- Select high-priority tasks first, then medium, then low. Within the same priority, sort by start time, then preferred category, then entry order. Untimed tasks follow timed tasks.
- Add a task if its entire duration fits in the remaining time. Otherwise, record it as skipped and continue considering other tasks.
- Require positive task durations and nonnegative available time. Priority must be `low`, `medium`, or `high`.
- Return an ordered task list and explain choices using priority, preferences, and remaining time. Tasks have optional HH:MM start times and due dates. Scheduler.sort_by_time() orders chosen tasks; detect_conflicts() warns about identical date/start times. Scheduler.mark_task_complete() creates the next daily/weekly occurrence for the same pet.
- If tasks are edited or completed, generate the plan again to reflect those changes.

## Mermaid UML

The class diagram is in [uml.mmd](uml.mmd). The matching classes are implemented in `pawpal_system.py`. Scheduler retrieves tasks through `Owner.get_all_tasks()`, then filters completed tasks and applies the shared time budget.

## Stretch extensions

Owner saves and restores its object graph with versioned JSON, ISO dates, and
atomic file replacement. Scheduler.next_available_slot() scans occupied intervals
across all pets to suggest the earliest duration-sized gap without moving tasks.
The final architecture is also recorded in [uml_final.mmd](uml_final.mmd).
