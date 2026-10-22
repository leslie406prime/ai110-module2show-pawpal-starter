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

The final architecture is recorded in diagrams/uml_final.mmd. It adds optional
time/date arguments and return types, scheduler algorithms, private explanation
state, and the dependency on Pet for appending recurring tasks.

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
shared time budget. It chooses high priority before medium and low, then start
time within each priority, then preferred categories and entry order for remaining
ties. Untimed tasks follow timed tasks within a priority. The chronological
browser remains available separately from the priority-ordered daily plan.

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

The most useful assistant capabilities were coordinated edits across Python,
Mermaid, and Markdown, reviewing method responsibilities, and running terminal
tests after changes. Streamlit AppTest helped verify real form interactions and
state persistence instead of relying only on backend tests.

Separate chat sessions were suggested in the assignment, but this project used
one continuing conversation. Algorithm and testing work were organized in
diagrams/algorithm_plan.md and tests/TEST_PLAN.md instead. These written plans
kept each phase focused while preserving shared design decisions. Separate chats
could reduce context clutter in a future project, but would need the current
files and constraints attached so earlier decisions are not lost.

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

Confidence level: 4/5 stars for the documented daily planning rules. All 51 tests
passed, including explicit acceptance checks for midnight sorting, correct-pet
daily recurrence, three simultaneous tasks, and a pet with no tasks. Expected
dates and times are written explicitly so tests do not simply repeat the algorithm.
Duration-overlap detection, timezone-aware appointments, and automatic handling
of twice-daily frequencies would need additional design and tests. Passing the
current suite does not imply these unimplemented features are supported.

---

## 5. Reflection

**a. What went well**

The final system keeps data ownership and planning responsibilities clear:
Owner aggregates tasks, Pet holds them, and Scheduler handles algorithms. The
same backend drives the CLI and browser UI. A readable demo, final UML, and tests
make that design easier to inspect and explain. UI filters and actionable warnings
now expose the algorithms directly to the pet owner.

**b. What you would improve**

The next iteration would add editing/rescheduling controls and duration-overlap
warnings. JSON storage now persists records locally. Right now warnings require the owner to arrange
separate times outside the app. I would also define timezone and twice-daily
recurrence rules explicitly before expanding date logic, and add tests for those
rules rather than guessing how they should behave.

**c. Key takeaway**

Acting as lead architect means setting the scope, choosing class responsibilities,
and checking that generated code matches the intended behavior. AI can produce
code and tests quickly, but passing tests alone does not justify claiming features
that are not implemented. Clear acceptance criteria, literal expected results,
and honest limitations keep the design understandable. Modifying the initial
CareTask design to match Task and keeping recurrence in the owner-aware Scheduler
illustrate why architectural judgment matters alongside automatic editing.

## Stretch extension review

The added free-slot algorithm sorts occupied intervals and finds a gap long
enough for a new activity across all pets. Unlike exact-start conflict warnings,
this suggestion accounts for durations and overlapping busy intervals. It does
not move tasks or decide that a suggestion fits the daily minute budget.

The advanced priority requirement changes the earlier plan policy: selection and
display now order by priority, then time; preferences break remaining ties. This
means a later high-priority task can appear before an earlier low-priority task.
The task browser retains chronological sorting for a different useful view.

Custom JSON conversion was sufficient without marshmallow. Tests cover restored
dates and completion history, schema errors, missing files, and save failure
preserving the previous file. Local JSON is a single-user convenience rather
than a concurrent database. Save errors are visible and corrupt files are not
silently overwritten.

Two independent model reviews (gpt-6.1-sol and gpt-6-sol) recommended weekly
cadence preservation and database transactions/unique successor IDs. Their
concurrency warnings were useful, but adding database infrastructure would exceed
this local app's scope. The tested max(today, due_date) + interval policy was
retained and its weekday-shifting tradeoff documented. The exact prompt, useful
findings, limitations, and decision are recorded in ai_interactions.md.
