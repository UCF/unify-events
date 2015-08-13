# Unify Events - [Calendar of Events and Activities at the University of Central Florida and Orlando, FL](http://events.ucf.edu/upcoming/)

## Installation and Setup
1. Install Elasticsearch on your server (tested with v1.1.0) (http://www.elasticsearch.org/overview/elkdownloads/).  Requires at least Java 6.
    - via Homebrew: `brew install elasticsearch`
    - via apt/yum: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html
2. Start Elasticsearch
    - Unix: `bin/elasticsearch`
    - Windows: `bin/elasticsearch.bat`
    - See Linux service docs:
        - http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup.html
        - http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-service.html

3. Install Open-LDAP development headers (debian: openldap-dev, rhel: openldap-devel)
4. Install Virtualenv for Python
  - via pip: `[sudo] pip install virtualenv`
5. Create virtual environment and `cd` to it

        virtualenv ENV
        cd ENV
6. Clone repo to a subdirectory (ex. `git clone REPO_URL src`)
7. Activate virtual environment

        source bin/activate
8. `cd` to new src directory and install requirements

        cd src
        pip install -r requirements.txt
9. Set up local settings using the local_settings.templ.py file
10. Set up apache/python.wsgi using apache/python.templ.wsgi
11. Set up static_files/static/robots.txt using static_files/static/robots.templ.txt
12. If necessary, configure VirtualHosts using apache/vhost.conf template
13. Sync the database. Create a new admin user when prompted. This user should have a unique (non-NID based) username.

        python manage.py syncdb
14. If you don't intend on importing any existing calendar data, create a Main Calendar. Otherwise, skip this step

        python manage.py shell
        >>> from events.models import Calendar
        >>> c = Calendar(title='Events at UCF')
        >>> c.save()
        >>> exit()
15. Rebuild the search index

        python manage.py rebuild_index
16. Collect static files

        python manage.py collectstatic -cl


## Importing Data

### UNL Events Import
Note that this importer should only be run on a fresh database, immediately after running `python manage.py syncdb` or `python manage.py flush`.

**Before running this import, make sure that a new user has been created in Django for every non-NID-based user in the UNL system. These users' events will fail to import otherwise.**

1. cd to the new virtual environment src folder
2. Activate virtual environment

        source ../bin/activate
3. Add old events database information to settings_local.py under DATABASES name 'unlevents'.  Make sure that SEARCH_ENABLED and ENABLE_CLEARCACHE are set to 'False'.
4. Run import command

        python manage.py import-unl-events
5. Set SEARCH_ENABLED and ENABLE_CLEARCACHE in settings_local.py back to 'True'.
6. Restart the app
7. Rebuild the search index

        python manage.py rebuild_index
8. Ban cache as necessary

### Locations Import
1. cd to the new virtual environment src folder
2. Activate virtual environment

        source ../bin/activate
3. Make sure that MAPS_DOMAIN and LOCATION_DATA_URL are set in settings_local.py, and that SEARCH_ENABLED and ENABLE_CLEARCACHE are set to 'False'.
4. Run import command

        python manage.py import-locations
5. Set SEARCH_ENABLED and ENABLE_CLEARCACHE in settings_local.py back to 'True'.
6. Restart the app
7. Rebuild the search index

        python manage.py rebuild_index
8. Ban cache as necessary


## Code Contribution
Never commit directly to master. Create a branch or fork and work on the new feature. Once it is complete it will be merged back to the master branch.

If you use a branch to develop a feature, make sure to delete the old branch once it has been merged to master.


## Development

### Sass

#### Gulp Setup
This project uses gulp to handle various tasks, such as installation of bower packages, compiling and minifying sass files and minifying/uglifying javascript. Use the following steps to setup gulp for this project.

1. Make sure an up to date version of npm is installed.
  * (OSX) brew install npm
  * (Debian) apt-get install nodejs
  * (RHEL) yum install npm
2. Run `npm install` from the root directory to install node packages defined in package.json, including gulp and bower. Node packages will save to a `node_modules` directory in the root of this repository. This directory is in the `.gitignore` list and should not be pushed to repository.
3. Install all front-end components and compile static assests by running `gulp default`. During development, run `gulp watch` to detect static file changes automatically. When a change is detected, minification and compilation commands will run automatically.
4. Make sure up-to-date concatenated/minified files ("artifacts") are pushed to the repo when making changes to static files.

#### Bootstrap
This project uses the official Sass port of Twitter Bootstrap (https://github.com/twbs/bootstrap-sass) for base styling of templates. **Do not modify the files in this directory**--override variables as necessary in `static_files/assets/scss/style.scss`.

The current version of Bootstrap is v3.3.5.

To upgrade Bootstrap, specify the version number in `bower.json`.

#### Font Awesome
Version 4.0.3 of Font Awesome (http://fontawesome.io/) is used as a replacement for Bootstrap's Glyphicon icon library. **Do not modify the files in this directory**--override variables as necessary in `static_files/assets/scss/style.scss`.

Note that these icons do not overwrite the Glyphicon library; both are available to use, but Font Awesome fonts are preferred. See the Font Awesome docs for usage.

To upgrade, specify the version number in `bower.json`.

#### Theme Sass Files
All of the raw custom styles for this project are contained in separate Sass files in `static_files/assets/scss/`. When modifying stylesheets in this project, only modify the files in this directory; **do NOT modify files in `static_files/static/css/`**! Sass files compile and write to this directory.

Partial Sass files are generally separated out by function, and must be compiled in a specific order. Keep in mind the following guidelines when modifying or adding styles:

1. `_utilities.scss`
   Where generic "helper" classes are defined.
2. `_type.scss`
   Where generic paragraph, heading, link, list, etc. styles are defined. These can override Bootstrap-related classes.
3. `_components.scss`
   Where generic Bootstrap component overrides (buttons, modals, panels, dropdowns, etc.) are defined.
4. `_forms.scss`
   Where generic form-related styles are defined. These can override Bootstrap-related classes.
5. `_calendar-small.scss`
   Styles specific to the small calendar sidebar widget, generated by the `{% calendar_widget %}` template tag. These styles do not modify the publicly-available Events Widget styles; these are managed separately in `/static_files/events-widget/`.
6. `_calendar-large.scss`
   Styles specific to the full-size calendar (used in the frontend Calendar Month View), generated by the `{% calendar_widget %}` template tag.
7. `_layout.scss`
   Styles related to base page structure; i.e. elements you would find in templates named `base.html` (header, navigation, sidebar, footer). View-specific styles should not be added here.
8. `_views-frontend.scss`
   Frontend, view-specific styles. Make sure to label each view with specific comments, and group similar views together (i.e. a set of single Calendar view styles should go directly above or below already-defined Calendar view styles.)
9. `_views-backend.scss`
   Backend, view-specific styles. Make sure to label each view with specific comments, and group similar views together (i.e. a set of single Calendar view styles should go directly above or below already-defined Calendar view styles.)

### Javascript

#### Concatenation Details
This project combines vendor javascript libraries with our own so fewer files need to be delivered to the client. The list below lays out the basic concatenation/uglification scheme.

* script.min.js
  * jquery.placeholder.js - *vender*
  * bootstrap.js - *vendor*
  * script.js - *project*
* script-frontend.min.js
  * script-frontend.js - *project*
*script-backend.min.js
  * bootstrap3-typeahead.js - *vendor*
  * jquery.timepicker.js - *vendor*
  * bootstrap-datepicker.js - *vendor*
  * script-manager.js - *project*
* wysiwyg.min.js
  * wysihtml5-0.3.0.js - *vendor*
  * bootstrap3-wysihtml5.js - *vendor*

Scripts marked `*vendor*` can be found in `static_files/assets/components` and are installed by bower during the gulp processing. These files should not be edited.

Scripts marked `*project*` are scripts maintained by this project and can found in `static_files/assets/js`.