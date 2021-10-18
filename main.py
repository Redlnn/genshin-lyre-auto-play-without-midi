#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import ctypes
import os
import random
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor

import regex
import win32api
import win32con

from config import BPM, GAME_PROCESS_NAME, MUSIC_SCORE, DRY_RUN
from focus import check_focus, set_focus
from logger import logger

pool = ProcessPoolExecutor(6)

key_map = {
    'A': 65, 'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70, 'G': 71, 'H': 72, 'I': 73, 'J': 74, 'K': 75, 'L': 76, 'M': 77,
    'N': 78, 'O': 79, 'P': 80, 'Q': 81, 'R': 82, 'S': 83, 'T': 84, 'U': 85, 'V': 86, 'W': 87, 'X': 88, 'Y': 89, 'Z': 90
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
        time.sleep(random.uniform(0.02, 0.1))
        release_key(key_map[key.upper()])
    elif isinstance(key, int):
        press_key(key)
        time.sleep(random.uniform(0.02, 0.1))
        release_key(key)


def press_and_release_muit_key(keys: list) -> None:
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
    time.sleep(random.uniform(0.02, 0.1))
    for _ in keys:
        if isinstance(_, str):
            release_key(key_map[_.upper()])
        elif isinstance(_, int):
            release_key(_)


def check_focus_on() -> None:
    """
    检查鼠标焦点是都在游戏里

    :return: None
    """
    if not check_focus(GAME_PROCESS_NAME):
        logger.warning('你的窗口焦点已离开原神游戏窗口，请在5秒内返回，否则程序自动退出')
        test = 0
        while 1:
            test += 1
            if test >= 10:
                raise ValueError('焦点离开原神游戏窗口过久')
            if check_focus(GAME_PROCESS_NAME):
                break
            time.sleep(0.5)


def play(music_score: list) -> None:
    """
    演奏

    :param music_score: 从谱读到的单个按键组成的列表
    :return: None
    """
    time.sleep(0.5)
    notes_speed = round(60 / BPM, 5)
    logger.info(f'BPM: {BPM}')
    logger.info(f'每个节拍间隔{notes_speed}s')
    logger.info('准备开始演奏，演奏过程中清保持焦点在游戏窗口')
    time.sleep(0.5)

    for i in music_score:
        if i.startswith('#'):
            notes_speed = round(60 / int(i[1:]), 5)
            logger.info(f'BPM已更改为: {i[1:]}')
            logger.info(f'每个节拍间隔{notes_speed}s')
            continue
        elif i.startswith('//'):
            logger.info(f'此处有注释：{i[2:]}')
            continue
        else:
            time.sleep(notes_speed)

        if i == '0':
            pass
        elif i.startswith('(') and i.endswith(')'):
            tmp = i[1:-1]
            if not regex.match('^[a-zA-Z]+', tmp):
                raise ValueError('乐谱格式错误')
            logger.info(f'按下按键：{i[1:-1]}')
            if DRY_RUN:
                continue
            pool.submit(press_and_release_muit_key, tmp)
            continue
        elif regex.match('^[a-zA-Z]$', i):
            logger.info(f'按下按键：{i}')
            if DRY_RUN:
                continue
            pool.submit(press_and_release_key, i)
        else:
            raise ValueError('乐谱格式错误')

        check_focus_on()


def main() -> None:
    """
    读取乐谱内容并传给演奏函数

    :return: None
    """
    logger.info('读取乐谱内容')
    with open(MUSIC_SCORE, 'r', encoding='utf-8') as f:
        txt = f.read()
    txt = txt.replace('\n', ' ').replace('\r', '').split()
    logger.info('读取完毕')
    play(txt)
    logger.info('演奏完毕')


if __name__ == '__main__':
    DRY_RUN = False
    if ctypes.windll.shell32.IsUserAnAdmin() or DRY_RUN:
        if not DRY_RUN:
            if not set_focus('YuanShen.exe'):
                logger.error('找不到原神游戏进程，程序即将退出')
                sys.exit(1)
        try:
            main()
        except KeyboardInterrupt:
            pass
        except ValueError as e:
            logger.error(e)
        except:  # noqa
            logger.error(traceback.format_exc())
        finally:
            pool.shutdown()
            if not DRY_RUN:
                os.system('pause')
    else:
        ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', sys.executable, __file__, None, 1)
