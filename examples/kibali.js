// var $ = require('jquery');

$.fn.serializeObject = function() {
	var arrSerialized = this.serializeArray();
	var objSerialized = {};

	arrSerialized.forEach(function(inputData) {
		var key = inputData['name'];
		var val = inputData['value'];
		if (key in objSerialized) {
			if (Array.isArray(objSerialized[key])) {
				objSerialized[key].push(val);
			} else {
				objSerialized[key] = [objSerialized[key], val];
			}
		} else {
			objSerialized[key] = val;
		}
	});
	return objSerialized;
};

// Approval Forms
// ~~~~~~~~~~~~~~

// Approval forms submit their data via XHR to the approval
// server.
function makeApprovalForm(form) {
	form.addEventListener('submit', function(evt) {
		evt.preventDefault();

		var data = $(this).serializeObject();
		var encodedData = JSON.stringify(data);

		// Submit the request.

		// Really though, we could just submit the form normally and
		// have the application know what URL to redirect to. That
		// would be good for graceful degredation into non-JS
		// situations.
	});
}