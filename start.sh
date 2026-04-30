#!/bin/bash
# FarmVault - Start Development Server
echo "🐄 Starting FarmVault Development Server..."
echo "   Database: SQLite"
echo "   URL: http://127.0.0.1:8000/"
echo "   Admin: http://127.0.0.1:8000/admin/"
echo ""
cd /home/z/my-project
/home/z/.venv/bin/python3 manage.py runserver 0.0.0.0:8000
