export async function searchArticles(query) {
    const response = await fetch(`http://127.0.0.1:8000/search?query=${encodeURIComponent(query)}`);
    const data = await response.json();
    return data.results;
}
