import React, { useState } from "react";
import { searchArticles } from "../api/searchApi";
import ResultsTable from "../components/ResultsTable";
import "../components/ResultTable.css";

function SearchPage() {
  const [query, setQuery] = useState("");
  const [keywordResults, setKeywordResults] = useState([]);
  const [semanticResults, setSemanticResults] = useState([]);
  const [rrfResults, setRrfResults] = useState([]);
  const [activeTab, setActiveTab] = useState("rrf");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      alert("Please enter a search query");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await searchArticles(query, 1, 10);
      setKeywordResults(data.keyword_results || []);
      setSemanticResults(data.semantic_results || []);
      setRrfResults(data.rrf_results || []);
    } catch (err) {
      console.error("Fetch failed:", err);
      setError(err.message || "Failed to load data from backend");
    } finally {
      setLoading(false);
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
      {error && <div style={{ color: "red", textAlign: "center", marginBottom: "20px" }}>Error: {error}</div>}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
        <button
          onClick={() => setActiveTab("rrf")}
          style={{
            padding: "8px 16px",
            marginRight: 8,
            backgroundColor: activeTab === "rrf" ? "#3b82f6" : "#e5e7eb",
            color: activeTab === "rrf" ? "white" : "#222",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          Kết hợp (RRF)
        </button>
        <button
          onClick={() => setActiveTab("keyword")}
          style={{
            padding: "8px 16px",
            marginRight: 8,
            backgroundColor: activeTab === "keyword" ? "#3b82f6" : "#e5e7eb",
            color: activeTab === "keyword" ? "white" : "#222",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          Từ khóa (BM25)
        </button>
        <button
          onClick={() => setActiveTab("semantic")}
          style={{
            padding: "8px 16px",
            backgroundColor: activeTab === "semantic" ? "#3b82f6" : "#e5e7eb",
            color: activeTab === "semantic" ? "white" : "#222",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          Ngữ nghĩa
        </button>
      </div>
      {activeTab === "rrf" && (
        <ResultsTable results={rrfResults} loading={loading} type="rrf" />
      )}
      {activeTab === "keyword" && (
        <ResultsTable results={keywordResults} loading={loading} type="keyword" />
      )}
      {activeTab === "semantic" && (
        <ResultsTable results={semanticResults} loading={loading} type="semantic" />
      )}
    </div>
  );
}

export default SearchPage;
