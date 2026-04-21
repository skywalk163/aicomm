@echo off
REM AI共创社区安装脚本 (Windows)

echo ========================================
echo AI共创社区 - 安装脚本
echo ========================================

REM 检查虚拟环境
if not exist "..\.venv" (
    echo 创建虚拟环境...
    python -m venv ..\.venv
)

REM 激活虚拟环境
call ..\.venv\Scripts\activate.bat

REM 安装依赖
echo.
echo 安装 Kotti 核心...
cd ..\Kotti
pip install -e ".[testing]"

echo.
echo 安装 kotti_g4f 插件...
cd ..\kotti_g4f
pip install -e ".[testing]"

echo.
echo 安装 AI共创社区插件...
cd ..\kotti_ai_community
pip install -e ".[testing]"

REM 初始化数据库
echo.
echo 初始化数据库...
cd ..\Kotti
if not exist "kotti.db" (
    echo 创建数据库...
    python -c "from kotti import initialize_sql; initialize_sql('sqlite:///kotti.db')"
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动服务器:
echo   cd kotti_ai_community
echo   ..\.venv\Scripts\pserve.exe development.ini
echo.
echo 访问: http://localhost:6542
echo ========================================
pause
