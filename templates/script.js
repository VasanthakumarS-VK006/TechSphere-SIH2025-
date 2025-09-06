// script.js
console.log("HEllo")
const searchInput = document.getElementById('search-input');
const suggestionsContainer = document.getElementById('suggestions');

searchInput.addEventListener('input', async () => {
  const query = searchInput.value.trim();
  if (query.length === 0) {
    suggestionsContainer.style.display = 'none';
    return;
  }

  // Fetch suggestions from the backend
  try {
    const response = await fetch(`http://localhost:5000/api/suggestions?q=${encodeURIComponent(query)}`);
    const suggestions = await response.json();
    
    // Clear previous suggestions
    suggestionsContainer.innerHTML = '';
    
    // Display suggestions
    if (suggestions.length > 0) {
      suggestions.forEach(item => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        div.textContent = item;
        div.addEventListener('click', () => {
          searchInput.value = item;
          suggestionsContainer.style.display = 'none';
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

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
  if (!suggestionsContainer.contains(e.target) && e.target !== searchInput) {
    suggestionsContainer.style.display = 'none';
  }
});
