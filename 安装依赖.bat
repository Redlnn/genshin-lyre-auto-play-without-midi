@echo off
%~d0
cd %~s0\..
cls
python -m pip install -U pip
python -m pip install -r requirements.txt
