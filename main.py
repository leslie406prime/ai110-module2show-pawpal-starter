"""Demonstrate sorting, filtering, recurrence, and conflict warnings."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Print a reproducible multi-pet scheduling demonstration."""
    today = date(2026, 10, 22)
    owner = Owner("Jordan", available_minutes=60)
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    # Deliberately enter later tasks before earlier tasks.
    mochi.add_task(Task("Brush coat", "grooming", 15, "low", "weekly",
                        time="18:00", due_date=today))
    walk = Task("Morning walk", "exercise", 20, "high", time="08:00", due_date=today)
    mochi.add_task(walk)
    luna.add_task(Task("Play session", "enrichment", 10, time="12:00", due_date=today))
    luna.add_task(Task("Breakfast", "feeding", 5, "high", time="08:00", due_date=today))
    scheduler = Scheduler(owner)
    pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}

    print("Today's Schedule (demo date: 2026-10-22)")
    print(f"Owner: {owner.name} | Available time: {owner.available_minutes} min")
    for task in scheduler.sort_by_time(scheduler.generate_plan(today=today)):
        print(f"{task.time} | {pet_names[id(task)]}: {task.description} "
              f"| {task.duration_minutes} min | {task.priority} priority")
    print(f"Total scheduled: {scheduler.get_total_duration()} / {owner.available_minutes} min")

    print("\nPending tasks for Mochi (sorted by time):")
    for task in scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False)):
        print(f"- {task.time}: {task.description}")

    print("\nConflict warnings:")
    for warning in scheduler.detect_conflicts():
        print(f"WARNING: {warning}")

    next_task = scheduler.mark_task_complete(walk, today=today)
    print("\nCompleted: Mochi's Morning walk")
    print(f"Next daily occurrence: {next_task.due_date} at {next_task.time}")
    print(f"Completed tasks: {len(scheduler.filter_tasks(completed=True))}")
    print(f"Pending tasks: {len(scheduler.filter_tasks(completed=False))}")


if __name__ == "__main__":
    main()
