"""Pet care objects and a daily, time-budgeted planner."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
import re


@dataclass
class Task:
    """One dated activity with an optional 24-hour HH:MM start time."""

    description: str
    category: str
    duration_minutes: int
    priority: str = "medium"
    frequency: str = "daily"
    completed: bool = False
    time: str | None = None
    due_date: date = field(default_factory=date.today)

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
        if self.time is not None and (
            not isinstance(self.time, str)
            or re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", self.time) is None
        ):
            raise ValueError("Time must use 24-hour HH:MM format, such as 09:30.")
        if type(self.due_date) is not date:
            raise ValueError("Due date must be a date.")

    def update_details(
        self, description: str, category: str, duration_minutes: int, priority: str
    ) -> None:
        """Validate and update this task's editable details."""
        # Validate a candidate first so a failed edit leaves this task unchanged.
        candidate = replace(self, description=description, category=category,
                            duration_minutes=duration_minutes, priority=priority)
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

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Filter all owner tasks by case-insensitive pet name and/or status."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            matching_ids = {
                id(task) for pet in self.owner.pets
                if pet.name.casefold() == pet_name.strip().casefold()
                for task in pet.tasks
            }
            tasks = [task for task in tasks if id(task) in matching_ids]
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        return tasks

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks ordered by HH:MM, with untimed tasks last and stable ties."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda task: task.time or "24:00")

    def mark_task_complete(self, task: Task, today: date | None = None) -> Task | None:
        """Complete an owned task once and append its next daily/weekly occurrence."""
        pet = next((pet for pet in self.owner.pets
                    if any(existing is task for existing in pet.tasks)), None)
        if pet is None:
            raise ValueError("Task does not belong to this owner.")
        if task.completed:
            return None
        intervals = {"daily": 1, "weekly": 7}
        next_task = None
        if task.frequency in intervals:
            base_date = max(today or date.today(), task.due_date)
            next_task = replace(
                task, completed=False,
                due_date=base_date + timedelta(days=intervals[task.frequency]),
            )
        task.mark_complete()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Warn about pending tasks with identical dates and start times across pets."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        pet_names = {id(task): pet.name for pet in self.owner.pets for task in pet.tasks}
        groups: dict[tuple[date, str], list[Task]] = {}
        for task in tasks:
            if not task.completed and task.time is not None:
                groups.setdefault((task.due_date, task.time), []).append(task)
        warnings = []
        for (due_date, start), group in sorted(groups.items()):
            if len(group) > 1:
                labels = "; ".join(
                    f"{pet_names.get(id(task), 'Unknown pet')}: {task.description}"
                    for task in group
                )
                warnings.append(f"Conflict on {due_date} at {start}: {labels}")
        return warnings

    def generate_plan(self, today: date | None = None) -> list[Task]:
        """Rebuild the plan using pending tasks, priority, preferences, and time."""
        _validate_minutes(self.owner.available_minutes)
        today = today or date.today()
        tasks = self.owner.get_all_tasks()
        for task in tasks:
            task.__post_init__()
        pending = [task for task in tasks if not task.completed and task.due_date <= today]
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
            "Tasks selected by priority, then preferred category, then entry order; "
            "displayed by start time."
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
        self.selected_tasks[:] = self.sort_by_time(self.selected_tasks)
        reasons.extend(self.detect_conflicts(self.selected_tasks))
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
