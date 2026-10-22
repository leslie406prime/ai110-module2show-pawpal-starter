"""Advanced scheduling and JSON persistence behavior."""

from datetime import date
import json

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


DAY = date(2026, 10, 22)


def make_owner():
    return Owner("Jordan", 60, ["feeding"], [Pet("Mochi", "dog", [
        Task("Walk", "exercise", 30, "high", time="08:00", due_date=DAY)
    ]), Pet("Luna", "cat", [
        Task("Feed", "feeding", 15, "medium", time="08:15", due_date=DAY)
    ])])


def test_next_slot_merges_overlaps_across_pets_without_mutation():
    owner = make_owner()
    assert Scheduler(owner).next_available_slot(15, DAY, "08:00", "09:00") == "08:30"
    assert owner.pets[0].tasks[0].time == "08:00"


def test_slot_boundaries_and_fully_occupied_window():
    scheduler = Scheduler(make_owner())
    assert scheduler.next_available_slot(30, DAY, "08:00", "09:00") == "08:30"
    assert scheduler.next_available_slot(31, DAY, "08:00", "09:00") is None
    assert scheduler.next_available_slot(15, DAY, "08:10", "08:30") is None
    assert scheduler.next_available_slot(10, DAY, "07:00", "08:00") == "07:00"


def test_slot_ignores_completed_future_and_untimed_tasks():
    owner = make_owner()
    owner.pets[0].tasks[0].mark_complete()
    owner.pets[1].tasks[0].due_date = date(2026, 10, 23)
    owner.pets[0].add_task(Task("Anytime", "grooming", 60, due_date=DAY))
    assert Scheduler(owner).next_available_slot(60, DAY, "08:00", "09:00") == "08:00"


@pytest.mark.parametrize("minutes,start,end", [(0, "08:00", "09:00"),
    (15, "8:00", "09:00"), (15, "09:00", "08:00"), (15, "08:00", "08:00")])
def test_slot_invalid_inputs(minutes, start, end):
    with pytest.raises(ValueError):
        Scheduler(make_owner()).next_available_slot(minutes, DAY, start, end)


def test_priority_then_time_overrides_early_low_priority():
    early_low = Task("Groom", "grooming", 5, "low", time="07:00", due_date=DAY)
    later_high = Task("Medicine", "health", 5, "high", time="18:00", due_date=DAY)
    earlier_high = Task("Walk", "exercise", 5, "high", time="09:00", due_date=DAY)
    owner = Owner("Jordan", 10, pets=[Pet("Mochi", "dog", [early_low, later_high, earlier_high])])
    scheduler = Scheduler(owner)
    assert scheduler.sort_by_priority() == [earlier_high, later_high, early_low]
    assert scheduler.generate_plan(DAY) == [earlier_high, later_high]
    assert scheduler.skipped_tasks == [early_low]


def test_json_roundtrip_dates_status_preferences_and_recurring_history(tmp_path):
    owner = make_owner()
    Scheduler(owner).mark_task_complete(owner.pets[0].tasks[0], today=DAY)
    path = tmp_path / "data.json"
    owner.save_to_json(path)
    restored = Owner.load_from_json(path)
    assert restored == owner
    assert restored is not owner
    assert type(restored.pets[0].tasks[0].due_date) is date
    assert restored.pets[0].tasks[0].completed
    assert restored.pets[0].tasks[1].due_date == date(2026, 10, 23)
    assert restored.pets[1].tasks[0].description == "Feed"
    assert not list(tmp_path.glob("*.tmp"))


def test_json_missing_corrupt_and_wrong_schema_are_not_silently_reset(tmp_path):
    path = tmp_path / "data.json"
    with pytest.raises(FileNotFoundError):
        Owner.load_from_json(path)
    for content in ["not json", '{"version":2}', '{"version":1,"owner":{}}']:
        path.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError):
            Owner.load_from_json(path)
        assert path.read_text(encoding="utf-8") == content


def test_json_invalid_task_and_failed_save_preserve_good_file(tmp_path):
    owner = make_owner()
    path = tmp_path / "data.json"
    owner.save_to_json(path)
    original = path.read_text(encoding="utf-8")
    owner.available_minutes = -1
    with pytest.raises(ValueError):
        owner.save_to_json(path)
    assert path.read_text(encoding="utf-8") == original
    data = json.loads(original)
    data["owner"]["pets"][0]["tasks"][0]["time"] = "25:00"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        Owner.load_from_json(path)


def test_atomic_replace_failure_keeps_old_file_and_removes_temporary(tmp_path, monkeypatch):
    from pathlib import Path

    owner = make_owner()
    path = tmp_path / "data.json"
    owner.save_to_json(path)
    original = path.read_bytes()

    def fail_replace(self, target):
        raise OSError("Simulated disk failure")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="disk failure"):
        owner.save_to_json(path)
    assert path.read_bytes() == original
    assert not list(tmp_path.glob("*.tmp"))
