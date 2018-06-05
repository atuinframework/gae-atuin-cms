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

