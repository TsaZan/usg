#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create Django project
django-admin startproject ugc_platform .

# Create Django apps
python manage.py startapp users
python manage.py startapp content
python manage.py startapp social
python manage.py startapp ai
python manage.py startapp analytics
python manage.py startapp api

# Create necessary directories
mkdir -p media static templates
mkdir -p users/templates/users
mkdir -p content/templates/content
mkdir -p social/templates/social
mkdir -p ai/templates/ai
mkdir -p analytics/templates/analytics
mkdir -p api/templates/api

# Create logs directory
mkdir -p logs

# Set up initial database
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

echo "Project setup completed successfully!" 