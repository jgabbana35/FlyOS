"""Fly OS v5 — Triple Hybrid Engine AI Assistant"""
import sys
import os

# Ensure the project root is always on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gui import FlyOS

if __name__ == "__main__":
    app = FlyOS()
    app.mainloop()
