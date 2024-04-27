const formToJson = (formElement) => {
	var inputElements = formElement.getElementsByTagName("input");
	var jsonObject = {};
	for (var i = 0; i < inputElements.length; i++) {
		var inputElement = inputElements[i];
		if (inputElement.type === "submit") {
			continue;
		}
		jsonObject[inputElement.name] = inputElement.value;

	}
	return JSON.stringify(jsonObject);
}

window.onload = (event) => {
	window.addEventListener('submit', async (event) => {
		event.preventDefault();
		let input = event.submitter;
		let form = input.form;
		let json = formToJson(form);
		let url = `/${form.name}`;

		const response = await fetch(url, {
			method: "POST",
			mode: "same-origin",
			cache: "no-cache",
			credentials: "same-origin",
			headers: {
				"Content-Type": "application/json",
			},
			redirect: "follow",
			referrerPolicy: "no-referrer",
			body: json,
		});

		console.log(await response.json())
	});

	console.log("page is fully loaded");
};