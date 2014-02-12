# Unify Events

## Setup
1. Install Open-LDAP developement headers (debian: openldap-dev, rhel: openldap-devel)
2. Ensure your environment has virtualenv and pip installed for python
3. Create virtual environment
4. cd to the new virtual environment
5. Clone repo to subdirectory (ex. git clone <url> src)
6. Activate virtual environment

        source bin/activate
7. Install requirements

		pip install -r src/requirements.txt
8. Setup local settings using the local_settings.templ.py file
9. Setup apache/python.wsgi using apache/python.templ.wsgi
10. python manage.py syncdb

## Code Contribution
Never commit directly to master. Create a branch or fork and work on the new feature. Once it is complete it will be merged back to the master branch.

If you use a branch to develop a feature, make sure to delete the old branch once it has been merged to master.
