"""PawPal+ backend blueprint. Method bodies will be implemented in a later phase."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CareTask:
    """One pet's care activity; priority will be low, medium, or high."""

    title: str
    category: str
    duration_minutes: int
    priority: str
    completed: bool = False

    def update_details(
        self, title: str, category: str, duration_minutes: int, priority: str
    ) -> None:
        """Validate and update this task's editable details."""
        pass

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a task belonging to this pet."""
        pass

    def remove_task(self, task: CareTask) -> None:
        """Remove a task from this pet."""
        pass

    def get_pending_tasks(self) -> list[CareTask]:
        """Return this pet's incomplete tasks."""
        pass


@dataclass
class Owner:
    """An owner's pets, daily time budget, and preferred task categories."""

    name: str
    available_minutes: int
    preferred_categories: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Validate and set the daily time budget."""
        pass

    def set_preferences(self, categories: list[str]) -> None:
        """Set preferred care categories."""
        pass


@dataclass
class Scheduler:
    """Build and explain one day's ordered plan for an owner's pets."""

    owner: Owner
    selected_tasks: list[CareTask] = field(default_factory=list, init=False)
    skipped_tasks: list[CareTask] = field(default_factory=list, init=False)

    def generate_plan(self) -> list[CareTask]:
        """Rebuild the plan using pending tasks, priority, preferences, and time."""
        pass

    def get_total_duration(self) -> int:
        """Return the total minutes of selected tasks."""
        pass

    def explain_plan(self) -> str:
        """Explain why tasks were selected or skipped."""
        pass
