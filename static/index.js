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

const doFetch = (url, body = null) => {
	let options = {
		method: "POST",
		mode: "same-origin",
		cache: "no-cache",
		credentials: "same-origin",
		headers: {
			"Content-Type": "application/json",
		},
		redirect: "follow",
		referrerPolicy: "no-referrer",
	};

	if (body !== null) {
		options['body'] = body;
	}

	return fetch(url, options);
};

const loadSugar = async () => {
	const response = await doFetch('/get_sugar', '{}');
	const data = await response.json();
	let table = document.getElementById("sugar-blend-table");
	table.innerHTML = '';

	data.result.forEach(({ id, created_at, ethyl_vanillin, sugar, vanillin }) => {
		table.innerHTML += `<tr><th>${id}</th><th>${created_at}</th><td>${sugar}</td><td>${vanillin}</td><td>${ethyl_vanillin}</td></tr>`;
	});

};

const loadTea = async () => {
	const response = await doFetch('/list_cups', '{}');
	const data = await response.json();
	let table = document.getElementById("tea-servings-table");
	table.innerHTML = '';

	let box = document.getElementById('last-cup-id');
	let button = document.getElementById('last-cup-rank-submit');

	data.result.forEach(({ id, created_at, water, blend, sugar, almond_milk, quality }) => {
		if (quality == null) {
			quality = 'Unknown';
		}

		box.value = id;

		if (button) {
			button.value = `Rank cup #${id}`;
		}

		table.innerHTML += `<tr><th>${id}</th><th>${created_at}</th><td>${water}</td><th>${blend}</th><td>${sugar}</td><td>${almond_milk}</td><th>${quality}</th></tr>`;
	});

};

const loadSuggestion = async () => {
	const response = await doFetch('/get_suggestion');
	const data = await response.json();
	displaySuggestion(data);
};

const loadBestGuess = async () => {
	const response = await doFetch('/get_best_guess');
	const data = await response.json();
	displayBestGuess(data);
};

const displaySuggestion = (data) => {
	let form = document.getElementById("cup-balance-suggestion");

	for (const el of form.getElementsByTagName('input')) {
		if (el.name) {
			el.value = data.result[el.name];
		}
	}
};

const displayBestGuess = (data) => {
	let form = document.getElementById("cup-balance-recommendation");

	for (const el of form.getElementsByTagName('input')) {
		if (el.name) {
			if (el.name === 'quality') {
				el.value = data.result.target;
			}
			else {
				el.value = data.result.params[el.name];
			}
		}
	}
};

window.onload = async (event) => {
	window.addEventListener('submit', async (event) => {
		event.preventDefault();
		let input = event.submitter;
		let form = input.form;
		let json = formToJson(form);
		let url = `/${form.name}`;

		const response = await doFetch(url, json);

		let data = await response.json();
		switch (form.name) {
			case 'set_sugar':
				await loadSugar();
				break;
			case 'update_cup':
				await loadSuggestion();
				await loadBestGuess();
			case 'add_cup':
				await loadTea();
				break;
			case 'get_suggestion':
				await displaySuggestion(data);
				break;
			case 'get_suggestion':
				await displayBestGuess(data);
				break;
		}
	});

	await loadSugar();
	await loadTea();
	await loadSuggestion();
	await loadBestGuess();

	console.log("page is fully loaded");
};

