// Home template

var bindHome = function () {
	$(document).ready(function () {
		console.log('GAE Atuin CMS: Home page template');
	});

};
$(function () {
	/*
	 * Template:
	 *
	 * $('html.example_section').each(function () {
	 * 	// call initialization function
	 * 	init_example_section()
	 * });
	 */

	$('html.home').each(function () {
		bindHome();
	});

});
