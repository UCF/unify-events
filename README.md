# Unify Events - [Calendar of Events and Activities at the University of Central Florida and Orlando, FL](https://events.ucf.edu/upcoming/)

## Installation and Setup
1. Install Open-LDAP development headers (debian: openldap-dev, rhel: openldap-devel)
  - via Homebrew: `brew install openldap`
2. Create virtual environment and `cd` to it

        python3 -m venv ENV
        cd ENV
3. Clone repo to a subdirectory (ex. `git clone REPO_URL src`)
4. Activate virtual environment

        source bin/activate
5. `cd` to new src directory and install requirements

        cd src
        pip install -r requirements.txt

    **NOTE:** if `pip install` returns a block of error text including `fatal error: 'sasl.h' file not found` upon installing `python-ldap`, do the following:

    1. In requirements.txt, comment out the `python-ldap` requirement.
    2. Re-run `pip install -r requirements.txt`.  It should complete successfully.
    3. Run the following, replacing "VERSION" with the version number specified for the `python-ldap` package in requirements.txt:

            pip install python-ldap==VERSION \
            --global-option=build_ext \
            --global-option="-I$(xcrun --show-sdk-path)/usr/include/sasl"

    4. Un-comment the `python-ldap` requirement in requirements.txt and save the file.
6. Set up local settings using the settings_local.templ.py file
7. Set up static_files/static/robots.txt using static_files/static/robots.templ.txt
8. Run the deployment command: `python manage.py deploy`. This runs any migrations and collects the static files.
9. Create a superuser: `python manage.py createsuperuser`
10. If you don't intend on importing any existing calendar data, create a Main Calendar and assign your superuser account as the owner. Otherwise, skip this step

        python manage.py shell
        >>> from django.contrib.auth.models import User
        >>> from events.models import Calendar
        >>> u = User.objects.get(pk=1)
        >>> c = Calendar(title='Events at UCF', owner=u)
        >>> c.save()
        >>> exit()


## Importing Data

### UNL Events Import
Note that this importer should only be run on a fresh database, immediately after running `python manage.py syncdb` or `python manage.py flush`.

**Before running this import, make sure that a new user has been created in Django for every non-NID-based user in the UNL system. These users' events will fail to import otherwise.**

1. cd to the new virtual environment src folder
2. Activate virtual environment

        source ../bin/activate
3. Add old events database information to settings_local.py under DATABASES name 'unlevents'.  Make sure that ENABLE_CLEARCACHE are set to 'False'.
4. Run import command

        python manage.py import-unl-events
5. Restart the app
6. Ban cache as necessary

### Locations Import
1. cd to the new virtual environment src folder
2. Activate virtual environment

        source ../bin/activate
3. Make sure that MAPS_DOMAIN and LOCATION_DATA_URL are set in settings_local.py, and that ENABLE_CLEARCACHE are set to 'False'.
4. Run import command

        python manage.py import-locations
5. Restart the app
6. Ban cache as necessary


## Code Contribution
Never commit directly to master. Create a branch or fork and work on the new feature. Once it is complete it will be merged back to the master branch.

If you use a branch to develop a feature, make sure to delete the old branch once it has been merged to master.


## Development

### Requirements
* node
* gulp-cli

### Gulp Setup
This project uses gulp to handle various tasks, such as compiling and minifying sass files and minifying/uglifying javascript. Use the following steps to setup gulp for this project.

1. Run `npm install` from the root directory to install node packages defined in package.json.
2. Optional: If you'd like to enable [BrowserSync](https://browsersync.io) for local development, or make other changes to this project's default gulp configuration, copy `gulp-config.template.json`, make any desired changes, and save as `gulp-config.json`.
3. Run `gulp default` to install all front-end components and compile static assets.
4. Run `gulp watch` during development to detect static file changes automatically. When a change is detected, minification and compilation commands will run automatically. If you enabled BrowserSync in `gulp-config.json`, it will also reload your browser when scss or js files change.
5. Make sure up-to-date concatenated/minified files (files in `static_files/static/`) are pushed to the repo when making changes to static files.

### Sass

All of the raw custom styles for this project are contained in separate Sass files in `static_files/assets/scss/`. When modifying stylesheets in this project, only modify the files in this directory; **do NOT modify files in `static_files/static/css/` directly**! Sass files compile and write to this directory.

Partial Sass files are generally separated out by function, and must be compiled in a specific order.

### Javascript

#### Concatenation Details
This project combines vendor javascript libraries with our own so fewer files need to be delivered to the client. The list below lays out the basic concatenation/uglification scheme.

* script.min.js
  * ucf-athena-framework/dist/js/framework.min.js - *vendor*
  * script.js - *project*
* script-frontend.min.js
  * script-frontend.js - *project*
* script-manager.min.js
  * jquery.timepicker.js - *vendor*
  * bootstrap-datepicker.js - *vendor*
  * select2.js - *vendor*
  * script-manager.js - *project*

Scripts marked `*vendor*` are retrieved as npm packages and concatenated into project files that include them during gulp processing.

Scripts marked `*project*` are scripts maintained by this project and can found in `static_files/assets/js`.  **Do NOT modify files in `static_files/static/js/` directly**.

#### TinyMCE
In addition to the scripts listed above, the TinyMCE library is copied into its own subdirectory, `static_files/static/js/wysiwyg`, during gulp processing.  TinyMCE, by default, expects its themes, plugins, and skins to be in subdirectories relative to the root directory of the primary TinyMCE script, so we maintain the directory structure as closely as possible while still picking out only the specific plugins/skins/themes needed for the events system to avoid bloat in the repo.

We also apply customizations to the default TinyMCE skin, "lightgray", after its directory finishes copying over from the components directory.  These customizations should be modified in `static_files/assets/scss/content.scss`.

