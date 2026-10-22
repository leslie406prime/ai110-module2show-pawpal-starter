"""Run a small multi-pet planning demo with: python main.py."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan", available_minutes=40)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "exercise", 20, "high"))
    mochi.add_task(Task("Brush coat", "grooming", 15, "low"))
    luna.add_task(Task("Breakfast", "feeding", 5, "high"))
    luna.add_task(Task("Play session", "enrichment", 10, "medium"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    # Keep the pet label attached to the exact task, even for identical activities.
    pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}

    print("Today's Schedule")
    print(f"Owner: {owner.name} | Available time: {owner.available_minutes} min")
    print(f"Pets: {mochi.name} ({mochi.species}), {luna.name} ({luna.species})")
    print()
    for number, task in enumerate(plan, start=1):
        print(
            f"{number}. {pet_names[id(task)]}: {task.description} "
            f"| {task.duration_minutes} min | {task.priority} priority"
        )
    if not plan:
        print("No tasks scheduled.")

    total = scheduler.get_total_duration()
    print(f"\nTotal scheduled: {total} / {owner.available_minutes} min")
    print(f"Time remaining: {owner.available_minutes - total} min")
    if scheduler.skipped_tasks:
        print("\nSkipped (not enough time):")
        for task in scheduler.skipped_tasks:
            print(
                f"- {pet_names[id(task)]}: {task.description} "
                f"| {task.duration_minutes} min | {task.priority} priority"
            )


if __name__ == "__main__":
    main()
