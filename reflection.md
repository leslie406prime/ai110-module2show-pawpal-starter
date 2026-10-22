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
inputs. Method bodies remain empty for the next implementation phase.

The review also identified issues to revisit: task ownership must remain clear
when displaying plans for multiple pets, and generate_plan must clear previous
results so repeated runs do not accumulate tasks. The current one-way Pet-to-task
relationship keeps the draft simple, but the UI may eventually need a pet lookup
or explicit task-to-pet reference. Priority sorting will take O(n log n) time for
n tasks, which is reasonable for a small household. A greedy selection may skip
a long task while admitting shorter ones; this tradeoff will need implementation
tests. These are design considerations, not verified scheduling behavior.

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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
