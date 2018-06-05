$(function () {
	/*
	 * Template for binding functions to context.
	 */
	/*
	$('html.admin.dashboard').each(function () {
		...
	});
	*/
	$('html.admin.users').each(function () {
		bindAdminUsers();
	});


	//window.modalAlert = initialize_custom_alert("#modalAlert");
});

var initialize_custom_alert = function (elem) {

	var modalPopUp = {
		"handler": function () {
		}, //result, this-class, event
		"active": false
	};

	modalPopUp.init = function (selector) {
		var self = this;

		this.elem = $(selector);
		this.title = this.elem.find(".alert-title");
		this.message = this.elem.find(".alert-message");
		this.content = this.elem.find(".alert-content");

		this.btn_confirm = this.elem.find(".alert-confirm").on("click", function (ev) {
			return self.handler("OK", self, ev);
		});

		this.btn_abort = this.elem.find(".alert-abort").on("click", function (ev) {
			return self.handler("ABORT", self, ev);
		});

		//this.set();
	};

	modalPopUp.show = function () {
		this.elem.modal("show");
		this.active = true;
	};
	modalPopUp.hide = function () {
		this.elem.modal("hide");
		this.active = false;
	};

	modalPopUp.reset = function () {
		this.set();
		//this.handler = function () {};
	};

	modalPopUp.set = function (title, message, content) {
		this.title.html(title || "");
		this.message.html(message || "");
		this.content.html(content || "");
	};


	modalPopUp.activate = function (title, callback, message, content) {
		this.reset();
		this.set(title, message, content);
		this.handler = callback || function () {
		};
		this.show();
	};


	modalPopUp.prompt = function (title, callback, message, content) {
		this.activate(title, callback, message, content);
	};

	modalPopUp.confirm = function (title, callback, message, content) {
		this.activate(title, callback, message, content);
	};

	modalPopUp.alert = function (title, callback, message, content) {
		this.activate(title, callback, message, content);
	};


	if (!!elem) {
		modalPopUp.init(elem);
	}
	return modalPopUp;
};


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
// Auth - Admin Users Management

function bindAdminUsers() {

	$('.modUser').on('click', function (e) {
		e.preventDefault();

		var url = $(this).data('url'),
			form = $('#userForm');

		form.attr('action', url);

		$.ajax(url)
			.done(function (data) {
				form.formtools('reset');
				user_role = data['role'];
				delete data['role'];
				user_active = data['active'];
				delete data['active'];

				form.formtools('reset', data);

				// set active
				if (user_active) {
					form.find('#active').prop('checked', true);
				}
				// set role
				role_selector = 'input[name="role"][value="' + user_role + '"]';
				form.find(role_selector).prop('checked', true);

				$('#userModal').modal('show');
			});

		return false;
	});

	$('.newUserBtn').on('click', function () {
		var form = $('#userForm');

		form.formtools('reset');
		form.find('input[type="radio"][name="role"]').first().prop('checked', true);

		form.attr('action', $(this).data('url'));
		$('#userModal').modal('show');
	});

	$('#userForm').on('submit', function () {
		$('#userModal .btnSave').trigger('click');
		return false;
	});

	$('#userModal .btnSave').on('click', function () {
		var btn = $(this),
			form = $('#userForm');


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
							window.location.reload();
						}, timeToRefresh);
					}
					else {
						btn.button('reset');
						window.alert("ERROR!");
					}
				})
				.fail(function (res) {
					btn.button('reset');
					window.alert("ERROR!")
				});
		}
	});

	$('.deleteUser').on('click', function () {
		var btn = $(this),
			row = btn.closest('tr');

		if (!window.confirm('ATTENZIONE!\nQuesta operazione è irreversibile.\n\nCancellare l\'utente?')) {
			return false;
		}
		btn.button('loading');
		$.ajax(
			$(this).data('url'),
			{
				method: 'DELETE'
			}
		)
			.done(function (res) {
				if (res['result'] == 'ok') {
					row.fadeOut('slow');
					$('.usersCount').html($('.usersCount').html() - 1);
				}
				else if (res['result'] == 'ko') {
					btn.button('reset');
					window.alert(res['error']);
				}
				else {
					btn.button('reset');
					window.alert("ERROR!");
				}
			})
			.fail(function (res) {
				window.alert("ERROR!")
			})
			.always(function () {
				btn.button('reset');
			});

		return false;
	});

	/**
	 * User search
	 */
	var updateUserSearch = function (q) {
		if (q.length > 2) {
			//search
			$('.searchable').parents('.userRow').show();
			$(".searchable:not(:icontains(" + q + "))").parents('.userRow').hide();
		} else {
			$('.searchable').parents('.userRow').show();
		}
	};

	$('#userListSearch').on('keyup', function () {
		updateUserSearch($('#userListSearch').val());
		return false;
	});

	$('#btnUserListSearch').on('click', function () {
		updateUserSearch($('#userListSearch').val());
		return false;
	});
}

