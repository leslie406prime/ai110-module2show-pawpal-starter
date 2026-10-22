"""Quick checks for task completion and pet task addition."""

from pawpal_system import Pet, Task


def test_task_completion():
    task = Task("Breakfast", "feeding", 5)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    pet = Pet("Mochi", "dog")
    task = Task("Morning walk", "exercise", 20)
    original_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == original_count + 1
    assert pet.tasks[-1] is task
