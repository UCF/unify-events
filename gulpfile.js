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
	vinylPaths = require('vinyl-paths'),
	del = require('del'),
	browserSync = require('browser-sync').create(),
	reload = browserSync.reload;

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
			var unneededFiles = [
				config.bowerDir + '/**/*.html',
				config.bowerDir + '/**/*.txt',
				config.bowerDir + '/**/LICENSE',
				config.bowerDir + '/**/*.md',
				config.bowerDir + '/**/*.markdown',
				config.bowerDir + '/**/.*',
				config.bowerDir + '/**/Makefile',
				config.bowerDir + '/**/README'
			];

			gulp.src(unneededFiles)
				.pipe(vinylPaths(del));

			gulp.src(config.bowerDir + '/bootstrap-sass-official/assets/fonts/bootstrap/*')
				.pipe(gulp.dest(config.fontPath));

			gulp.src(config.bowerDir + '/font-awesome/fonts/*')
				.pipe(gulp.dest(config.fontPath));
		});
});

gulp.task('css', function() {
	gulp.src(config.sassPath + '/*.scss')
		.pipe(scsslint())
		.pipe(sass().on('error', sass.logError))
		.pipe(minifyCss({compatibility: 'ie8'}))
		.pipe(rename('style.min.css'))
		.pipe(bless())
		.pipe(gulp.dest(config.cssPath))
		.pipe(browserSync.stream());
});

gulp.task('js', function() {
	gulp.src([config.jsPath + '/*.js', '!' + config.jsPath + '/*.min.js'])
		.pipe(jshint())
		.pipe(jshint.reporter('jshint-stylish'))
		.pipe(jshint.reporter('fail'));

	gulp.src(config.jsPath + '/script.js')
		.pipe(concat('script.min.js'))
		.pipe(uglify())
		.pipe(gulp.dest(config.jsMinPath));

	gulp.src(config.jsPath + '/script-frontend.js')
		.pipe(concat('script-frontend.min.js'))
		.pipe(uglify())
		.pipe(gulp.dest(config.jsMinPath));

	gulp.src(config.jsPath + '/script-manager.js')
		.pipe(concat('script-manager.min.js'))
		.pipe(uglify())
		.pipe(gulp.dest(config.jsMinPath));

	gulp.src(config.bowerDir + '/bootstrap-sass-official/assets/javascripts/bootstrap.min.js')
		.pipe(gulp.dest(config.jsMinPath));
});

gulp.task('watch', function() {
	gulp.watch(config.sassPath + '/*.scss', ['css']);
	gulp.watch(config.jsPath + '/*.js', ['js']);
});

gulp.task('default', ['bower', 'css', 'js']);
