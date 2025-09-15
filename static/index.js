// when the return button is clicked it returns the current value in the search box to the backend.
function returnJson() {
    const icdValue = document.getElementById("icdCode1").value;
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
    queryCallbackFunction: (results) => {
        console.log("Raw results:", results);

        const container = document.getElementById('my-results');
        container.innerHTML = '';
        results.forEach(entity => {
            const div = document.createElement('div');
            div.textContent = `${entity.code} - ${entity.title}`;
            div.addEventListener('click', () => {
                console.log("Selected entity:", entity);
                // Optional: call selectedEntityFunction yourself if needed
            });
            container.appendChild(div);
        });
    },

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

    selectedEntityFunction: (selectedEntity) => { 
        // document.getElementById('icdCode').value = `${selectedEntity.code} - ${selectedEntity.title}`;
        ECT.Handler.clear("1");
		console.log(selectedEntity.code)
		document.getElementById('icdCode1').value = `${selectedEntity.code} , ${selectedEntity.title}`;
    }
};


ECT.Handler.configure(mySettings, myCallbacks);

