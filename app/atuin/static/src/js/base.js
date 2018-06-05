// Base generic utilities

/**
 * jQuery hack to add case insensitive contains() selector named :icontains
 */
jQuery.expr[":"].icontains = jQuery.expr.createPseudo(function (arg) {
	return function (elem) {
		return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
	};
});


/**
 * Time to refresh is a shared time interval used to delay the page refresh after a datastore entity update.
 */
timeToRefresh = 1000;


$('.btnLogin').on('click', function () {
	$('#loginForm').submit();
	return false;
});

$('#loginForm input').on('keyup', function (ev) {
	var code = ev.which;
	if (code == 13) {
		$('#loginForm').submit();
	}
});

$('.panel-link').on('click', function () {
	window.location = $(this).attr('href');
});


