import random
import copy

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
PERIODS = [1,2,3,4,5,6,7]

POP = 20
GEN = 50
MUT = 0.1

def random_tt(subjects, staff_map, rooms):
    tt = []
    for s in subjects:
        hours = s["weekly_hours"]
        staffs = staff_map.get(s["id"], [])
        while hours > 0 and staffs:
            tt.append({
                "day": random.choice(DAYS),
                "period": random.choice(PERIODS),
                "subject_id": s["id"],
                "staff_id": random.choice(staffs),
                "classroom_id": random.choice(rooms)
            })
            hours -= 1
    return tt

def fitness(tt):
    score = 1000
    staff_slots = set()
    room_slots = set()

    for t in tt:
        s = (t["day"], t["period"], t["staff_id"])
        r = (t["day"], t["period"], t["classroom_id"])
        if s in staff_slots: score -= 50
        if r in room_slots: score -= 50
        staff_slots.add(s)
        room_slots.add(r)
    return score

def generate_timetable(subjects, staff_map, rooms):
    population = [random_tt(subjects, staff_map, rooms) for _ in range(POP)]

    for _ in range(GEN):
        population.sort(key=fitness, reverse=True)
        next_gen = population[:POP//2]
        while len(next_gen) < POP:
            p1, p2 = random.sample(next_gen, 2)
            cut = len(p1)//2
            child = copy.deepcopy(p1[:cut] + p2[cut:])
            if random.random() < MUT and child:
                c = random.choice(child)
                c["day"] = random.choice(DAYS)
                c["period"] = random.choice(PERIODS)
            next_gen.append(child)
        population = next_gen

    population.sort(key=fitness, reverse=True)
    return population[0]