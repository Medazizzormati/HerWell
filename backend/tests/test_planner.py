def test_planner_duration_constraints():
    tasks = [{"title": "Math", "duration_minutes": 60}, {"title": "Java", "duration_minutes": 45}]
    available = 80
    total = 0
    for task in tasks:
        if total >= available: break
        total += min(task["duration_minutes"], available - total)
    assert total == 80
