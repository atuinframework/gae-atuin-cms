// Linked sections management - Admin Atuincms

var bindMediaLinkedSectionsAdmin = function () {
	$('#linked_section').autoComplete({
		resolver: 'custom',
		formatResult: function (item) {
			return {
				value: item['value'],
				text: item['section_name'] + ' | ' + item['section_path'],
				html: [
					$('<b>').text(item['section_name']).css('font-size', '1.2em'),
					'<br>',
					item['section_path']
				]
			};
		},
		events: {
			search: function (qry, callback) {
				// let's do a custom ajax call
				$.ajax(
					$('#linked_section_search').data('url'),
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
	$('.btnAcmsPickLinkedSection').on('click', function () {
		var btn = $(this),
			form = $('#linkedSectionForm');

		linked_section_url = btn.closest('.acmsLinkedSectionPanel').data('url');
		form.formtools('reset');
		form.attr('action', linked_section_url);

		btn.button('loading');
		$.ajax(
			linked_section_url
		)
			.done(function (res) {
				if (res['exists']) {
					$('#linked_section').autoComplete('set', res);
				}
				$('#linkedSectionModal').modal('show');
				$('#linkedSectionModal').on('shown.bs.modal', function () {
					$('#linked_section').focus();
				});
			})
			.fail(function (err) {
				alert('Error on get linked section');
			})
			.always(function () {
				btn.button('reset');
			});
	});

	$('#linkedSectionForm').on('submit', function () {
		$('#linkedSectionForm .btnSave').trigger('click');
		return false;
	});

	$('#linkedSectionModal .btnSave').on('click', function () {
		var btn = $(this),
			form = $('#linkedSectionForm');

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
					alert('Error on linked section save');
				}

			})
			.fail(function (err) {
				alert('Error on linked section save');
				btn.button('reset');
			});

		return false;
	});

	$('.btnAcmsDeleteLinkedSection').click(function () {
		var btn = $(this);

		url = btn.closest('.acmsLinkedSectionPanel').data('url');
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
						alert('Error deleting linked section');
					}
				})
				.fail(function () {
					btn.button('reset');
					alert('Error deleting linked section');
				});

		}
		return false;
	});
};
