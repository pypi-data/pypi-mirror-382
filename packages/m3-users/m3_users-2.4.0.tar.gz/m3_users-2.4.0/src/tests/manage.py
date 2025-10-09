#!/usr/bin/python
import importlib
import os
import sys

from django.core.management import (
    execute_from_command_line,
)


project_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_path, '../'))
sys.path.insert(0, os.path.join(project_path, '../env'))
sys.path.insert(0, os.path.join(project_path, '../env/m3/vendor'))

settings_module = 'settings'

try:
    importlib.import_module(settings_module)
except ImportError:
    import sys

    sys.stderr.write(
        "Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things."
        "\nYou'll have to run django-admin, passing it your settings module."
        "\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__
    )
    sys.exit(1)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
