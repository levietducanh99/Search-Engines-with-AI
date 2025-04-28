import React, { useState } from "react";
import SearchBar from "../components/SearchBar";
import ResultsTable from "../components/ResultsTable";
import { searchArticles } from "../api/searchApi";

function SearchPage() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);

    const handleSearch = async () => {
        if (!query) {
            alert("Please enter a query!");
            return;
        }
        const searchResults = await searchArticles(query);
        setResults(searchResults);
    };

    return (
        <div style={{ padding: "20px", fontFamily: "Arial" }}>
            <h1>Hybrid Search Engine</h1>
            <SearchBar query={query} setQuery={setQuery} onSearch={handleSearch} />
            <ResultsTable results={results} />
        </div>
    );
}

export default SearchPage;
