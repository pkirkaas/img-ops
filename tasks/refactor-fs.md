# Refactor and re-implement some functions in file_system.py

## funtion filter_imgs

- The function filter_imgs declares a local variable `default_image_extensions`
- Take that variable out of the local scope of the filter_imgs function so it is available to other functions - like a new `valid_img_path` function (defined below)
- The filter_imgs function accepts 3 parameters - a list of paths, boolean case_sensitive, and list of custom_extensions
- Let's remove the last two parameters - we don't need to add custom extensions, and we can assume that the case of the file extension is case-insensitve - both '.jpg' & '.JPG' are valid image extensions.


## Create function is_image_path 
## Simplify filter_imgs