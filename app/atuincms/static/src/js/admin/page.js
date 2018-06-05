var bindPageAdmin = function () {
	$('#editPageAdmin').on('submit', function () {
		$('#editPageAdmin .btnSavePageInfo').trigger('click');
		return false;
	});

	$('#editPageAdmin .btnSavePageInfo').on('click', function () {
		var btn = $(this),
			form = $('#editPageAdmin');

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
						alert('Error on page information save');
					}
				})
				.fail(function (err) {
					alert('Error on page information save');
					btn.button('reset');
				});
		}
		return false;
	});

	function createOptions(sections, depth, select) {
		if (!sections) {
			return;
		}

		$.each(sections, function (i, s) {
			dashes = Array(depth + 1).join('— ');

			select.append($('<option>').val(s.key_us).text(dashes + s['name']));
			createOptions(s.subs, depth + 1, select);
		});

		return;
	}

	function fillSectionsSelect() {
		select = $('#parentSection');
		spinner = $('#treeLoadingSpinner');

		$.ajax(
			select.data('tree')
		)
			.done(function (res) {
				select.html('');
				select.append($('<option>').val('/').text(_t('** Root **')));
				createOptions(res.results, 0, select)

				select.val(select.data('value'));
				spinner.detach();
			})
			.fail(function (err) {
				alert('Error on sections tree loading');
			});
	}

	fillSectionsSelect();


	$('.modLang').click(function () {
		var btn = $(this),
			form = $('#pageLangForm'),
			lang = btn.data('language');

		pageInfoUrl = $('.acmsPageInfo').data('url');

		form.attr('action', pageInfoUrl);

		// no cached data, do the request
		$.ajax(pageInfoUrl)
			.done(function (res) {
				goToShowPageModal(res, lang);
			})
			.fail(function (err) {
				alert('Error on get page data');
			});
		return false;
	});


	function goToShowPageModal(res, lang) {
		var form = $('#pageLangForm'),
			modal = $('#pageLangModal'),
			descriptions = res['descriptions'];

		local_data = descriptions[current_language];
		if (!local_data) {
			// get firs elem available
			local_data = descriptions[Object.keys(descriptions)[0]];
		}
		trans_data = descriptions[lang];

		// ad the current translated language to the form input field
		$('#language').val(lang);
		form.formtools('reset', trans_data);

		modal.find('.defaultLangTitle p').text(local_data['name']);
		modal.find('.defaultLangDescription p').text(local_data['description']);

		modal.find('#nameLang').text(languages[lang]);
		modal.find('#flagLangIcon').attr('class', '');
		modal.find('#flagLangIcon').addClass('flag-icon flag-icon-' + lang);
		modal.find('#flagLangIcon').attr('title', languages[lang]);

		modal.modal('show');
	}

	$('#pageLangForm').on('submit', function () {
		$('#pageLangForm .btnSave').trigger('click');
		return false;
	});

	$('#pageLangModal .btnSave').on('click', function () {
		var btn = $(this),
			form = $('#pageLangForm');

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
					}
				})
				.fail(function (err) {
					alert('Error on page data saving');
					btn.button('reset');
				});
		}
		return false;
	});

	$('#editPageAdmin .btnDeletePage').on('click', function () {
		var btn = $(this);

		url = btn.data('url');

		msg = _t('Do you really want to delete this item?\n\nWARNING: this operation cannot be undone.');
		if (confirm(msg)) {
			btn.button('loading');
			$.ajax(url, {method: 'DELETE'})
				.done(function (res) {
					if (res['result'] == 'ok') {
						setTimeout(function () {
							window.location.href = res['url'];
						}, timeToRefresh);
					} else {
						alert('Error deleting page');
					}
				})
				.fail(function (err) {
					alert('Error deleting page');
					btn.button('reset');
				});
		}
		return false;
	});
};
