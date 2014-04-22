# Require any additional compass plugins here.

# Set this to the root of your project when deployed:
http_path = "/"
http_stylesheets_path = "static/css"
http_images_path = "static/img"
http_javascripts_path = "static/js"
http_fonts_path = "static/fonts"

css_dir = "static_files/css"
sass_dir = "static_files/sass"
images_dir = "static_files/img"
javascripts_dir = "static_files/js"
fonts_dir = "static_files/fonts"

output_style = :nested
environment = :development

# To enable relative paths to assets via compass helper functions. Uncomment:
# relative_assets = true

# To disable debugging comments that display the original location of your selectors. Uncomment:
# line_comments = false
color_output = false


# If you prefer the indented syntax, you might want to regenerate this
# project again passing --syntax sass, or you can uncomment this:
# preferred_syntax = :sass
# and then run:
# sass-convert -R --from scss --to sass static/sass scss && rm -rf sass && mv scss sass
preferred_syntax = :scss
