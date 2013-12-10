# Unify Events

## Setup
1. Install Open-LDAP developement headers (debian: openldap-dev, rhel: openldap-devel)
2. Create virtual environment
2. cd to the new virtual environment
3. Clone repo to subdirectory (ex. git clone <url> src)
4. Install requirements

		pip install -r requirements.txt
5. Setup local settings using the local_settings.templ.py file
6. Setup apache/python.wsgi using apache/python.templ.wsgi
7. python manage.py syncdb

## Code Contribution
Never commit directly to master. Create a branch or fork and work on the new feature. Once it is complete it will be merged back to the master branch.

If you use a branch to develop a feature, make sure to delete the old branch once it has been merged to master.
