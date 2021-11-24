#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ctypes import CDLL, byref, c_ulong

import psutil
import win32com.client
import win32con
import win32gui
import win32process

__all__ = ['check_focus', 'set_focus']

shell = win32com.client.Dispatch('WScript.Shell')
user32dll = CDLL('user32.dll')


def get_pid_for_pname(process_name) -> int:
    pids = psutil.pids()  # 获取主机所有的PID
    for pid in pids:  # 对所有PID进行循环
        try:
            p = psutil.Process(pid)  # 实例化进程对象
            if p.name() == process_name:  # 判断实例进程名与输入的进程名是否一致（判断进程是否存活）
                return pid  # 返回
        except psutil.NoSuchProcess:
            pass
    return 0


def get_hwnds_for_pid(pid) -> list:
    def callback(hwnd, hwnd_s):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnd_s.append(hwnd)
            return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def check_focus(process_name: str) -> bool:
    target_pid = get_pid_for_pname(process_name)
    hwnd = user32dll.GetForegroundWindow()
    pid = c_ulong(0)
    # 获取进程ID
    user32dll.GetWindowThreadProcessId(hwnd, byref(pid))
    top_pid = int(pid.value)
    return top_pid == target_pid


def set_focus(process_name: str) -> bool:
    pid = get_pid_for_pname(process_name)
    if pid:
        for hwnd in get_hwnds_for_pid(pid):
            shell.SendKeys('%')
            user32dll.LockSetForegroundWindow(2)
            if user32dll.IsIconic(hwnd):
                win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
            user32dll.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
            user32dll.SetForegroundWindow(hwnd)
            user32dll.SetActiveWindow(hwnd)
        return True
    return False
