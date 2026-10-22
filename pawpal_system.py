"""Pet care objects and a daily, time-budgeted planner."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """One activity. Frequency is descriptive; recurrence is not automated."""

    description: str
    category: str
    duration_minutes: int
    priority: str = "medium"
    frequency: str = "daily"
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate the task's details when it is created."""
        if not self.description.strip() or not self.category.strip():
            raise ValueError("Description and category must not be blank.")
        _validate_minutes(self.duration_minutes, minimum=1)
        if self.priority not in {"low", "medium", "high"}:
            raise ValueError("Priority must be low, medium, or high.")
        if not self.frequency.strip():
            raise ValueError("Frequency must not be blank.")
        if not isinstance(self.completed, bool):
            raise ValueError("Completion status must be a boolean.")

    def update_details(
        self, description: str, category: str, duration_minutes: int, priority: str
    ) -> None:
        """Validate and update this task's editable details."""
        # Validate a candidate first so a failed edit leaves this task unchanged.
        candidate = Task(description, category, duration_minutes, priority,
                         self.frequency, self.completed)
        self.description = candidate.description
        self.category = candidate.category
        self.duration_minutes = candidate.duration_minutes
        self.priority = candidate.priority

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task belonging to this pet."""
        if any(existing is task for existing in self.tasks):
            raise ValueError("This task is already assigned to this pet.")
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        for index, existing in enumerate(self.tasks):
            if existing is task:
                del self.tasks[index]
                return
        raise ValueError("This task does not belong to this pet.")

    def get_pending_tasks(self) -> list[Task]:
        """Return this pet's incomplete tasks."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """An owner's pets, daily time budget, and preferred task categories."""

    name: str
    available_minutes: int
    preferred_categories: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the owner's initial daily time budget."""
        _validate_minutes(self.available_minutes)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care."""
        if any(existing is pet for existing in self.pets):
            raise ValueError("This pet is already assigned to this owner.")
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return all pets' tasks in pet/task entry order, including completed tasks."""
        return [task for pet in self.pets for task in pet.tasks]

    def set_available_time(self, minutes: int) -> None:
        """Validate and set the daily time budget."""
        _validate_minutes(minutes)
        self.available_minutes = minutes

    def set_preferences(self, categories: list[str]) -> None:
        """Set preferred care categories."""
        self.preferred_categories = list(categories)


@dataclass
class Scheduler:
    """Build and explain one day's ordered plan for an owner's pets."""

    owner: Owner
    selected_tasks: list[Task] = field(default_factory=list, init=False)
    skipped_tasks: list[Task] = field(default_factory=list, init=False)
    _explanation: str = field(default="Generate a plan first.", init=False, repr=False)

    def generate_plan(self) -> list[Task]:
        """Rebuild the plan using pending tasks, priority, preferences, and time."""
        _validate_minutes(self.owner.available_minutes)
        tasks = self.owner.get_all_tasks()
        for task in tasks:
            task.__post_init__()
        pending = [task for task in tasks if not task.completed]
        priority_order = {"high": 0, "medium": 1, "low": 2}
        preferences = set(self.owner.preferred_categories)
        pending.sort(key=lambda task: (
            priority_order[task.priority], task.category not in preferences
        ))
        self.selected_tasks.clear()
        self.skipped_tasks.clear()
        remaining = self.owner.available_minutes
        reasons = [
            f"Daily time budget: {remaining} minutes. "
            "Tasks ordered by priority, then preferred category, then entry order."
        ]
        for task in pending:
            if task.duration_minutes <= remaining:
                self.selected_tasks.append(task)
                remaining -= task.duration_minutes
                preferred = ", preferred category" if task.category in preferences else ""
                reasons.append(
                    f"Selected {task.description}: {task.priority} priority{preferred}, "
                    f"{task.duration_minutes} minutes; {remaining} minutes remain."
                )
            else:
                self.skipped_tasks.append(task)
                reasons.append(
                    f"Skipped {task.description}: needs {task.duration_minutes} minutes, "
                    f"but only {remaining} remain."
                )
        if not pending:
            reasons.append("No pending tasks.")
        self._explanation = "\n".join(reasons)
        return list(self.selected_tasks)

    def get_total_duration(self) -> int:
        """Return the total minutes of selected tasks."""
        return sum(task.duration_minutes for task in self.selected_tasks)

    def explain_plan(self) -> str:
        """Explain why tasks were selected or skipped."""
        return self._explanation


def _validate_minutes(minutes: int, minimum: int = 0) -> None:
    """Reject fractional, boolean, and out-of-range minute values."""
    if type(minutes) is not int or minutes < minimum:
        raise ValueError(f"Minutes must be an integer of at least {minimum}.")
