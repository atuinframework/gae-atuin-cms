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

