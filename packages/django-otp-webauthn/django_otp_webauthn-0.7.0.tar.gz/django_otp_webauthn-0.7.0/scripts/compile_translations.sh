#!/bin/sh

# This script is used to compile translations
# Usage:
#
# ./compile_translations.sh

set -e

python manage.py compilemessages --ignore venv --ignore client --ignore .tox --ignore dist --ignore node_modules --ignore docs $@
