const fs           = require('fs');
const browserSync  = require('browser-sync').create();
const gulp         = require('gulp');
const autoprefixer = require('gulp-autoprefixer');
const cleanCSS     = require('gulp-clean-css');
const include      = require('gulp-include');
const eslint       = require('gulp-eslint');
const isFixed      = require('gulp-eslint-if-fixed');
const babel        = require('gulp-babel');
const rename       = require('gulp-rename');
const sass         = require('gulp-sass');
const sassLint     = require('gulp-sass-lint');
const uglify       = require('gulp-uglify');
const merge        = require('merge');


let config = {
  src: {
    scssPath: './static_files/assets/scss',
    jsPath: './static_files/assets/js'
  },
  dist: {
    cssPath: './static_files/static/css',
    jsPath: './static_files/static/js',
    fontPath: './static_files/static/fonts'
  },
  packagesPath: './node_modules',
  sync: false,
  syncTarget: 'http://127.0.0.1:8000'
};

/* eslint-disable no-sync */
if (fs.existsSync('./gulp-config.json')) {
  const overrides = JSON.parse(fs.readFileSync('./gulp-config.json'));
  config = merge(config, overrides);
}
/* eslint-enable no-sync */


//
// Helper functions
//

// Base SCSS linting function
function lintSCSS(src) {
  return gulp.src(src)
    .pipe(sassLint())
    .pipe(sassLint.format())
    .pipe(sassLint.failOnError());
}

// Base SCSS compile function
function buildCSS(src, dest) {
  dest = dest || config.dist.cssPath;

  return gulp.src(src)
    .pipe(sass({
      includePaths: [config.src.scssPath, config.packagesPath]
    })
      .on('error', sass.logError))
    .pipe(cleanCSS())
    .pipe(autoprefixer({
      // Supported browsers added in package.json ("browserslist")
      cascade: false
    }))
    .pipe(rename({
      extname: '.min.css'
    }))
    .pipe(gulp.dest(dest));
}

// Base JS linting function (with eslint). Fixes problems in-place.
function lintJS(src, dest) {
  dest = dest || config.src.jsPath;

  return gulp.src(src)
    .pipe(eslint({
      fix: true
    }))
    .pipe(eslint.format())
    .pipe(isFixed(dest));
}

// Base JS compile function
function buildJS(src, dest) {
  dest = dest || config.dist.jsPath;

  return gulp.src(src)
    .pipe(include({
      includePaths: [config.packagesPath, config.src.jsPath]
    }))
    .on('error', console.log) // eslint-disable-line no-console
    .pipe(babel())
    .pipe(uglify())
    .pipe(rename({
      extname: '.min.js'
    }))
    .pipe(gulp.dest(dest));
}

// BrowserSync reload function
function serverReload(done) {
  if (config.sync) {
    browserSync.reload();
  }
  done();
}

// BrowserSync serve function
function serverServe(done) {
  if (config.sync) {
    browserSync.init({
      proxy: {
        target: config.syncTarget
      }
    });
  }
  done();
}


//
// Installation of components/dependencies
//

// Bootstrap Glyphicon font processing
gulp.task('move-components-bs-fonts', (done) => {
  gulp.src([`${config.packagesPath}/bootstrap-sass/assets/fonts/bootstrap/*`])
    .pipe(gulp.dest(config.dist.fontPath));
  done();
});

// Font Awesome font processing
gulp.task('move-components-fa-fonts', (done) => {
  gulp.src([`${config.packagesPath}/font-awesome-4/fonts/*`])
    .pipe(gulp.dest(config.dist.fontPath));
  done();
});

// TinyMCE WYSIWYG asset processing
gulp.task('move-components-tinymce', (done) => {
  // Main TinyMCE lib
  gulp.src([`${config.packagesPath}/tinymce/tinymce.min.js`])
    .pipe(gulp.dest(`${config.dist.jsPath}/wysiwyg`));

  // TinyMCE Theme
  gulp.src([`${config.packagesPath}/tinymce/themes/modern/**/*`])
    .pipe(gulp.dest(`${config.dist.jsPath}/wysiwyg/themes/modern/`));

  // TinyMCE Skin
  gulp.src([
    `${config.packagesPath}/tinymce/skins/lightgray/**/*`,
    `!${config.packagesPath}/tinymce/skins/lightgray/content.min.css`
  ])
    .pipe(gulp.dest(`${config.dist.jsPath}/wysiwyg/skins/lightgray/`));

  // TinyMCE Plugins
  gulp.src([`${config.packagesPath}/tinymce/plugins/paste/**/*`])
    .pipe(gulp.dest(`${config.dist.jsPath}/wysiwyg/plugins/paste/`));

  gulp.src([`${config.packagesPath}/tinymce/plugins/link/**/*`])
    .pipe(gulp.dest(`${config.dist.jsPath}/wysiwyg/plugins/link/`));

  gulp.src([`${config.packagesPath}/tinymce/plugins/autoresize/**/*`])
    .pipe(gulp.dest(`${config.dist.jsPath}/wysiwyg/plugins/autoresize/`));

  done();
});

// Run all component-related tasks
gulp.task('components', gulp.parallel(
  'move-components-bs-fonts',
  'move-components-fa-fonts',
  'move-components-tinymce'
));


//
// CSS
//

// Lint all project scss files
gulp.task('scss-lint', () => {
  return lintSCSS(`${config.src.scssPath}/*.scss`);
});

// Compile frontend stylesheet
gulp.task('scss-build-frontend', () => {
  return buildCSS(`${config.src.scssPath}/style.scss`);
});

// Compile backend stylesheet
gulp.task('scss-build-backend', () => {
  return buildCSS(`${config.src.scssPath}/style-backend.scss`);
});

// Compile WYSIWYG content stylesheet
gulp.task('scss-build-wysiwyg-content', () => {
  return buildCSS(
    `${config.src.scssPath}/content.scss`,
    `${config.dist.jsPath}/wysiwyg/skins/lightgray`
  );
});

// All theme css-related tasks
gulp.task('css', gulp.series('scss-lint', 'scss-build-frontend', 'scss-build-backend', 'scss-build-wysiwyg-content'));


//
// JavaScript
//

// Run eslint on js files in src.jsPath
gulp.task('es-lint', () => {
  return lintJS([`${config.src.jsPath}/*.js`], config.src.jsPath);
});

// Concat and uglify global js files through babel
gulp.task('js-build-global', () => {
  return buildJS(`${config.src.jsPath}/script.js`, config.dist.jsPath);
});

// Concat and uglify frontend js files through babel
gulp.task('js-build-frontend', () => {
  return buildJS(`${config.src.jsPath}/script-frontend.js`, config.dist.jsPath);
});

// Concat and uglify backend js files through babel
gulp.task('js-build-backend', () => {
  return buildJS(`${config.src.jsPath}/script-manager.js`, config.dist.jsPath);
});

// All js-related tasks
gulp.task('js', gulp.series('es-lint', 'js-build-global', 'js-build-frontend', 'js-build-backend'));


//
// Rerun tasks when files change
//
gulp.task('watch', (done) => {
  serverServe(done);

  gulp.watch(`${config.src.scssPath}/**/*.scss`, gulp.series('css', serverReload));
  gulp.watch(`${config.src.jsPath}/**/*.js`, gulp.series('js', serverReload));
});


//
// Default task
//
gulp.task('default', gulp.series('components', 'css', 'js'));
