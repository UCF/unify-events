# Unify Events

## Setup
1. Install Elasticsearch on your server (tested with v1.1.0) (http://www.elasticsearch.org/overview/elkdownloads/).  Requires at least Java 6.
	- via Homebrew: `brew install elasticsearch`
	- via apt/yum: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html
2. Start Elasticsearch
	- Unix: `bin/elasticsearch`
	- Windows: `bin/elasticsearch.bat`
	- See Linux service docs:
		- http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup.html
		- http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-service.html

3. Install Open-LDAP developement headers (debian: openldap-dev, rhel: openldap-devel)
4. Ensure your environment has virtualenv and pip installed for python
5. Create virtual environment
6. cd to the new virtual environment
7. Clone repo to subdirectory (ex. git clone <url> src)
8. Activate virtual environment

        source bin/activate
9. Install requirements

        pip install -r src/requirements.txt
10. Setup local settings using the local_settings.templ.py file
11. Setup apache/python.wsgi using apache/python.templ.wsgi
12. Sync the database
		
		python manage.py syncdb
13. Rebuild the search index

		python manage.py rebuild_index

## Import
1. cd to the new virtual environment src folder
2. Activate virtual environment

        source ../bin/activate
3. Add old events database information to local_settings.py under DATABASES name 'unlevents'
4. Run import command

        python manage.py import-unl-events

## Code Contribution
Never commit directly to master. Create a branch or fork and work on the new feature. Once it is complete it will be merged back to the master branch.

If you use a branch to develop a feature, make sure to delete the old branch once it has been merged to master.
