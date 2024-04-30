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

const ff = (number) => Number.parseFloat(number).toFixed(2);
const fd = (date) => (new Date(date)).toLocaleString();

const loadSugar = async () => {
	const response = await doFetch('/get_sugar', '{}');
	const data = await response.json();
	let table = document.getElementById("sugar-blend-table");
	table.innerHTML = '';

	data.result.forEach(({ id, created_at, ethyl_vanillin, sugar, vanillin }) => {
		table.innerHTML += `<tr><th>${id}</th><th>${fd(created_at)}</th><td>${ff(sugar)}</td><td>${ff(vanillin)}</td><td>${ff(ethyl_vanillin)}</td></tr>`;
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

		table.innerHTML += `<tr><th>${id}</th><th>${fd(created_at)}</th><td>${ff(water)}</td><th>${blend}</th><td>${ff(sugar)}</td><td>${ff(almond_milk)}</td><th>${quality}</th></tr>`;
	});

};

const loadSuggestions = async () => {
	const response = await doFetch('/list_suggestions', '{}');
	const data = await response.json();
	let table = document.getElementById("tea-suggestions-table");
	table.innerHTML = '';

	data.result.forEach(({ id, created_at, water, blend, sugar, almond_milk }) => {
		table.innerHTML += `<tr><th>${id}</th><th>${fd(created_at)}</th><td>${ff(water)}</td><th>${blend}</th><td>${ff(sugar)}</td><td>${ff(almond_milk)}</td></tr>`;
	});

};

const loadSuggestion = async () => {
	const response = await doFetch('/get_suggestion');
	const data = await response.json();
	if (!data.result) {
		return
	}

	displaySuggestion(data);
};

const loadBestGuess = async () => {
	const response = await doFetch('/get_best_guess');
	const data = await response.json();
	if (!data.result) {
		return
	}
	displayBestGuess(data);
};

const loadSugarSuggestion = async () => {
	const response = await doFetch('/get_sugar_suggestion');
	const data = await response.json();
	if (!data.result) {
		return
	}

	displaySugarSuggestion(data);
};

const displaySugarSuggestion = (data) => {
	let form = document.getElementById("sugar-blend-suggestion");

	for (const el of form.getElementsByTagName('input')) {
		if (el.name) {
			el.value = ff(data.result[el.name]);
		}
	}
};

const displaySuggestion = (data) => {
	let form = document.getElementById("cup-balance-suggestion");

	for (const el of form.getElementsByTagName('input')) {
		if (el.name) {
			el.value = ff(data.result[el.name]);
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
				el.value = ff(data.result.params[el.name]);
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
				await loadSuggestions();
				await loadBestGuess();
				await loadTea();
				await loadSugarSuggestion();
				break;
			case 'add_cup':
				await loadTea();
				break;
			case 'get_suggestion':
				await displaySuggestion(data);
				await loadSuggestions();
				break;
			case 'get_best_guess':
				await displayBestGuess(data);
				break;
			case 'get_sugar_suggestion':
				await displaySugarSuggestion(data);
				break;
		}
	});

	await loadSuggestions();
	await loadSugar();
	await loadTea();
	await loadSuggestion();
	await loadBestGuess();
	await loadSugarSuggestion();

	console.log("page is fully loaded");
};

