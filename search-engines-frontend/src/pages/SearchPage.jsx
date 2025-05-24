import React, { useState } from "react";
import { searchArticles } from "../api/searchApi";
import ResultsTable from "../components/ResultsTable";
import "../components/ResultTable.css";

function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    if (!query.trim()) {
      alert("Please enter a search query");
      return;
    }

    try {
      const data = await searchArticles(query);
      setResults(data);
    } catch (err) {
      console.error("Fetch failed:", err);
      alert("Failed to load data from backend");
    }
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Segoe UI, sans-serif", maxWidth: "900px", margin: "auto" }}>
      <h1 style={{ fontSize: "28px", marginBottom: "20px", textAlign: "center" }}>
        🔍 Hybrid Search Engine
      </h1>
      <div style={{ marginBottom: "20px", textAlign: "center" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your search query..."
          style={{
            padding: "10px",
            width: "300px",
            border: "1px solid #aaa",
            borderRadius: "4px",
            marginRight: "10px",
          }}
        />
        <button
          onClick={handleSearch}
          style={{
            padding: "10px 20px",
            backgroundColor: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Search
        </button>
      </div>

      {results.length > 0 && <ResultsTable results={results} />}
    </div>
  );
}

export default SearchPage;
