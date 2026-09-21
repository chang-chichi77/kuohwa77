# -*- encoding: utf8 -*-
from flask import session


def is_overlap(a, b):
    a, b = map(lambda x: x if isinstance(x, list) or isinstance(x, tuple) else [x], [a, b])
    intersection_ab = set(a) & set(b)
    if len(intersection_ab) == 0:
        return False
    else:
        return True


def check_roles_permission(*roles):
    roles = roles or []
    user_role = session.get('roles') or ""
    return is_overlap(roles, user_role)