$(document).ready(function () {
	var atuinFlashMessageDisappearTimeLatency = 5000;
	var atuinFlashMessageDisappearTimeDelay = 0;
	$('.atuinFlashMessagesAdmin .alert').each(function (i, alert) {
		atuinFlashMessageDisappearTimeDelay += atuinFlashMessageDisappearTimeLatency;
		setTimeout(function () {
			$(alert).slideUp();
		}, atuinFlashMessageDisappearTimeDelay);
	});
});