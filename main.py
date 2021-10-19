#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ctypes
import logging
import os
import sys
import time
import traceback

import regex

from config import BPM, DEBUG, DRY_RUN, GAME_PROCESS_NAME, MUSIC_SCORE
from utils.focus import check_focus, set_focus
from utils.logger import logger
from utils.pressKey import press_and_release_key, press_and_release_muit_key

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# 此处前后顺序会影响 nmn_converter() 的结果，单个数字必须放最后
music_score_map = {
    '+1': 'Q',
    '+2': 'W',
    '+3': 'E',
    '+4': 'R',
    '+5': 'T',
    '+6': 'Y',
    '+7': 'U',
    '-1': 'Z',
    '-2': 'X',
    '-3': 'C',
    '-4': 'V',
    '-5': 'B',
    '-6': 'N',
    '-7': 'M',
    '1': 'A',
    '2': 'S',
    '3': 'D',
    '4': 'F',
    '5': 'G',
    '6': 'H',
    '7': 'J',
}


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


# nmn -> Numbered musical notation 即简谱
def nmn_converter(nmn: str) -> str:
    """
    简谱（手机谱）转换为键盘按键

    :param nmn: 简谱音符/音符组合
    :return: 转换结果
    """
    if len(nmn) == 1:
        return music_score_map[nmn]
    else:
        result = nmn
        for i, j in music_score_map.items():
            result = result.replace(i, j)
        return result


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

        if regex.match('^[+\\-1-9]+', tmp):
            tmp = nmn_converter(tmp)
        elif not regex.match('^[a-zA-Z]+', tmp):
            raise ValueError('乐谱格式错误')

        logger.info(f'按下组合键：{tmp}')
        if DRY_RUN:
            return len(tmp)
        press_and_release_muit_key(tmp)
        return len(tmp)
    elif regex.match('^[a-zA-Z]$', music_score):
        logger.info(f'按下单个键：{music_score}')
        if DRY_RUN:
            return 1
        press_and_release_key(music_score)
        return 1
    elif music_score in music_score_map.keys():
        logger.info(f'按下单个键：{music_score_map[music_score]}')
        if DRY_RUN:
            return 1
        press_and_release_key(music_score_map[music_score])
        return 1
    else:
        raise ValueError('乐谱格式错误')


def play(music_scores: list, notes_interval: float) -> None:
    """
    演奏

    :param music_scores: 从谱读到的单个按键组成的列表
    :param notes_interval: 按键间隔
    :return: None
    """
    logger.debug(f'获取到的音符列表如下：{music_scores}')
    logger.info('准备开始演奏，演奏过程中清保持焦点在游戏窗口')
    logger.info('============================================')
    time.sleep(0.5)
    step = 0

    for music_score in music_scores:
        check_focus_on()

        if music_score.startswith('#'):
            notes_interval = round(60 / int(music_score[1:]), 5)
            logger.info('=====================')
            logger.info(f'BPM已更改为: {music_score[1:]}')
            if BPM >= 600:
                raise ValueError('BPM 过快')
            logger.info(f'每个节拍间隔{notes_interval}s')
            logger.info('=====================')
            continue
        elif music_score.startswith('//'):
            logger.info(f'注释 → {music_score[2:]}')
            continue
        else:
            time.sleep(notes_interval - 0.04)  # 减 0.04 是给 log 记录和其他操作占用时间的补偿
            logger.debug('sleep: %f', notes_interval)

        step += play_single(music_score)
    logger.info(f'演奏完毕，共按下按键 {step} 次')


def main() -> None:
    """
    读取乐谱内容并传给演奏函数

    :return: None
    """
    notes_interval = round(60 / BPM, 5)
    logger.info(f'BPM: {BPM}')
    if BPM >= 600:
        raise ValueError('BPM 过快')
    logger.info(f'每个节拍间隔{notes_interval}s')
    logger.info('读取乐谱内容')
    with open(os.path.join(os.path.dirname(__file__), 'spectrums', MUSIC_SCORE), 'r', encoding='utf-8') as f:
        txt = f.read()
    txt = txt.replace('\n', ' ').replace('\r', '').split()
    logger.info('读取完毕')
    play(txt, notes_interval)


if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin() or DRY_RUN:
        logger.info('genshin-lyre-auto-play-without-midi')
        logger.info('无需MIDI文件的原神风物之诗琴自动演奏程序')
        logger.info('作者：Red_lnn')
        logger.info('https://github.com/Redlnn/genshin-lyre-auto-play-without-midi/')
        logger.info('==============================================================')
        time.sleep(0.5)
        try:
            if DRY_RUN:
                main()
            else:
                if not set_focus('YuanShen.exe'):
                    logger.error('找不到原神游戏进程，程序即将退出')
                else:
                    logger.info('已自动切换到原神游戏窗口')
                    main()
        except KeyboardInterrupt:
            pass
        except ValueError as e:
            logger.error(e)
        except FileNotFoundError:
            logger.error(f'spectrums 文件夹中不存在名为 "{MUSIC_SCORE}" 的文件')
        except:  # noqa
            logger.error(traceback.format_exc())
        finally:
            os.system('pause')
    else:
        ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', sys.executable, __file__, None, 1)
