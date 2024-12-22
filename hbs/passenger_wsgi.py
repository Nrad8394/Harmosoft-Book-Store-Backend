import os
import sys
from django.core.wsgi import get_wsgi_application

# Set up the project base directory
sys.path.insert(0, "/home/harmoso1/repositories/Harmosoft-Book-Store-Backend/hbs")

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hbs.settings')

# Activate the virtual environment
activate_this = '/home/harmoso1/virtualenv/repositories/Harmosoft-Book-Store-Backend/hbs/3.11/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

application = get_wsgi_application()
