// Sections - Admin Atuincms sections management

var bindSectionsAdmin = function () {
	function createOptions(sections, depth, select, disabled, go_on_disabling) {
		var t = '';

		if (!sections) {
			return;
		}

		$.each(sections, function (i, s) {
			dashes = Array(depth + 1).join('— ');

			opt = $('<option>').val(s.key_us).text(dashes + s.name);
			if (disabled == s.key_us || go_on_disabling) {
				opt.attr('disabled', true)
				select.append(opt);
				createOptions(s.subs, depth + 1, select, disabled, true);
			} else {
				select.append(opt);
				createOptions(s.subs, depth + 1, select, disabled);
			}
		});
		return;
	}

	$('.btnNewSection').on('click', function () {
		var btn = $(this),
			form = $('#sectionForm'),
			select = $('#parent_section');

		form.formtools('reset');
		form.attr('action', btn.data('url'));

		btn.button('loading');
		$.ajax(
			btn.data('tree')
		)
			.done(function (res) {
				select.html('');
				select.append($('<option>').val('/').text(_t('** Root **')));
				createOptions(res.results, 0, select);

				$('#sectionModal').modal('show');
				$('#sectionModal').on('shown.bs.modal', function () {
					$('#parent_section').focus();
				});
			})
			.fail(function (err) {
				alert('Error on get menu tree');
			})
			.always(function () {
				btn.button('reset');
			});
	});

	$('body').on('click', '.btnEditSection', function () {
		var btn = $(this),
			li = btn.closest('li'),
			form = $('#sectionForm'),
			select = $('#parent_section');


		form.formtools('reset');
		form.attr('action', btn.data('url'));

		btn.button('loading');
		$.ajax(
			$('.btnNewSection').data('tree')
		)
			.done(function (res) {
				select.html('');
				select.append($('<option>').val('/').text(_t('** Root **')));
				// disable the self key
				disabled = btn.closest('.section').data('key-us');
				createOptions(res.results, 0, select, disabled);

				// Load the section object
				$.ajax(
					li.data('section-url')
				)
					.done(function (d) {
						form_data = d['descriptions'][current_language];
						if (!form_data) {
							form_data = d['descriptions'][Object.keys(d['descriptions'])[0]];
						}
						form_data['parent_section'] = d['parent_section'];

						form.formtools('reset', form_data);

						$('#sectionModal').modal('show');
						$('#sectionModal').on('shown.bs.modal', function () {
							$('#parent_section').focus();
						});

					})
					.fail(function (err) {
						alert('Error on get section in section edit');
					})
					.always(function () {
						btn.button('reset');
					});

			})
			.fail(function (err) {
				alert('Error on get menu tree');
			})
			.always(function () {
				btn.button('reset');
			});

	});

	$('#sectionForm').on('submit', function () {
		$('#sectionModal .btnSave').trigger('click');
		return false;
	});

	$('#sectionModal .btnSave').on('click', function () {
		var btn = $(this),
			form = $('#sectionForm');

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
					// update - res is json
					if (res == 'ok') {
						setTimeout(function () {
							window.location.reload();
						}, timeToRefresh);
					} else {
						alert('Error on section');
					}

				})
				.fail(function (err) {
					alert('Error on section');
					btn.button('reset');
				});
		}

		return false;
	});

	/** Expand and inject submenus after clicked menu **/
	$('body').on('click', '.getSubsections', function () {
		var a = $(this),
			li = a.closest('li');

		subsectionUl = li.children('ul');

		if (subsectionUl.length > 0) {
			subsectionUl.detach();
		} else {
			li.append('<i class="fa fa-spinner fa-spin"></i> ');

			$.ajax(
				a.data('sub-sections'),
				{
					method: 'GET'
				}
			)
				.done(function (res) {
					li.append(res);
				})
				.fail(function (err) {
					alert('Error on get sub sections');
				})
				.always(function () {
					$('i.fa.fa-spinner.fa-spin').detach();
				});
		}

		return false;
	});


	$('body').on('click', '.btnDeleteSection', function () {
		var btn = $(this);

		url = btn.data('url');

		msg = _t('Do you really want to delete this item?\nAll nested pages will not be deleted.\n\nWARNING: this operation cannot be undone.');
		if (confirm(msg)) {
			btn.button('loading');
			$.ajax(url, {method: 'DELETE'})
				.done(function (res) {
					// update - res is json
					if (res == 'ok') {
						setTimeout(function () {
							window.location.reload();
						}, timeToRefresh);
					} else {
						alert('Error deleting section');
					}
				})
				.fail(function (err) {
					alert('Error deleting section');
					btn.button('reset');
				});
		}
		return false;
	});
};
