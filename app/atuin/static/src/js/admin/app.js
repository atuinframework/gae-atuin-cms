$(function () {
	/*
	 * Template for binding functions to context.
	 */
	/*
	$('html.admin.dashboard').each(function () {
		...
	});
	*/
	$('html.admin.users').each(function () {
		bindAdminUsers();
	});


	//window.modalAlert = initialize_custom_alert("#modalAlert");
});
