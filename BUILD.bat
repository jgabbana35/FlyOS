@echo off
echo =====================================================
echo   Fly OS v5.0 — Triple Hybrid Engine
echo   Building EXE...
echo =====================================================

pip install google-genai customtkinter pillow pyperclip requests ^
    python-docx reportlab python-pptx openpyxl ^
    beautifulsoup4 lxml pandas xlrd pyinstaller ^
    --quiet --upgrade

python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "FlyOS" ^
  --hidden-import customtkinter ^
  --hidden-import google.genai ^
  --hidden-import google.genai.types ^
  --hidden-import PIL ^
  --hidden-import PIL._tkinter_finder ^
  --hidden-import pyperclip ^
  --hidden-import docx ^
  --hidden-import reportlab ^
  --hidden-import pptx ^
  --hidden-import openpyxl ^
  --hidden-import bs4 ^
  --hidden-import lxml ^
  --hidden-import pandas ^
  --hidden-import sqlite3 ^
  --collect-data customtkinter ^
  --collect-data google.genai ^
  --add-data "app;app" ^
  main.py

echo.
if exist "dist\FlyOS.exe" (
  echo =====================================================
  echo   SUCCESS! dist\FlyOS.exe is ready.
  echo =====================================================
  copy "version.json" "dist\version.json"
) else (
  echo BUILD FAILED — check errors above
)
pause
