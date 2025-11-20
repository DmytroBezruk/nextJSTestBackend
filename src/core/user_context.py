"""Utilities for storing and retrieving the current authenticated user in thread-local storage.

This avoids passing user explicitly through many layers while keeping it explicit
and testable. Use cautiously; prefer explicit dependency injection where feasible.
"""
from threading import local
from typing import Optional

from django.contrib.auth import get_user_model

_thread_locals = local()


def set_current_user(user) -> None:
    _thread_locals.user = user


def get_current_user() -> Optional[get_user_model()]:
    return getattr(_thread_locals, "user", None)


def clear_current_user() -> None:
    if hasattr(_thread_locals, "user"):
        del _thread_locals.user

