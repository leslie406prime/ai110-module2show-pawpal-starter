# PawPal+ building blocks

This draft uses four classes inferred from the starter app requirements.

| Object | Attributes (information it holds) | Methods (actions it performs) |
|--------|----------------------------------|--------------------------------|
| Owner | Name, available minutes per day, preferred task categories, pets | Add a pet, change available time, change preferences |
| Pet | Name, species, care tasks | Add a task, remove a task, get incomplete tasks |
| CareTask | Title, category (feeding, walking, grooming, etc.), duration in minutes, priority, completion status | Edit task details, mark a task complete |
| Scheduler | Owner, selected tasks in order, skipped tasks | Generate a plan, calculate its total duration, explain selected and skipped tasks |

## Draft scheduling rules

- Plan for one day using the owner's available minutes across all their pets.
- Consider incomplete tasks only. Each task belongs to one pet.
- Select high-priority tasks first, then medium, then low. Within the same priority, prefer the owner's preferred categories; preserve entry order for remaining ties.
- Add a task if its entire duration fits in the remaining time. Otherwise, record it as skipped and continue considering other tasks.
- Require positive task durations and nonnegative available time. Priority must be `low`, `medium`, or `high`.
- Return an ordered task list and explain choices using priority, preferences, and remaining time. Exact clock times and recurring tasks are future extensions.
- If tasks are edited or completed, generate the plan again to reflect those changes.

## Mermaid UML

The class diagram is in [uml.mmd](uml.mmd). This is a design draft; the Python classes are not implemented yet.
