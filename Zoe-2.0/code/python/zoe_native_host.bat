@echo off
setlocal enabledelayedexpansion
set ROOT_DIR=%~dp0
set PY=python
if defined PROGRAMFILES(x86) if exist "%SystemRoot%\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe" set PY=python
set HOST=%ROOT_DIR%zoe_native_host.py
"%PY%" "%HOST%" %*
