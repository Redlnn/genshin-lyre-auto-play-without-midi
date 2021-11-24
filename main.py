#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import ctypes
import os
import sys
import time

import regex
from loguru import logger

from config import DEBUG, DRY_RUN, GAME_PROCESS_NAME
from utils.focus import check_focus, set_focus
from utils.pressKey import press_and_release_key, press_and_release_muit_key

pause = False
if DEBUG:
    LOG_FORMAT = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSSS}</green> | <level>{level: <9}</level> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> '
    )
    LOG_LEVEL = 'DEBUG'
else:
    LOG_FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SS}</green> | <level>{level: <8}</level> | <level>{message}</level>'
    LOG_LEVEL = 'INFO'
logger.remove()
logger.add(sys.stderr, format=LOG_FORMAT, backtrace=True, diagnose=True, colorize=True, level=LOG_LEVEL)

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
        logger.warning('你的窗口焦点已离开原神游戏窗口，请在 10秒 内返回，否则程序自动退出')
        test = 0
        while True:
            test += 1
            if test >= 20:
                logger.error('窗口焦点离开原神游戏窗口过久')
                return False
            if check_focus(GAME_PROCESS_NAME):
                break
            time.sleep(0.5)
        return True
    return True


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
    global pause
    if music_score == '0':
        if not pause:
            logger.debug('此处有停顿')
            pause = True
        return 0
    elif music_score.startswith('(') and music_score.endswith(')'):
        pause = False
        tmp = music_score[1:-1]

        if regex.match('^[+\\-1-9]+', tmp):
            tmp = nmn_converter(tmp)
        elif not regex.match('^[a-hjmnq-zA-HJMNQ-Z]+', tmp):
            raise ValueError('乐谱格式错误')

        logger.debug(f'按下组合键：{tmp}')
        if DRY_RUN:
            return len(tmp)
        press_and_release_muit_key(tmp)
        return len(tmp)
    elif regex.match('^[a-hjmnq-zA-HJMNQ-Z]$', music_score):
        pause = False
        logger.debug(f'按下单个键：{music_score}')
        if DRY_RUN:
            return 1
        press_and_release_key(music_score)
        return 1
    elif music_score in music_score_map.keys():
        pause = False
        logger.debug(f'按下单个键：{music_score_map[music_score]}')
        if DRY_RUN:
            return 1
        press_and_release_key(music_score_map[music_score])
        return 1
    else:
        raise ValueError('乐谱格式错误')


async def play(music_scores: list, notes_interval: float) -> None:
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
        if not check_focus_on():
            break

        if step == 1:  # 蜜汁第一下按键会紧跟着第二下，给个补偿
            await asyncio.sleep(notes_interval - 0.03)

        if music_score.startswith('#'):
            notes_interval = round(60 / int(music_score[1:]), 5)
            logger.info('=====================')
            logger.info(f'BPM已更改为: {music_score[1:]}')
            if int(music_score[1:]) >= 600:
                logger.error('BPM 过快')
                break
            logger.info(f'每个节拍间隔{notes_interval}s')
            logger.info('=====================')
            continue
        elif music_score.startswith('//'):
            logger.info(f'注释 → {music_score[2:]}')
            continue
        else:
            await asyncio.sleep(notes_interval - 0.03)  # 减 0.03 是给 log 记录和其他操作占用时间的补偿

        step += await asyncio.to_thread(play_single, music_score)
    logger.info(f'演奏完毕，共按下按键 {step} 次')


async def main() -> None:
    """
    读取乐谱内容并传给演奏函数

    :return: None
    """
    while True:
        spectrum_list = os.listdir(os.path.join(os.getcwd(), 'spectrums'))
        for i in spectrum_list:
            if not i.endswith('.txt'):
                spectrum_list.remove(i)
        print('\n===========乐谱列表===========')
        print('0. 退出程序')
        for spectrum_id in range(1, len(spectrum_list) + 1):
            print(f'{spectrum_id}. {spectrum_list[spectrum_id-1]}')
        print('==============================')
        while True:
            spectrum_id = input('请输入你想演奏的乐谱ID并按回车键：')
            if not spectrum_id.isdigit():
                print()
                logger.error('请输入纯数字')
                print()
                continue
            elif spectrum_id == '0':
                print('你选择了退出程序...\n')
                exit()
            try:
                spectrum = spectrum_list[int(spectrum_id) - 1]
            except IndexError:
                print()
                logger.error(f'不存在ID为 {spectrum_id} 的乐谱')
                print()
                continue
            else:
                print(f'\n你选择的乐谱是: {spectrum}\n')
                print('请输入乐谱的BPM')
                print(' - BPM 即每分钟节拍数（演奏多少个音符）')
                print(' - 若乐谱中已设置BPM，可以直接按回车键')
                print(' - 如果你不知道你也可以直接按回车键，默认BPM为 140')
                print(' - 你也可以输入0并按回车键')
                while True:
                    bpm = input('请输入你选择的BPM并按回车键：')
                    if bpm == '0':
                        print('你选择了退出程序...\n')
                        exit()
                    elif bpm.isdigit():
                        bpm = int(bpm)
                        break
                    elif bpm == '':
                        bpm = 140
                        break
                    else:
                        print()
                        logger.error('请输入纯数字')
                        print()
                break
        print()
        logger.info(f'你所设置的BPM为 {bpm}')
        if not DRY_RUN:
            logger.info('5 秒后将自动为你切换到原神游戏窗口并开始演奏')
            time.sleep(5)
            if not set_focus('YuanShen.exe'):
                logger.error('找不到原神游戏进程，程序即将退出')
            else:
                logger.info('已自动为你切换到原神游戏窗口')
        else:
            logger.info('5 秒后开始测试演奏（不实际按下按键）')
            time.sleep(5)
        notes_interval = round(60 / bpm, 5)
        if bpm >= 600:
            raise ValueError('BPM 过快')
        logger.info(f'每个节拍间隔{notes_interval}s')
        logger.info('读取乐谱内容...')
        with open(os.path.join(os.path.dirname(__file__), 'spectrums', spectrum), 'r', encoding='utf-8') as f:
            txt = f.read()
        txt = txt.replace('\n', ' ').replace('\r', '').split()
        logger.info('读取完毕，开始演奏')
        logger.info('默认不显示当前按下的按键，如果想要查看当前按下的按键，请在配置中将 DEBUG 设置为 True')
        await play(txt, notes_interval)


if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin() or DRY_RUN:
        while True:
            os.system('cls')
            print(' > genshin-lyre-auto-play-without-midi')
            print(' > 无需MIDI文件的原神风物之诗琴自动演奏程序')
            print(' > 作者：Red_lnn')
            print(' > 链接：https://github.com/Redlnn/genshin-lyre-auto-play-without-midi/')
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(main())
            except KeyboardInterrupt:
                pass
            except Exception as e:
                logger.exception(e)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, __file__, None, 1)
