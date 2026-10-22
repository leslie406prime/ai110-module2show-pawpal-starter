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
The CLI demo now labels tasks with their pet names. Automatic recurrence remains
future work.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
Automatic recurrence was deferred rather than adding unrequested date-handling
complexity; the documentation states this limitation.

Verification used the actual main.py output, which showed tasks for both pets
and a grooming task skipped when it could not fit the time budget. Automated
tests check completion, task addition, multi-pet retrieval through the Owner
method, priority and preference ordering, time limits, and repeated scheduling.
The README sample was copied from the successful demo run rather than invented.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
