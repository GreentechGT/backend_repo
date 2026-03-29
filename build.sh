#!/usr/bin/env bash
# exit on error
set -o errexit

echo ">>> Starting Render Build Process..."

python -m pip install --upgrade pip
pip install -r requirements.txt

echo ">>> Running Collectstatic..."
python manage.py collectstatic --no-input

echo ">>> Running Migrations..."
python manage.py migrate

echo ">>> Loading Database Backup..."
if [ -f db_backup.json ]; then
    python manage.py loaddata -v 2 db_backup.json
    echo ">>> Database Backup Loaded Successfully!"
else
    echo ">>> ERROR: db_backup.json NOT FOUND!"
fi

echo ">>> Build Process Complete!"
