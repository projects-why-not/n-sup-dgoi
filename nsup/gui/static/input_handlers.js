function _setDateOffset(dateParent, offset) {
	var tag = dateParent.children[1];	
	if (offset > 0) {
		tag.stepUp(offset);
	} else {
		tag.stepDown(-offset);
	}
};

function incDate(sender) {
	_setDateOffset(sender.parentElement, 1);
	if (sender.id.slice(0, -1) == "6")
		chatDateSelected(sender.parentElement.children[1]);
};

function decDate(sender) {
	_setDateOffset(sender.parentElement, -1);
		
	if (sender.id.slice(0, -1) == "6")
		chatDateSelected(sender.parentElement.children[1]);
};

function checkInt(sender) {
	var value = sender.value;
	console.log(value, value.slice(-2));
	if (value.slice(-2, -1) == '.' || value.slice(-2, -1) == ',') {
		sender.value = value.slice(0, -2);
	}
}

function checkFloat(sender) {
	var value = sernder.value;
	if (value.slice(-2, -1) == ',') {
		sender.value = value.slice(0, -2) + '.' + value.slice(-1);
	}
}

function chatDateSelected(sender) {
	var value = sender.value;
	
	[12, 30].forEach(fid => {
		var field = document.getElementById(fid);
		field.value = value;
		decDate(field);
	});
	
}

function matchDateAndDaysAgo(sender) {
	var curDate = document.getElementById("6").value;
	
	if (sender.type == "number") {
		document.getElementById((parseInt(sender.id) - 1).toString()).value = curDate + parseInt(sender.value);
	} else if (sender.type == "date") {
		var setDate = sender.value;
		document.getElementById((parseInt(sender.id) + 1).toString()).value = curDate - setDate;
	} else {
		alert("Smth went wrong during date-days matching!");
	}

}

function tubeDateHandler(sender) {
	var dateDOM = document.getElementById((parseInt(sender.id) + 1).toString());
	var hasCath = sender.value != "Нет"; // sender.value.includes("зонд") || sender.value.includes("стома");
	dateDOM.parentElement.children.forEach(elem => {
		elem.disabled = !hasCath;
	});
}

function addEnteralField(sender) {
	var selftr = sender.parentElement.parentElement;
	var sampletr = selftr.parentElement.children[0];
	var table = sender.parentElement.parentElement.parentElement;

	console.log(sampletr, sampletr.cloneNode());
		
	table.insertBefore(sampletr.cloneNode(), sender.parentElement.parentElement);
}
