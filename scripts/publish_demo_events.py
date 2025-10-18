import requests, random

API = "http://localhost:8000"
requests.post(f"{API}/events/reset")

demo = []
# 20 willekeurige schoten/3 goals
for i in range(20):
    demo.append({
        "ts_ms": i*10000,
        "event_type": "shot",
        "player_id": f"tracker-{random.randint(7,18)}",
        "x": random.random(),
        "y": random.random(),
        "distance_m": round(random.uniform(3.0,9.0), 1)
    })
for i in range(3):
    demo.append({
        "ts_ms": 50000+i*15000,
        "event_type": "goal",
        "player_id": f"tracker-{random.randint(7,18)}",
        "x": random.random(),
        "y": random.random(),
        "distance_m": round(random.uniform(3.0,9.0), 1)
    })

r = requests.post(f"{API}/events/batch", json=demo)
print(r.json())
