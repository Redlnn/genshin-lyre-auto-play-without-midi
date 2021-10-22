#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import random
# import time
import win32api
import win32con

__all__ = [
    'press_key', 'release_key', 'press_and_release_key', 'press_and_release_muit_key'
]

key_map = {
    'A': 65,
    'B': 66,
    'C': 67,
    'D': 68,
    'E': 69,
    'F': 70,
    'G': 71,
    'H': 72,
    'J': 74,
    'M': 77,
    'N': 78,
    'Q': 81,
    'R': 82,
    'S': 83,
    'T': 84,
    'U': 85,
    'V': 86,
    'W': 87,
    'X': 88,
    'Y': 89,
    'Z': 90
}


def press_key(key_code: int) -> None:
    """
    按下按键

    :param key_code: 按键值
    :return: None
    """
    win32api.keybd_event(key_code, win32api.MapVirtualKey(key_code, 0), 0, 0)


def release_key(key_code: int) -> None:
    """
    抬起按键

    :param key_code: 按键值
    :return: None
    """
    win32api.keybd_event(key_code, win32api.MapVirtualKey(
            key_code, 0), win32con.KEYEVENTF_KEYUP, 0)


def press_and_release_key(key: int | str) -> None:
    """
    按一下按键

    :param key: 按键名/按键值
    :return: None
    """
    if isinstance(key, str):
        press_key(key_map[key.upper()])
        # time.sleep(random.uniform(0.02, 0.1))
        release_key(key_map[key.upper()])
    elif isinstance(key, int):
        press_key(key)
        # time.sleep(random.uniform(0.02, 0.1))
        release_key(key)


def press_and_release_muit_key(keys: str) -> None:
    """
    按下多个按键

    :param keys: 要按下的按键列表
    :return: None
    """
    for _ in keys:
        if isinstance(_, str):
            press_key(key_map[_.upper()])
        elif isinstance(_, int):
            press_key(_)
    # time.sleep(random.uniform(0.02, 0.1))
    for _ in keys:
        if isinstance(_, str):
            release_key(key_map[_.upper()])
        elif isinstance(_, int):
            release_key(_)
