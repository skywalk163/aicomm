@echo off
echo ============================================
echo   AI Community Server
echo ============================================
echo.
echo Virtual Environment: G:\dumate\.venv
echo.
echo Access URLs:
echo   http://localhost:6542/@@home
echo   http://localhost:6542/@@ideas
echo   http://localhost:6542/@@resources
echo   http://localhost:6542/@@projects
echo   http://localhost:6542/@@members
echo   http://localhost:6542/@@ai-assistant
echo.
echo Press Ctrl+C to stop the server.
echo ============================================
echo.

G:\dumate\.venv\Scripts\python.exe -c "from pyramid.paster import get_app; from waitress import serve; serve(get_app('development.ini', 'main'), host='0.0.0.0', port=6542)"
