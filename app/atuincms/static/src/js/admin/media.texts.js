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
