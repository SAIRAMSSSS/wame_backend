import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@yultimate.com', 'admin123')
    print("✅ Superuser 'admin' created successfully!")
    print("Username: admin")
    print("Password: admin123")
    print("Access admin panel at: http://127.0.0.1:8000/admin/")
else:
    print("⚠️ Superuser 'admin' already exists")
    print("Username: admin")
    print("Password: admin123 (if not changed)")
    print("Access admin panel at: http://127.0.0.1:8000/admin/")
