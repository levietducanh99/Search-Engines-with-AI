import React from "react";

function SearchBar({ query, setQuery, onSearch }) {
    return (
        <div style={{ marginBottom: "20px" }}>
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your search query"
                style={{ padding: "8px", width: "300px", marginRight: "10px" }}
            />
            <button onClick={onSearch} style={{ padding: "8px 16px" }}>
                Search
            </button>
        </div>
    );
}

export default SearchBar;
