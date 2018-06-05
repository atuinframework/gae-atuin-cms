var bindPageNewAdmin = function () {
	$("#template").on("change", function (e) {
		tpl_url = $(this).find(":selected").data('src');
		$('.tplPreview img').attr('src', tpl_url);
	});
	$("#template").trigger('change');


	$('#newPageForm').on('submit', function () {
		$('#newPageForm .btnSaveNewPage').trigger('click');
		return false;
	});

	$('#newPageForm .btnSaveNewPage').on('click', function () {
		var btn = $(this),
			form = $('#newPageForm');

		if (form.formtools('validate')) {
			btn.button('loading');
			$.ajax(
				form.attr('action'),
				{
					data: form.serialize(),
					method: 'POST'
				}
			)
				.done(function (res) {
					if (res['result'] == 'ok') {
						setTimeout(function () {
							window.location.href = res['url'];
						}, timeToRefresh);
					} else {
						alert('Error on page save');
					}
				})
				.fail(function (err) {
					alert('Error on page save');
					btn.button('reset');
				});
		}
		return false;
	});
};
