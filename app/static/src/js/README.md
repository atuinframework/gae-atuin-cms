## Project scripts
These javascript will be minified and optimized for better performance on page loading.

Attention: `public scripts` are distinguished from `admin scripts`

### Create a script file for one section
For every site section creates a file with the same name.
If it's a pubblic script, place it in `static/src/js`.
Else if it's an admin script, place it in `static/src/js/admin`.

The file must have the following structure:
```javascript
window.init_example_section = function() {

	/* All the code for this section goes here... */

}
```

To make work properly the script add the relative init function in the right `main.js` file (admin or public).
```javascript
$(function () {
	/*
	 * Template:
	 *
	 * $('html.example_section').each(function () {
	 * 	// call initialization function
	 * 	init_example_section()
	 * });
	 */
});

```

### Destinations
The concatenated and minified javascript file will be put here:

- **Public scripts** `/static/min/js/all.js`
This directory is public

- **Admin scripts** `/static/min/js/admin/all.js`
This directory could be secured through deployment or webserver configuration
