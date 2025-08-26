function _setDateOffset(dateParent, offset) {
	var tag = dateParent.children[1];
	if (tag.disabled)
		return false
	if (offset > 0) {
		tag.stepUp(offset);
	} else {
		tag.stepDown(-offset);
	}
	return true;
};

function incDate(sender) {
	if (!_setDateOffset(sender.parentElement, 1))
		return;
	if (sender.id.slice(0, -1) == "6")
		chatDateSelected(sender.parentElement.children[1]);
	const sender_id = sender.id.slice(2, -1);
	if (sender_id == "30" || sender_id == "12")
		matchDateAndDaysAgo(sender.parentElement.children[1]);
};

function decDate(sender) {
	if (!_setDateOffset(sender.parentElement, -1))
		return;
	if (sender.id.slice(0, -1) == "6")
		chatDateSelected(sender.parentElement.children[1]);
	const sender_id = sender.id.slice(2, -1);
	if (sender_id == "30" || sender_id == "12")
		matchDateAndDaysAgo(sender.parentElement.children[1]);
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

function toggleNecessity(tag, required) {
	const span_text = '<span title="Это поле должно быть заполнено" style="color:red; font-size:150%">*</span>';
	tag.required = required;
	const labelTd = tag.parentElement.parentElement.children[0];
	console.log(required);
	if (required) {
		console.log(required, labelTd, span_text);
		// labelTd.insertBefore(document.createTextNode(span_text), labelTd.children[0]);

		labelTd.innerHTML = span_text + labelTd.innerHTML;
	} else {
		if (labelTd.children.length > 1)
			labelTd.children[0].remove();
		// labelTd.children.splice(0, 1);
	}

}

function manageTherapyStage(sender) {
	const opt_id = sender.value;
	console.log(opt_id);
	const tgtDOM = document.getElementById("6^10");
	const required_opts = ["блок ПХТ", "период после блока ПХТ", "послеоперационный период", "лучевая терапия", "ничего из перечисленного"];
	const required = required_opts.includes(opt_id);
	toggleNecessity(tgtDOM, required);

}

function chatDateSelected(sender) {
	var value = sender.value;
	var inputs = document.getElementsByTagName("input");

	for (var i = 0; i < inputs.length; i++) {
		var field = inputs[i];
		if (field.type != 'date')
			continue;
		if (field.disabled)
			continue;
		field.value = value;
		const _id = field.id.slice(2);
		if (_id == "12")
			matchDateAndDaysAgo(field, 1);
		if (_id == "30")
			matchDateAndDaysAgo(field, 0);
	};

}

function matchDateAndDaysAgo(sender, delta) {
	var curDate = document.getElementById("1^6").value;

	curDate = new Date(Date.parse(curDate));

	console.log(curDate);

	if (sender.type == "number") {
		var tgt_tr = sender.parentElement.parentElement.nextSibling.nextSibling;
		var tgt_input = tgt_tr.childNodes[3].childNodes[1].childNodes[3];

		var n_days = 0;
		if (sender.value.length > 0)
			n_days = parseInt(sender.value);


		var newDate = new Date(curDate.valueOf());
		newDate.setDate(curDate.getDate() - n_days + delta);

		var day = ("0" + newDate.getDate()).slice(-2);
		var month = ("0" + (newDate.getMonth() + 1)).slice(-2);
		var tgtDate = newDate.getFullYear() + "-" + (month)+"-"+(day);

		tgt_input.value = tgtDate;
	} else if (sender.type == "date") {
		var tgt_tr = sender.parentElement.parentElement.parentElement.previousSibling.previousSibling;
		var tgt_input = tgt_tr.childNodes[3].childNodes[1];

		var setDate = new Date(Date.parse(sender.value));

		const diffTime = Math.abs(curDate - setDate);
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + delta;

		tgt_input.value = diffDays;


	} else {
		alert("Smth went wrong during date-days matching!");
	}

}

function tubeDateHandler(sender) {
	var dateDOMpts = sender.id.split("^");
	dateDOMpts[1] = (parseInt(dateDOMpts[1]) + 1).toString();

	const dateDOMid = dateDOMpts[0] + "^" + dateDOMpts[1];
	const dateDOM = document.getElementById(dateDOMid);
	var hasCath = sender.value != 3;
	const nodes = dateDOM.parentElement.children;


	for (var i = 0; i < nodes.length; i++) {
		nodes[i].disabled = !hasCath;
	};
	if (hasCath)
		dateDOM.name = dateDOM.id;
	else
		dateDOM.removeAttribute("name");
}

function duplicatePreviousField(sender) {
	var selftr = sender.parentElement.parentElement;
	var sampletr = selftr.parentElement.children[0];
	var table = sender.parentElement.parentElement.parentElement;
	var curTotalSameFields = table.children.length - 1;

	console.log(table, table.children[0].children);

	var trCopy = sampletr.cloneNode(true);

	console.log(trCopy.children);

	var labelPts = trCopy.children[0].innerText.split(" ");
	trCopy.children[0].innerText = labelPts[0] + " " + labelPts[1] + " " + (curTotalSameFields + 1).toString()

	// console.log(trCopy.children[1].children[0].children[0].children);
	var trs = trCopy.children[1].children[0].children[0].children;
	for (var i = 0; i < trs.length; i++) {
		var tr = trs[i];

		var kMax = tr.children[1].children.length - 1;
		var inputElem = tr.children[1].children[kMax];
		var idPts = inputElem.id.split("*");
		idPts[1] = (curTotalSameFields + 1).toString();
		var newId = idPts[0] + "*" + idPts[1] + "*" + idPts[2];

		trCopy.children[1].children[0].children[0].children[i].children[1].children[kMax].id = newId;

		trCopy.children[1].children[0].children[0].children[i].children[1].children[0].name = newId;
		trCopy.children[1].children[0].children[0].children[i].children[1].children[0].value = "";
		if (kMax != 0) {
			trCopy.children[1].children[0].children[0].children[i].children[1].children[0].setAttribute('list', newId);
		}
	};

	table.insertBefore(trCopy, sender.parentElement.parentElement);

}
