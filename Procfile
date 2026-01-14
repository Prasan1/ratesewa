release: python fix_clinic_tables.py && python fix_duplicate_cities.py
web: gunicorn --worker-tmp-dir /dev/shm --workers 1 --threads 2 --max-requests 500 --max-requests-jitter 50 --bind 0.0.0.0:$PORT wsgi:application
