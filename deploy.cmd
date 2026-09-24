@echo off
setlocal
set GIT="C:\Program Files\Git\bin\git.exe"
set ROOT=C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app
set LOG=%ROOT%\deploy.log
echo ===== %date% %time% ===== > %LOG%

cd /d %ROOT%
%GIT% --version >> %LOG% 2>&1

REM 取 GitHub token（Windows 凭证管理器）
for /f "tokens=*" %%a in ('echo protocol=https^&echo host=github.com^&echo. ^| %GIT% credential fill 2^>nul ^| findstr /b "password="') do set TOKEN=%%a
set TOKEN=%TOKEN:password==%
echo TOKEN_LEN=%TOKEN:~0,4%... >> %LOG%

REM 初始化仓库（若尚未）
if not exist .git (
  %GIT% init -b main >> %LOG% 2>&1
  echo init done >> %LOG%
)

REM 配置（避免交互）
set GCM_INTERACTIVE=never
set GIT_TERMINAL_PROMPT=0

REM 添加所有（忽略 .git 自身；如有 .workbuddy 子目录也一并纳入，无密钥）
%GIT% add -A >> %LOG% 2>&1
%GIT% commit -m "update: 知识类PDF右侧学习互动面板(背一背/测一测/用一用) + 缓存刷新" >> %LOG% 2>&1

REM 设置远端
%GIT% remote remove origin >nul 2>&1
%GIT% remote add origin https://github.com/Z11K345/hj8-english.git >> %LOG% 2>&1

REM 推送（最多重试3次）
set PUSHOK=0
for /l %%i in (1,1,3) do (
  echo --- push attempt %%i --- >> %LOG%
  %GIT% push -u origin main --force >> %LOG% 2>&1
  if errorlevel 0 (
    echo PUSH_RETURN=%%i >> %LOG%
    set PUSHOK=1
    goto :done
  )
)
:done
echo PUSHOK=%PUSHOK% >> %LOG%
echo ===== end ===== >> %LOG%
