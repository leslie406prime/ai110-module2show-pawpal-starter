"""Demonstrate sorting, filtering, recurrence, and conflict warnings."""

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from pawpal_system import Owner, Pet, Scheduler, Task


def format_schedule(owner: Owner, tasks: list[Task]) -> str:
    """Format an ASCII terminal table with readable priorities and task statuses."""
    pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
    rows = [["PRIORITY", "TIME", "PET", "ACTIVITY", "MIN", "STATUS"]]
    rows.extend([
        task.priority.upper(), task.time or "Anytime", pet_names[id(task)],
        task.description, str(task.duration_minutes), "DONE" if task.completed else "TODO"
    ] for task in tasks)
    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
    lines = [" | ".join(value.ljust(width) for value, width in zip(row, widths)) for row in rows]
    lines.insert(1, "-+-".join("-" * width for width in widths))
    return "\n".join(line.rstrip() for line in lines)


def main() -> None:
    """Print a reproducible multi-pet scheduling demonstration."""
    today = date(2026, 10, 22)
    owner = Owner("Jordan", available_minutes=60)
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    # Deliberately enter later tasks before earlier tasks.
    mochi.add_task(Task("Brush coat", "grooming", 15, "low", "weekly",
                        time="07:00", due_date=today))
    walk = Task("Morning walk", "exercise", 20, "high", time="08:00", due_date=today)
    mochi.add_task(walk)
    luna.add_task(Task("Play session", "enrichment", 10, time="12:00", due_date=today))
    luna.add_task(Task("Breakfast", "feeding", 5, "high", time="08:00", due_date=today))
    scheduler = Scheduler(owner)

    print("Today's Schedule (demo date: 2026-10-22)")
    print(f"Owner: {owner.name} | Available time: {owner.available_minutes} min")
    print(format_schedule(owner, scheduler.generate_plan(today=today)))
    print(f"Total scheduled: {scheduler.get_total_duration()} / {owner.available_minutes} min")

    print("\nPending tasks for Mochi (sorted by time):")
    for task in scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False)):
        print(f"- {task.time}: {task.description}")

    print("\nConflict warnings:")
    for warning in scheduler.detect_conflicts():
        print(f"WARNING: {warning}")
    print(f"\nNext free 15-minute slot (08:00-20:00): {scheduler.next_available_slot(15, today)}")

    next_task = scheduler.mark_task_complete(walk, today=today)
    print("\nCompleted: Mochi's Morning walk")
    print(f"Next daily occurrence: {next_task.due_date} at {next_task.time}")
    print(f"Completed tasks: {len(scheduler.filter_tasks(completed=True))}")
    print(f"Pending tasks: {len(scheduler.filter_tasks(completed=False))}")
    # Verify storage without overwriting the browser app's real data.json.
    with TemporaryDirectory() as directory:
        path = Path(directory) / "data.json"
        owner.save_to_json(path)
        restored = Owner.load_from_json(path)
        print(f"JSON round-trip: restored {len(restored.pets)} pets and {len(restored.get_all_tasks())} tasks")


if __name__ == "__main__":
    main()
