import enum

Action = enum.Enum('Action', [
    'set_sugar',
    'get_sugar',
    'add_cup',
    'get_suggestion',
    'list_cups',
    'update_cup',
])


def dispatch_action(db_session, action, data) -> dict:
    print(action, data)
    return {}
