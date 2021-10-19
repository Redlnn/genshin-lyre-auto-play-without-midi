#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ctypes
import logging
import os
import regex
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor

from config import BPM, DEBUG, DRY_RUN, GAME_PROCESS_NAME, MUSIC_SCORE
from utils.focus import check_focus, set_focus
from utils.logger import logger
from utils.pressKey import press_and_release_key, press_and_release_muit_key

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

pool = ProcessPoolExecutor(6)


def check_focus_on() -> None:
    """
    检查鼠标焦点是否在游戏里

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


def play_single(music_score: str) -> int:
    """
    演奏单个音符/音符组合

    :param music_score: 单个按键/按键组合
    :return: 按键个数
    """
    if music_score == '0':
        logger.debug('此处有空音符')
        return 0
    elif music_score.startswith('(') and music_score.endswith(')'):
        tmp = music_score[1:-1]
        if not regex.match('^[a-zA-Z]+', tmp):
            raise ValueError('乐谱格式错误')
        logger.info(f'按下按键组合：{music_score[1:-1]}')
        if DRY_RUN:
            return len(music_score[1:-1])
        pool.submit(press_and_release_muit_key, tmp)
        return len(music_score[1:-1])
    elif regex.match('^[a-zA-Z]$', music_score):
        logger.info(f'按下按键：{music_score}')
        if DRY_RUN:
            return 1
        pool.submit(press_and_release_key, music_score)
        return 1
    else:
        raise ValueError('乐谱格式错误')


def play(music_scores: list) -> None:
    """
    演奏

    :param music_scores: 从谱读到的单个按键组成的列表
    :return: None
    """
    logger.debug(f'获取到的音符列表如下：{music_scores}')
    time.sleep(0.5)
    notes_speed = round(60 / BPM, 5)
    logger.info(f'BPM: {BPM}')
    if BPM >= 600:
        raise ValueError('BPM 过快')
    logger.info(f'每个节拍间隔{notes_speed}s')
    logger.info('准备开始演奏，演奏过程中清保持焦点在游戏窗口')
    time.sleep(0.5)
    step = 0

    for music_score in music_scores:
        check_focus_on()

        if music_score.startswith('#'):
            notes_speed = round(60 / int(music_score[1:]), 5)
            logger.info(f'BPM已更改为: {music_score[1:]}')
            if BPM >= 600:
                raise ValueError('BPM 过快')
            logger.info(f'每个节拍间隔{notes_speed}s')
            continue
        elif music_score.startswith('//'):
            logger.info(f'注释 → {music_score[2:]}')
            continue
        else:
            time.sleep(notes_speed)
            logger.debug('sleep: %f', notes_speed)

        # 不知道为什么，实际在游戏里按下第一个音的时间会和按下第二个音的时间非常接近，甚至会吞掉
        # 但是日志里的时间间隔却是正常的
        # 只能手动加一个延迟
        if step == 1 and notes_speed <= 0.5:
            time.sleep(notes_speed / 2)
            logger.debug('sleep: %f', notes_speed / 2)

        step += play_single(music_score)
    logger.info(f'演奏完毕，共按下按键 {step} 次')


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


if __name__ == '__main__':
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
