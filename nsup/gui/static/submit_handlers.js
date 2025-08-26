
window.addEventListener("load", () => {
	function sendData(sender) {
		const XHR = new XMLHttpRequest();
		const FD = new FormData(form);
		FD.append(form.submitted, 1);
		XHR.addEventListener("load", (event) => {
			let overlayDiv = event.target.responseText;

			if (overlayDiv.slice(0, 3) == "ERR" || overlayDiv.slice(0, 3) == "MSG") {
				alert(overlayDiv.substring(5));
			}
			else {
				var newWindow = window.open("_blank");
				newWindow.document.write(overlayDiv);
				newWindow.focus();
				// form.parentElement.parentElement.innerHTML = form.parentElement.parentElement.innerHTML + overlayDiv;
			}
			return false;
		});

		XHR.addEventListener("error", (event) => {
			alert('Oops! Something went wrong.');
		});
		// XHR.open("POST", "https://nutrition.projectswhynot.site/nutrition");
		XHR.open("POST", "http://127.0.0.1:3000/nutrition");
		XHR.send(FD);

		return false;
	}

	function goToNextInput(event) {
		event.preventDefault();
		let selfInd = inputs.indexOf(event.target);
		if (selfInd == inputs.length)
			return false;
		if (inputs[selfInd + 1].id[0] != event.target.id[0]) {
			const activeTab = document.getElementsByClassName("selected")[0];
			const activeTabInd = tabNavs.indexOf(activeTab);
			if (activeTabInd == tabNavs.length)
				return false;
			tabNavs[activeTabInd + 1].onclick();
		}

		inputs[selfInd + 1].focus();
	}

	function goToPrevInput(event) {
		event.preventDefault();
		let selfInd = inputs.indexOf(event.target);
		if (selfInd == 0)
			return false;
		if (inputs[selfInd - 1].id[0] != event.target.id[0]) {
                        const activeTab = document.getElementsByClassName("selected")[0];
                        const activeTabInd = tabNavs.indexOf(activeTab);
                        if (activeTabInd == 0)
                                return false;
                        tabNavs[activeTabInd - 1].onclick();
                }

		inputs[selfInd - 1].focus();
	}
	
	const form = document.getElementById("main_form");
	form.addEventListener("submit", (event) => {
		console.log(form.submitted);
		event.preventDefault();
		sendData(event.target);
		return false;
	});

	const submitBts = document.getElementsByClassName("pag-item-submit");
	for (var i = 0; i < submitBts.length; i++) {
		submitBts[i].addEventListener("click", (event) => {
			event.target.form.submitted = event.target.name;
		});
	}

	const inputs = Array.prototype.slice.call(document.getElementsByTagName("input"));
	const tabNavs = Array.prototype.slice.call(document.getElementsByClassName("nav-item"));

	for (var i = 0; i < inputs.length; i++) {
		inputs[i].onkeydown = function(e) {
			if (e.keyCode == 38) {
				goToPrevInput(e);
				return false;
			}
			if (e.keyCode == 40) {
				goToNextInput(e);
				return false; 
			}

			if (e.target.type == "checkbox" && (e.keyCode == 37 || e.keyCode == 39)) {
				console.log(e.target.parentElement);
				e.target.parentElement.click();
				return false;
			}

		};
	}

	var date = new Date();
	var currentDate = date.toISOString().substring(0,10);
	var chatDateHandler = document.getElementById("1^6");
	chatDateHandler.value = currentDate;
	chatDateHandler.onchange();
	document.getElementById("5^147").checked = true;
});
