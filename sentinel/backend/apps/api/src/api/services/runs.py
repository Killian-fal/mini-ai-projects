import store

DAYS = 30


def listed() -> tuple[list[store.Run], list[store.DayCount]]:
    return store.runs(), store.daily(DAYS)
