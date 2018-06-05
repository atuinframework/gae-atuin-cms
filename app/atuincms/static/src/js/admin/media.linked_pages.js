// Linked pages management - Admin Atuincms

var bindMediaLinkedPagesAdmin = function () {
	$('#linked_page').autoComplete({
		resolver: 'custom',
		formatResult: function (item) {
			return {
				value: item['value'],
				text: item['page_name'] + ' | ' + item['page_url'],
				html: [
					$('<b>').text(item['page_name']).css('font-size', '1.2em'),
					'<br>',
					item['page_url']
				]
			};
		},
		events: {
			search: function (qry, callback) {
				// let's do a custom ajax call
				$.ajax(
					$('#linked_page_search').data('url'),
					{
						data: {'q': qry}
					}
				).done(function (res) {
					callback(res.results)
				});
			}
		}
	});

	// new or edit linked page
	$('.btnAcmsPickLinkedPage').on('click', function () {
		var btn = $(this),
			form = $('#linkedPageForm');

		linked_page_url = btn.closest('.acmsLinkedPagePanel').data('url');
		form.formtools('reset');
		form.attr('action', linked_page_url);

		btn.button('loading');
		$.ajax(
			linked_page_url
		)
			.done(function (res) {
				if (res['exists']) {
					$('#linked_page').autoComplete('set', res);
				}
				$('#linkedPageModal').modal('show');
				$('#linkedPageModal').on('shown.bs.modal', function () {
					$('#linked_page').focus();
				});
			})
			.fail(function (err) {
				alert('Error on get linked page');
			})
			.always(function () {
				btn.button('reset');
			});
	});

	$('#linkedPageForm').on('submit', function () {
		$('#linkedPageForm .btnSave').trigger('click');
		return false;
	});

	$('#linkedPageModal .btnSave').on('click', function () {
		var btn = $(this),
			form = $('#linkedPageForm');

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
						window.location.reload();
					}, timeToRefresh);
				} else {
					alert('Error on linked page save');
				}

			})
			.fail(function (err) {
				alert('Error on linked page save');
				btn.button('reset');
			});

		return false;
	});

	$('.btnAcmsDeleteLinkedPage').click(function () {
		var btn = $(this);

		url = btn.closest('.acmsLinkedPagePanel').data('url');
		msg = _t('Do you really want to delete this item?\n\nWARNING: this operation cannot be undone.');

		if (confirm(msg)) {
			btn.button('loading');
			$.ajax(
				url,
				{method: 'DELETE'}
			)
				.done(function (res) {
					if (res['result'] == 'ok') {
						setTimeout(function () {
							window.location.reload();
						}, timeToRefresh);
					} else {
						alert('Error deleting linked page');
					}
				})
				.fail(function () {
					btn.button('reset');
					alert('Error deleting linked page');
				});

		}
		return false;
	});
};
