# AI Interactions Log

## Agent Workflow (SF7)

**Assistant/tool:** Codex automatic editing, terminal commands, pytest, and two
named model review agents for the prompt comparison below.

**Request:** Extend PawPal+ with an algorithm beyond the basic requirements,
JSON persistence, priority-then-time scheduling, user-friendly formatting, and a
real two-model comparison. Keep the final UI/UML/manual consistent.

**What the agent completed:**

- Added Scheduler.next_available_slot(), scanning sorted occupied intervals across all pets and accounting for durations/overlaps.
- Added Owner.save_to_json()/load_from_json() with versioned dictionaries, ISO dates, validation, and temporary-file replacement.
- Connected UI startup restoration and automatic saves after mutations, with visible file errors. Kept tests isolated from real data.json.
- Added sort_by_priority() and changed plan selection/display to priority first, then time; chronological browsing remains available separately.
- Added status icons, a free-slot form, and main.format_schedule() for aligned CLI tables without extra dependencies.
- Ran the CLI demo and the complete test suite: 51 passed. Copied actual output into README.
- Obtained independent responses from gpt-6.1-sol and gpt-6-sol using the same weekly-recurrence prompt.

**Files modified:** pawpal_system.py, app.py, main.py, .gitignore, README.md,
ai_interactions.md, reflection.md, diagrams/uml.mmd, diagrams/uml_final.mmd,
diagrams/design.md, diagrams/algorithm_plan.md, tests/TEST_PLAN.md,
tests/test_algorithms.py, tests/test_app.py, and new tests/test_extensions.py.

**Review and corrections:** No manual user corrections have been reported for
this extension. During agent review, the previous chronological-plan assertion
was changed to match the newly requested priority-first policy. UI tests were
updated to use temporary JSON paths so they cannot overwrite personal records.
Completion now keeps a save error visible instead of immediately rerunning and
hiding it. An atomic replacement failure test verifies the prior file survives.
The agent kept custom serialization rather than adding marshmallow, because the
schema has four simple dataclasses and only dates require special conversion.

## Prompt Comparison (SF11)

Two different models were actually invoked as independent review agents. They
received the same prompt without the conversation history or repository tools.
The responses were design recommendations, not executable patches.

**Identical prompt/task:**

> Design weekly recurring pet-task completion. A Task has due_date (date),
> completed, frequency, time, description, category, duration_minutes, priority.
> Owner owns multiple Pets each with tasks. Completing via Scheduler must append
> a fresh incomplete task to the same pet exactly once. Specify early/late
> completion date policy, preserve details, reject foreign tasks, avoid duplicate
> successors. Explain tradeoffs and 3 tests. No files/tools needed.

| Aspect | Option A | Option B |
|--------|----------|----------|
| Model/tool used | gpt-6.1-sol via Codex review agent compare_weekly_a | gpt-6-sol via Codex review agent compare_weekly_b |
| Response | Gave pseudocode using a DB transaction, owned-pet lookup, row lock, stable task ID, and unique successor_of link. Computes weeks as max(1, elapsed_days // 7 + 1). | Recommended transactional completion keyed by task ID/current owner, an atomic completion update, and a unique predecessor_task_id. Described the first due_date + 7*k strictly after completion. |
| Date policy | Preserve original weekday; early completion advances from original due date, late completion skips missed weeks. | Same original-cadence policy; skip missed weekly occurrences rather than making a backlog. |
| Useful output | Concrete date arithmetic, copied-field pseudocode, ownership-before-status check, explanation of cadence versus completion spacing. | Emphasized concurrency, retry safety, and the fact that an in-memory append cannot guarantee exactly once for concurrent callers. |
| Flaws/limitations for PawPal+ | Assumes database APIs and ID fields absent from the four-class JSON app; pseudocode is not directly runnable. | Mostly a database design rather than a lightweight implementation; also needs IDs, locks, and unique constraints absent here. |
| Suggested tests | Early completion, late completion with copied fields, foreign ownership and repeated/concurrent completion. | Early/on-time/late dates, foreign task rejection without changes, retry/concurrent exactly-one successor. |
| Final decision | Adopt the ownership/idempotency review criteria; do not add the database design or change date semantics in this extension. | Document the concurrency limitation and use atomic file replacement for JSON, without claiming transaction-level guarantees. |

**Decision and rationale:** Both responses favor original-weekday cadence. The
existing tested app deliberately uses max(today, due_date) + 7 days for weekly
completion, preserving spacing after a late completion while allowing the weekday
to shift. Retain that documented policy rather than silently changing user-visible
behavior. Tests verify copied fields, same-pet assignment, foreign-task rejection,
early/late dates, calendar boundaries, and sequential duplicate prevention.
Atomic JSON replacement prevents partial destination writes; it is not a database
transaction and does not prevent competing sessions from overwriting each other.
Neither model's database pseudocode was represented as production-ready code.
