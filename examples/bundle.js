/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports) {

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

/***/ }
/******/ ]);