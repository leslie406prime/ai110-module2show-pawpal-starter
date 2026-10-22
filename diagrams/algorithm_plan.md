# Scheduling algorithm plan

The original demo manually created four tasks, printed them in priority order,
and required the owner to recreate recurring activities. It did not represent
start times or due dates, expose filters, or warn about simultaneous activities.

Small improvements:

1. Validate optional start times as zero-padded 24-hour HH:MM strings, then use
   `sorted(tasks, key=lambda task: task.time or "24:00")`. This keeps the key
   readable and puts untimed activities last without modifying the input list.
2. Filter through `Owner.get_all_tasks()` by pet name and completion status.
3. Add due dates and an owner-aware completion method. Preserve the completed
   task and append a fresh daily/weekly instance to the same pet. Repeated
   completion must not duplicate the next occurrence. Late completions advance
   from today; early completions advance from the future due date.
4. Group pending tasks by (due date, start time) and return one warning per
   group. Include tasks across pets because one owner performs the care.
5. Keep priority-based budget selection, then display chosen tasks in time
   order. Exclude future occurrences until their due date.

Readability review: a grouped dictionary is easier to follow than a nested
pairwise comprehension and takes O(n) grouping time. Sorting warning groups
gives deterministic output. Exact start matches are deliberately simpler than
interval overlap detection; warnings do not resolve conflicts automatically.
