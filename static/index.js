// NOTE: For NAMC to ICD
// when the return button is clicked it returns the current value in the search box to the backend.
function returnJson() {
	const icdValue = document.getElementById("icdCode").value;
	const namcValue = document.getElementById("search-input").value;

	const payload = { icd: icdValue, namc: namcValue };

	fetch("http://127.0.0.1:5000/api/returnJson", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(payload)
	}).catch(error => console.error("Error:", error));
}

// script.js
const searchInput = document.getElementById('search-input');
const suggestionsContainer = document.getElementById('suggestions');
const submitButton = document.getElementById('submit-button');
const resultInput = document.getElementById('result-input');
const resultDiv = document.getElementById('result');

let isSuggestionSelected = false; // Track if a suggestion was selected
let isResultSelected = false; // Track if a suggestion was selected


//NOTE: Checks if any change is made to the NAMC Code search box
searchInput.addEventListener('input', async () => {
	const query = searchInput.value.trim();
	isSuggestionSelected = false; // Reset on new input
	submitButton.disabled = true; // Disable button until suggestion is selected

	if (query.length === 0) {
		suggestionsContainer.style.display = 'none';
		return;
	}

	try {
		const response = await fetch(`http://127.0.0.1:5000/api/suggestions?q=${encodeURIComponent(query)}`);
		if (!response.ok) throw new Error(`Network response was not ok: ${response.status}`);

		const suggestions = await response.json();
		console.log('Suggestions:', suggestions); // Debug

		suggestionsContainer.innerHTML = '';

		if (suggestions.length > 0) {
			suggestions.forEach(item => {
				const div = document.createElement('div');
				div.className = 'suggestion-item';
				div.textContent = item; // English term
				div.addEventListener('click', () => {
					searchInput.value = item; // Set input value
					suggestionsContainer.style.display = 'none';
					isSuggestionSelected = true; // Mark suggestion as selected
					submitButton.disabled = false; // Enable submit button
				});
				suggestionsContainer.appendChild(div);
			});
			suggestionsContainer.style.display = 'block';
		} else {
			suggestionsContainer.style.display = 'none';
		}
	} catch (error) {
		console.error('Error fetching suggestions:', error);
		suggestionsContainer.style.display = 'none';
	}
});




//NOTE: Handle submit button click
submitButton.addEventListener('click', async () => {
	if (!isSuggestionSelected) {
		resultDiv.innerHTML = '<p>Please select a suggestion from the list.</p>';
		return;
	}

	const selectedTerm = searchInput.value.trim();
	if (!selectedTerm) {
		resultDiv.innerHTML = '<p>No term selected.</p>';
		return;
	}

	try {

		terms = selectedTerm.split(",")
		ECT.Handler.search("1", terms[1]);
		console.log(terms[1])


	} catch (error) {
		console.error('Error submitting term:', error);
		resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
	}
});



// NOTE: This is for the WHO ECT

const mySettings = {
	apiServerUrl: "https://id.who.int",
	apiSecured: true,
	popupMode: true,
	searchByCodeOrURI: true
};


const myCallbacks = {
	// queryCallbackFunction: (results) => {
	//     console.log("Raw results:", results);
	//
	//     const container = document.getElementById('my-results');
	//     container.innerHTML = '';
	//     results.forEach(entity => {
	//         const div = document.createElement('div');
	//         div.textContent = `${entity.code} - ${entity.title}`;
	//         div.addEventListener('click', () => {
	//             console.log("Selected entity:", entity);
	//             // Optional: call selectedEntityFunction yourself if needed
	//         });
	//         container.appendChild(div);
	//     });
	// },

	getNewTokenFunction: async () => {
		const url = 'http://127.0.0.1:5000/api/newToken';
		try {
			const response = await fetch(url);
			const result = await response.json();
			return result.token;
		} catch (e) {
			console.log("Error during the request", e);
			return null;
		}
	},

	selectedEntityFunction: (selectedEntity, ctwObject) => {
		// document.getElementById('icdCode').value = `${selectedEntity.code} - ${selectedEntity.title}`;
		console.log(selectedEntity.code)

		if (selectedEntity.iNo == 1) {
			ECT.Handler.clear("1");
			document.getElementById('icdCode').value = `${selectedEntity.code} , ${selectedEntity.title}`;
		}
		else {
			ECT.Handler.clear("2");
			document.getElementById('icdCode2').value = `${selectedEntity.code} , ${selectedEntity.title}`;
			submitButton2.disabled = false; // Enable submit button
		}
	}
};


ECT.Handler.configure(mySettings, myCallbacks);





// NOTE: For ICD to NAMC

function returnJson() {
	const icdValue2 = document.getElementById("icdCode2").value;
	const namcValue2 = document.getElementById("search-input2").value;

	const payload2 = { icd: icdValue2, namc: namcValue2 };

	fetch("http://127.0.0.1:5000/api/returnJson", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(payload2)
	}).catch(error => console.error("Error:", error));
}

// script.js
const searchInput2 = document.getElementById('icdCode2');
const suggestionsContainer2 = document.getElementById('suggestions2');
const submitButton2 = document.getElementById('submit-button2');
const resultInput2 = document.getElementById('search-input2');

let isSuggestionSelected2 = false; // Track if a suggestion was selected
let isResultSelected2 = false; // Track if a suggestion was selected


//NOTE: Checks if any change is made to the NAMC Code search box
searchInput2.addEventListener('input', async () => {
	const query2 = searchInput.value.trim();
	isSuggestionSelected2 = false; // Reset on new input
	submitButton2.disabled = true; // Disable button until suggestion is selected

	if (query2.length === 0) {
		suggestionsContainer2.style.display = 'none';
		return;
	}

	try {
		const response = await fetch(`http://127.0.0.1:5000/api/suggestions?q=${encodeURIComponent(query2)}`);
		if (!response.ok) throw new Error(`Network response was not ok: ${response.status}`);

		console.log("Inside the try blocl");
		const suggestions = await response.json();
		console.log('Suggestions:', suggestions); // Debug

		suggestionsContainer2.innerHTML = '';

		if (suggestions.length > 0) {
			suggestions.forEach(item => {
				const div2 = document.createElement('div');
				div2.className = 'suggestion-item';
				div2.textContent = item; // English term
				div2.addEventListener('click', () => {
					searchInput2.value = item; // Set input value
					suggestionsContainer2.style.display = 'none';
					isSuggestionSelected2 = true; // Mark suggestion as selected
				});
				suggestionsContainer2.appendChild(div);
			});
			suggestionsContainer2.style.display = 'block';
		} else {
			suggestionsContainer2.style.display = 'none';
		}
	} catch (error) {
		console.error('Error fetching suggestions:', error);
		suggestionsContainer2.style.display = 'none';
	}
});




//NOTE: Handle submit button click
submitButton2.addEventListener('click', async () => {
	console.log("Inside the submit's event listener")

	const selectedTerm = searchInput2.value.trim();
	console.log(selectedTerm)
	console.log("After displaying selectedTerm")
	if (!selectedTerm) {
		return;
	}

	try {

		console.log("Inside the submit's event listener")
		const response = await fetch(`http://127.0.0.1:5000/api/ICDtoNAMC?q=${encodeURIComponent(selectedTerm)}`);
		if (!response.ok) throw new Error(`Network response was not ok: ${response.status}`);

		const suggestions = await response.json();

		resultInput2.value = `${suggestions.code}, ${suggestions.term}`;




	} catch (error) {
		console.error('Error submitting term:', error);
	}
});


