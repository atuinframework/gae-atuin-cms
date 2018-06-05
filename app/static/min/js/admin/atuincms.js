$(function () {
	/*
	 * Template:
	 *
	 * $('html.example_section').each(function () {
	 * 	// call initialization function
	 * 	init_example_section()
	 * });
	 */

	$('html.admin.cms.menus').each(function () {
		bindMenusAdmin();
	});
	$('html.admin.cms.sections').each(function () {
		bindSectionsAdmin();
	});
	$('html.admin.cms.pageNew').each(function () {
		bindPageNewAdmin();
	});
	$('html.admin.cms.page').each(function () {
		bindPageAdmin();
		bindMediaTextsAdmin();
		bindMediaImagesAdmin();
		bindMediaLinkedPagesAdmin();
		bindMediaLinkedSectionsAdmin();
	});
});
// Images management - Admin Atuincms

var bindMediaImagesAdmin = function () {
	/* UPLOAD */
	var btnBrowse = $('#btnBrowseImages'),
		progressbar = $('#imageUploadModal .progress-bar'),
		pending_upload_url_requests = 0,
		acmsImagePanel;

	$('.btnAcmsImageUpload').click(function () {
		var btn = $(this),
			btnBrws = $('#btnBrowseImages');

		btnBrws.data('get-upload-url', btn.data('get-upload-url'));
		acmsImagePanel = btn.closest('.acmsImagePanel');

		$('#imageUploadModal').modal('show');
	});

	var getUploadUrl = function (cbk) {
		$.ajax(
			btnBrowse.data('get-upload-url') + '&_=' + new Date().getTime() // to force browsers not to cache the response
		)
			.done(function (res) {
				if (res['result'] == 'ok') {
					cbk(res['url']);
				}
			})
			.fail(function () {
				alert('Error handshaking an upload URL');
			});
	};

	var uploader = new plupload.Uploader({
		runtimes: 'html5,html4',
		browse_button: btnBrowse.get(0),
		file_data_name: 'upload',
		multipart_params: {},
		filters: {
			// Maximum file size
			max_file_size: '5mb',
			// Specify what files to browse for
			mime_types: [
				{title: "Images files", extensions: "jpg,jpeg,gif,png"}
			]
		},
		multi_selection: false,
	});

	uploader.bind("FilesAdded", function (uploader, files) {
		$.each(files, function (idx, file) {
			pending_upload_url_requests += 1;
			getUploadUrl(function (url) {
				file.url = url;
				pending_upload_url_requests -= 1;
				if (pending_upload_url_requests === 0) {
					uploader.start();
				}
			});
		});
		btnBrowse.addClass('hidden');
		progressbar.closest('.progress').removeClass('hidden');
	});

	uploader.bind("BeforeUpload", function (uploader, file) {
		uploader.settings.url = file.url;
	});

	uploader.bind("UploadProgress", function (uploader, file) {
		if (file.percent > 12) {
			percentage = file.percent - 2;
			progressbar.width(percentage + '%').text(percentage + '%');
		}
		else if (file.percent < 10) {
			progressbar.width(10 + '%').text(10 + '%');
		}
	});

	uploader.bind("FileUploaded", function (uploader, file, resp) {
		progressbar.width('100%').text('100%');
		var res = JSON.parse(resp.response);
		if (res['result'] == 'ok') {
			progressbar.closest('.progress').addClass('hidden');
			progressbar.text('10%').css('width', '10%');

			btnBrowse.removeClass('hidden');
			updateImage(res);
			$('#imageUploadModal').modal('hide');
		} else {
			alert('Error on uploading file response');
		}
	});

	uploader.init();

	$('.btnAcmsImageDelete').click(function () {
		var btn = $(this);

		acmsImagePanel = btn.closest('.acmsImagePanel');
		url = btn.closest('.acmsImagePanel').data('url');
		msg = _t('Do you really want to delete this item?\n\nWARNING: this operation cannot be undone.');

		if (confirm(msg)) {
			btn.button('loading');
			$.ajax(
				url,
				{method: 'DELETE'}
			)
				.done(function (res) {
					if (res['result'] == 'ok') {
						updateImage(res);
					}
				})
				.fail(function () {
					alert('Error deleting img');
				})
				.always(function () {
					btn.button('reset');
				});
		}
		return false;
	});

	var updateImage = function (res) {
		acmsImagePanel.find('.fa-image').removeClass('fa-image').addClass('fa-spin fa-refresh fa-fw');

		var imgLoad = $('<img>').css('width', '1px').css('height', '1px').attr('src', res['image_url']).appendTo('body');

		imgLoad.load(function () {
			acmsImagePanel.find('img').attr('src', res['image_url']);
			acmsImagePanel.find('.btnAcmsImageDownload').attr('href', res['image_url']);
			acmsImagePanel.find('.fa-spin.fa-refresh').removeClass('fa-spin fa-refresh fa-fw').addClass('fa-image');

			if (res['image_exists']) {
				acmsImagePanel.find('.btnAcmsImageDownload').removeClass('hidden');
				acmsImagePanel.find('.btnAcmsImageDelete').removeClass('hidden');
			} else {
				acmsImagePanel.find('.btnAcmsImageDownload').addClass('hidden');
				acmsImagePanel.find('.btnAcmsImageDelete').addClass('hidden');
			}

			imgLoad.detach();
		});
	};

};

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

// Texts management - Admin Atuincms

var bindMediaTextsAdmin = function () {
	var textEditorInitialTextValue = '';

	function inputChanged() {
		new_value = $('#textEditorInputTextarea').val();
		return textEditorInitialTextValue != new_value;
	}

	// Edit text
	$('.btnAcmsTextEdit').click(function () {
		var btn = $(this),
			textPanel = btn.closest('.acmsTextPanel'),
			preview_box = $('#previewBox'),
			preview_refresh_spinner = $('.textEditorPreviewRefresh');

		$('#textEditorForm').data('acmsTextPanel', textPanel);
		preview_refresh_spinner.addClass('fa-spin');
		preview_box.html($('#htmlPreviewSavedSpinner').html());

		$.ajax(
			textPanel.data('url')
		)
			.done(function (res) {
				// to perform the check for some edits
				textEditorInitialTextValue = res['text'];
				$('#textEditorInputTextarea').val(res['text']);
				preview_box.html(res['text_html']);
				preview_refresh_spinner.removeClass('fa-spin');
			})
			.fail(function () {
				alert('Error on get text');
			});


		$('#textEditorModal').modal('show');
	});

	function getSelection(selector) {
		var selectedText;
		var textComponent = $(selector)[0];
		var startPos, endPos;

		if (textComponent.selectionStart != undefined) {
			startPos = textComponent.selectionStart;
			endPos = textComponent.selectionEnd;
			selectedText = textComponent.value.substring(startPos, endPos);
		}

		return {start: startPos, end: endPos, selectedText: selectedText};
	}

	function previewUpdate() {
		$('.textEditorPreviewRefresh').addClass('fa-spin');
		$.ajax(
			$('#previewBox').data('url'),
			{
				method: 'POST',
				data: $('#textEditorForm').serialize(),
				timeout: 5000
			}
		)
			.done(function (res) {
				$('#previewBox').html(res);
			})
			.fail(function () {
				alert('Error on getting preview');
			})
			.always(function () {
				$('.textEditorPreviewRefresh').removeClass('fa-spin');
			});
	}

	previewUpdate.start = function () {
		if (previewUpdate.tid !== undefined) {
			clearTimeout(previewUpdate.tid);
		}
		previewUpdate.tid = window.setTimeout(previewUpdate, 1000);
	};

	function editorBtn(btn) {
		// get selected text if any
		var ta = $('#textEditorInputTextarea');
		var current_text = ta.val();
		var selection = getSelection('#textEditorInputTextarea');

		if (btn.hasClass('btnBold')) {
			//make it bold
			if (selection.selectedText != '') {

				var new_text = current_text.slice(0, selection.start) + '**' + selection.selectedText + '**' + current_text.slice(selection.end);
				ta.val(new_text);
				ta.focus();
			}
		}
		else if (btn.hasClass('btnItalic')) {
			//make it italic
			if (selection.selectedText != '') {

				var new_text = current_text.slice(0, selection.start) + '*' + selection.selectedText + '*' + current_text.slice(selection.end);
				ta.val(new_text);
				ta.focus();
			}
		}
		else if (btn.hasClass('btnHeader1')) {
			//add Header1
			var new_text = current_text.slice(0, selection.start) + '# ' + current_text.slice(selection.start);
			ta.val(new_text);
			ta.focus();
		}
		else if (btn.hasClass('btnHeader2')) {
			//add Header2
			var new_text = current_text.slice(0, selection.start) + '## ' + current_text.slice(selection.start);
			ta.val(new_text);
			ta.focus();
		}
		else if (btn.hasClass('btnHeader3')) {
			//add Header3
			var new_text = current_text.slice(0, selection.start) + '### ' + current_text.slice(selection.start);
			ta.val(new_text);
			ta.focus();
		}

		$('#textEditorForm').trigger('keyup');
	}


	$(function () {
		$('#textEditorForm').on('keyup', function () {
			previewUpdate.start();
		});
	});

	$('.editorBtn').on('click', function () {
		var btn = $(this);
		editorBtn(btn);
		return false;
	});

	$('#textEditorForm').on('submit', function () {
		$('#btnAcmsTextSave').trigger('click');
		return false;
	});

	$('#btnAcmsTextSave').click(function () {
		var btn = $(this),
			modal = $('#textEditorModal'),
			form = $('#textEditorForm'),
			textPanel = form.data('acmsTextPanel');

		btn.button('loading');
		// update value only if input has been modified
		if (inputChanged()) {
			$.ajax(
				textPanel.data('url'),
				{
					data: form.serialize(),
					method: 'POST'
				}
			)
				.done(function (res) {
					if (res['result'] == 'ok') {
						textPanel.find('.textContent').html(res['text_html']);
						textPanel.find('.btnAcmsTextDelete').removeClass('hidden');
						modal.modal('hide');
					} else {
						alert('Error on save text');
					}
				})
				.fail(function () {
					alert('Error on save text');
				})
				.always(function () {
					btn.button('reset');
				});
		} else {
			btn.button('reset');
			modal.modal('hide');
		}

	});

	// Delete text
	$('.btnAcmsTextDelete').click(function () {
		var btn = $(this),
			textPanel = btn.closest('.acmsTextPanel');

		url = textPanel.data('url');
		msg = _t('Do you really want to delete this item?\n\nWARNING: this operation cannot be undone.');

		if (confirm(msg)) {
			btn.button('loading');
			$.ajax(
				url,
				{
					method: 'DELETE'
				}
			)
				.done(function (res) {
					if (res['result'] == 'ok') {
						textPanel.find('.textContent').html(res['text_html']);
						btn.button('reset');
						btn.addClass('hidden');
						modal.modal('hide');
					} else {
						alert('Error on delete text');
					}
				})
				.fail(function () {
					alert('Error on delete text');
				})
				.always(function () {
					btn.button('reset');
				});
		}
		return false;
	});

};

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
