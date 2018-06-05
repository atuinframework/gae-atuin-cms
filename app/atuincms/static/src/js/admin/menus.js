// Menus - Admin Atuincms menus management

var bindMenusAdmin = function () {
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

	function createOptions(menus, depth, select, disabled, go_on_disabling) {
		var t = '';

		if (!menus) {
			return;
		}

		$.each(menus, function (i, m) {
			dashes = Array(depth + 1).join('— ');

			opt = $('<option>').val(m.key_us).text(dashes + m['name']);
			if (disabled == m.key_us || go_on_disabling) {
				opt.attr('disabled', true)
				select.append(opt);
				createOptions(m.subs, depth + 1, select, disabled, true);
			} else {
				select.append(opt);
				createOptions(m.subs, depth + 1, select, disabled);
			}
		});
		return;
	}


	/**
	 * Menu
	 */
	$('.btnNewMenu').on('click', function () {
		var btn = $(this),
			form = $('#menuForm'),
			select = $('#parent_menu');

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

				$('#menuModal').find('.modal-title').text(_t('Nuovo menu'));
				$('#menuModal').modal('show');
				$('#menuModal').on('shown.bs.modal', function () {
					$('#parent_menu').focus();
				});
			})
			.fail(function (err) {
				alert('Error on get menu tree');
			})
			.always(function () {
				btn.button('reset');
			});
	});

	$('body').on('click', '.btnEditMenu', function () {
		var btn = $(this),
			li = btn.closest('li'),
			form = $('#menuForm'),
			select = $('#parent_menu');


		form.formtools('reset');
		form.attr('action', btn.data('url'));

		btn.button('loading');
		$.ajax(
			$('.btnNewMenu').data('tree')
		)
			.done(function (res) {
				select.html('');
				select.append($('<option>').val('/').text(_t('** Root **')));
				// disable the self key
				disabled = btn.closest('.menu').data('key-us');
				createOptions(res.results, 0, select, disabled);

				// Load the menu object
				$.ajax(
					li.data('menu-url')
				)
					.done(function (d) {
						form_data = d['descriptions'][current_language];
						if (!form_data) {
							form_data = d['descriptions'][Object.keys(d['descriptions'])[0]];
						}
						form_data['parent_menu'] = d['parent_menu'];

						form.formtools('reset', form_data);

						// set the default value into the select
						if (d['linked_page'] != '') {
							$('#linked_page').autoComplete('set',
								{
									value: d['linked_page'],
									page_name: d['linked_page_name'],
									page_url: d['linked_page_url']
								}
							);
						}

						$('#menuModal').find('.modal-title').text(_t('Modifica menu'));
						$('#menuModal').modal('show');
						$('#menuModal').on('shown.bs.modal', function () {
							$('#parent_menu').focus();
						});

					})
					.fail(function (err) {
						alert('Error on get menu in menu edit');
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

	$('#menuForm').on('submit', function () {
		$('#menuModal .btnSave').trigger('click');
		return false;
	});

	$('#menuModal .btnSave').on('click', function () {
		var btn = $(this),
			form = $('#menuForm');

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
						alert('Error on menu');
					}

				})
				.fail(function (err) {
					alert('Error on menu');
					btn.button('reset');
				});
		}

		return false;
	});

	/** Expand and inject submenus after clicked menu **/
	$('body').on('click', '.getSubmenus', function () {
		var a = $(this),
			li = a.closest('li');

		submenuUl = li.children('ul');

		if (submenuUl.length > 0) {
			submenuUl.detach();
		} else {
			li.append('<i class="fa fa-spinner fa-spin"></i> ');

			$.ajax(
				a.data('sub-menus'),
				{
					method: 'GET'
				}
			)
				.done(function (res) {
					li.append(res);
					updateShiftMenuBtns();
				})
				.fail(function (err) {
					alert('Error on get sub menus');
				})
				.always(function () {
					$('i.fa.fa-spinner.fa-spin').detach();
				});
		}

		return false;
	});


	/** Modify language **/
	$('body').on('click', '.modLang', function () {
		var form = $('#menuLangForm'),
			li = $(this).closest('li');
		li.data('translatingLang', $(this).data('language'));

		form.attr('action', li.data('language-url'));
		form.data('li', li);

		if (li.data('data_cache')) {
			goToShowModal(li);
		} else {
			// no cached data, do the request
			$.ajax(
				li.data('menu-url')
			)
				.done(function (menu_data) {
					li.data('data_cache', menu_data);
					goToShowModal(li);
				})
				.fail(function (err) {
					alert('Error on get menu in language edit');
				});
		}
		return false;
	});

	function goToShowModal(li) {
		var form = $('#menuLangForm'),
			modal = $('#menuLangModal'),
			menu_data = li.data('data_cache'),
			translatingLang = li.data('translatingLang');

		menu_localized = menu_data['descriptions'][current_language];
		if (!menu_localized) {
			// get firs elem available
			menu_localized = menu_data['descriptions'][Object.keys(menu_data['descriptions'])[0]];
		}
		menu_translation = menu_data['descriptions'][translatingLang];

		// ad the current translated language to the form input field
		$('#language').val(translatingLang);
		form.formtools('reset', menu_translation);

		modal.find('.defaultLangTitle p').text(menu_localized['name']);
		modal.find('.defaultLangDescription p').text(menu_localized['description']);

		modal.find('#nameLang').text(languages[translatingLang]);
		modal.find('#flagLangIcon').attr('class', '');
		modal.find('#flagLangIcon').addClass('flag-icon flag-icon-' + translatingLang);
		modal.find('#flagLangIcon').attr('title', languages[translatingLang]);

		modal.modal('show');
	}

	$('#menuLangForm').on('submit', function () {
		$('#menuLangModal .btnSave').trigger('click');
		return false;
	});

	$('#menuLangModal .btnSave').on('click', function () {
		var btn = $(this),
			form = $('#menuLangForm');

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
					if (res) {
						var li = form.data('li'),
							lang = li.data('translatingLang');
						li.data('data_cache', null);

						if (lang == current_language) {
							li.children('.getSubmenus').text(form.find('#name').val());
						}
						li.find('.flag-icon-' + lang).first().removeClass('noLang');
					}
				})
				.fail(function (err) {
					alert('Error on menu language');
				})
				.always(function () {
					btn.button('reset');
				});

			$('#menuLangModal').modal('hide');
		}

		return false;
	});


	$('body').on('click', '.btnShiftMenu', function () {
		var btn = $(this),
			dir_up = btn.find('.fa').hasClass('fa-arrow-up'),
			url = $('.menusList').data('menu-switch'),
			menu_li, menu_target_li;

		if (dir_up) {
			menu_li = btn.closest('li');
			menu_target_li = btn.closest('li').prev();

		} else {
			menu_li = btn.closest('li');
			menu_target_li = btn.closest('li').next();
		}

		url = url
			.replace('CAT_KEY_US', menu_li.data('key-us'))
			.replace('CAT_KEY_US_TARGET', menu_target_li.data('key-us'));

		btn.button('loading');
		$.ajax(
			url, {method: 'POST'}
		)
			.done(function (res) {
				if (res == 'OK') {
					// update order number
					var menu_on = parseInt(menu_li.find('.menuOrder').text()),
						menu_target_on = parseInt(menu_target_li.find('.menuOrder').text());

					if (menu_on == menu_target_on) {
						menu_target_on++;
					} else {
						t = menu_on;
						menu_on = menu_target_on;
						menu_target_on = t;
					}
					menu_li.find('.menuOrder').text(menu_on);
					menu_target_li.find('.menuOrder').text(menu_target_on);


					// update position
					if (dir_up) {
						menu_target_li.before(menu_li.detach());
					} else {
						menu_li.before(menu_target_li.detach());
					}
				} else {
					alert('Error on menu switch');
				}
			})
			.fail(function (err) {
				alert('Error on menu switch');
			})
			.always(function () {
				btn.button('reset');
				setTimeout(updateShiftMenuBtns, 10);
			});

	});

	function updateShiftMenuBtns() {
		// re enable all arrows
		$('.menusList').find('button[disabled=disabled]').removeAttr('disabled');

		$('.menusList').find('ul').each(function (i, o) {
			var ul = $(o);

			// diasable first up and last down
			ul.find('> li > button > .fa-arrow-up').first().closest('button').attr('disabled', 'disabled');
			ul.find('> li > button > .fa-arrow-down').last().closest('button').attr('disabled', 'disabled');
		});
	}

	updateShiftMenuBtns();

	// $('body').on('click', '.btnDeleteCategory', function () {
	// 	var btn = $(this);
	//
	// 	// confirm
	// 	if (!window.confirm("SICURO???? Non potrai piu' tornare indietro!!!")) {
	// 		return;
	// 	}
	// 	statefulBtn(btn, 'loading');
	// 	$.ajax(
	// 		btn.attr('href'),
	// 		{ method: 'DELETE' }
	// 	)
	// 	.done(function (res) {
	// 		if (res.res == 'KO') {
	// 			// Error
	// 			window.alert(res.error);
	// 			statefulBtn(btn, 'reset');
	// 		} else {
	// 			// OK - remove it
	// 			btn.closest('li').fadeOut();
	// 		}
	// 	});
	// });

};
