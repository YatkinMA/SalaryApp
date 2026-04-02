@echo off
chcp 1251 > nul
echo Удаление старых сборок...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del *.spec

echo Установка зависимостей...
pip install -r requirements.txt

echo Сборка приложения...
pyinstaller --onedir --windowed --name "SalarySystem" ^
    --hidden-import PyQt5.sip ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    --hidden-import sqlalchemy ^
    --collect-all PyQt5 ^
    --collect-all sqlalchemy ^
    main.py

echo Готово! Исполняемый файл: dist\SalarySystem\SalarySystem.exe
pause
