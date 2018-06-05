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
