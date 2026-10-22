# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial design has four classes. Owner stores the owner's name, daily time
budget, category preferences, and pets. Pet stores basic pet information and its
care tasks. CareTask stores an activity's title, category, duration, priority,
and completion status. Scheduler uses the owner's pets and pending tasks to
build an ordered daily plan and explain selected and skipped tasks.

The relationships are Owner has Pets, Pet has CareTasks, and Scheduler plans
for an Owner. The Mermaid source is saved in diagrams/uml.mmd, and the matching
Python dataclass skeletons are in pawpal_system.py.

**b. Design changes**

At the skeleton stage, the four classes and their relationships remain the same.
The AI review identified shared mutable lists as a Python implementation risk,
so each list uses dataclasses.field(default_factory=list). Scheduler's result
lists also use init=False because they are generated output, not constructor
inputs. Method bodies were left empty at that stage for the next implementation phase.

The review also identified issues to revisit: task ownership must remain clear
when displaying plans for multiple pets, and generate_plan must clear previous
results so repeated runs do not accumulate tasks. The current one-way Pet-to-task
relationship keeps the draft simple, but the UI may eventually need a pet lookup
or explicit task-to-pet reference. Priority sorting will take O(n log n) time for
n tasks, which is reasonable for a small household. A greedy selection may skip
a long task while admitting shorter ones; this tradeoff will need implementation
tests.

During the core implementation, CareTask was renamed to Task to match the
assignment. Its title became description, and frequency was added as descriptive
text. Owner gained get_all_tasks(), which combines all pets' tasks. Scheduler
calls this method rather than reading one pet directly, keeping task retrieval
separate from planning. The implementation now resets plan results on each run,
filters completed tasks, and uses the owner's shared time budget. Tests cover
multi-pet retrieval, priority and preference ordering, skipped tasks, completion,
repeated runs, empty plans, input validation, and independent mutable lists.
The CLI demo now labels tasks with their pet names. In the algorithm phase, Task
gained a due date and optional HH:MM start time. Scheduler gained sorting,
filtering, exact-start conflict warnings, and an owner-aware completion method
that creates the next daily or weekly occurrence for the same pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler selects incomplete tasks due today or earlier within the owner's
shared time budget. It chooses high priority before medium and low, uses preferred
categories to break priority ties, and preserves entry order for remaining ties.
Chosen tasks are displayed in start-time order, with untimed tasks last. This
keeps urgent care central while making the resulting plan easy to read.

**b. Tradeoffs**

Conflict detection checks identical due dates and start times across all pets,
rather than overlapping durations. This is easy to explain and groups tasks in
O(n) time, but it misses a 30-minute walk at 08:00 overlapping feeding at 08:15.
It returns warnings without rejecting tasks or automatically rescheduling them,
so the owner decides how to resolve the conflict. The priority-based greedy
selection also does not guarantee an optimal use of every available minute.

The algorithm review considered a compact pairwise comprehension for conflicts.
The implementation keeps an explicit grouping loop because it is easier to read
and avoids comparing every task against every other task. For time sorting, a
short lambda is clear: validated zero-padded HH:MM strings sort chronologically,
and a 24:00 sentinel places untimed tasks last.

---

## 3. AI Collaboration

**a. How you used AI**

AI helped brainstorm the four classes, generate Mermaid UML, translate the design
into dataclass skeletons, and implement the backend. It suggested separate list
defaults for each object, an Owner.get_all_tasks() method for multi-pet access,
and a scheduler that filters completed tasks and rebuilds its results each run.
These suggestions were incorporated into the implementation. Requests with
concrete requirements, such as retrieving every pet's tasks and formatting a
two-pet terminal demo, gave clear targets for reviewing the generated code.

**b. Judgment and verification**

The initial AI design used CareTask and omitted frequency. That design was
revised to Task with a description and frequency field to match the assignment.
The suggestion to defer explicit pet labels was also revisited: the CLI now maps
each scheduled task back to its pet so the output is understandable across pets.
Automatic recurrence was initially deferred, then implemented when requested.
Daily and weekly tasks advance by one or seven days; other frequency labels
remain descriptive. Recurrence is handled through Scheduler.mark_task_complete()
so the next instance can be attached to the correct pet. Task.mark_complete()
remains the low-level status change for callers that do not need recurrence.

Verification used the actual main.py output, which showed tasks for both pets
and a grooming task skipped when it could not fit the time budget. Automated
tests check completion, task addition, multi-pet retrieval through the Owner
method, priority and preference ordering, time limits, and repeated scheduling.
The README sample was copied from the successful demo run rather than invented.

---

## 4. Testing and Verification

**a. What you tested**

Tests cover task completion and addition, all-pet access, ordering, combined
pet/status filters, budget limits, repeated runs, invalid times, conflict warnings,
and Streamlit session persistence. Recurrence tests check daily/weekly intervals,
year and leap-day boundaries, early and late completions, correct pet assignment,
and duplicate prevention. These checks protect the relationships and date logic
that would be difficult to verify from one printed schedule alone.

**b. Confidence**

Confidence level: 4/5 stars for the documented daily planning rules. All 37 tests
passed, including explicit acceptance checks for midnight sorting, correct-pet
daily recurrence, three simultaneous tasks, and a pet with no tasks. Expected
dates and times are written explicitly so tests do not simply repeat the algorithm.
Duration-overlap detection, timezone-aware appointments, and automatic handling
of twice-daily frequencies would need additional design and tests. Passing the
current suite does not imply these unimplemented features are supported.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
