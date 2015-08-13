var gulp = require('gulp'),
  sass = require('gulp-sass'),
  minifyCss = require('gulp-minify-css'),
  bless = require('gulp-bless'),
  notify = require('gulp-notify'),
  bower = require('gulp-bower'),
  concat = require('gulp-concat'),
  uglify = require('gulp-uglify'),
  rename = require('gulp-rename'),
  jshint = require('gulp-jshint'),
  jshintStylish = require('jshint-stylish'),
  scsslint = require('gulp-scss-lint'),
  vinylPaths = require('vinyl-paths');
  // browserSync = require('browser-sync').create(),
  // reload = browserSync.reload;

var config = {
  sassPath: './static_files/assets/scss',
  cssPath: './static_files/static/css',
  jsPath: './static_files/assets/js',
  jsMinPath: './static_files/static/js',
  fontPath: './static_files/static/fonts',
  bowerDir: './static_files/assets/components'
};

gulp.task('bower', function() {
  bower()
    .pipe(gulp.dest(config.bowerDir))
    .on('end', function() {
      // Copy gylphicon font files out to config.fontPath
      gulp.src(config.bowerDir + '/bootstrap-sass-official/assets/fonts/bootstrap/*')
        .pipe(gulp.dest(config.fontPath));

      // Copy fontawesome font files out to config.fontPath
      gulp.src(config.bowerDir + '/font-awesome/fonts/*')
        .pipe(gulp.dest(config.fontPath));
    });
});

gulp.task('css', function() {
  // style.min.css
  gulp.src(config.sassPath + '/*.scss')
    .pipe(scsslint())
    .pipe(sass().on('error', sass.logError))
    .pipe(minifyCss({compatibility: 'ie8'}))
    .pipe(rename('style.min.css'))
    .pipe(bless())
    .pipe(gulp.dest(config.cssPath));
    //.pipe(browserSync.stream());

  // style-backend.min.css
  gulp.src([
    config.bowerDir + '/jquery-timepicker-jt/jquery.timepicker.css',
    config.bowerDir + '/bootstrap-datepicker/dist/css/bootstrap-datepicker3.css',
    config.bowerDir + '/bootstrap3-wysihtml5-bower/dist/bootstrap3-wysihtml5.css'
  ])
    .pipe(minifyCss({compatibility: 'ie8'}))
    .pipe(concat('style-backend.min.css'))
    .pipe(bless())
    .pipe(gulp.dest(config.cssPath));
});

gulp.task('js', function() {
  // lint scripts in config.jsPath
  gulp.src([config.jsPath + '/*.js', '!' + config.jsPath + '/*.min.js'])
    .pipe(jshint())
    .pipe(jshint.reporter('jshint-stylish'))
    .pipe(jshint.reporter('fail'));

  // script.min.js
  gulp.src([
    config.bowerDir + '/jquery-placeholder/jquery.placeholder.js',
    config.bowerDir + '/bootstrap-sass-official/assets/javascripts/bootstrap.js',
    config.jsPath + '/script.js'
  ])
    .pipe(concat('script.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest(config.jsMinPath));

  // script-frontend.min.js
  gulp.src(config.jsPath + '/script-frontend.js')
    .pipe(rename('script-frontend.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest(config.jsMinPath));

  // script-backend.min.js
  gulp.src([
    config.bowerDir + '/bootstrap3-typeahead/bootstrap3-typeahead.js',
    config.bowerDir + '/jquery-timepicker-jt/jquery.timepicker.js',
    config.bowerDir + '/bootstrap-datepicker/dist/js/bootstrap-datepicker.js',
    config.jsPath + '/script-manager.js'
  ])
    .pipe(concat('script-manager.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest(config.jsMinPath));

  // wysiwyg.min.js
  gulp.src([
    config.bowerDir + '/wysihtml5/dist/wysihtml5-0.3.0.js',
    config.bowerDir + '/bootstrap3-wysihtml5-bower/dist/bootstrap3-wysihtml5.js'
  ])
    .pipe(concat('wysiwyg.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest(config.jsMinPath));
});

gulp.task('watch', function() {
  gulp.watch(config.sassPath + '/*.scss', ['css']);
  gulp.watch(config.jsPath + '/*.js', ['js']);
});

gulp.task('default', ['bower', 'css', 'js']);
