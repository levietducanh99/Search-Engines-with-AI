import React from "react";

function ResultsTable({ results }) {
    return (
        <table style={{ width: "80%", borderCollapse: "collapse" }}>
            <thead>
            <tr>
                <th style={thStyle}>Ranking</th>
                <th style={thStyle}>Title</th>
                <th style={thStyle}>BM25 Score</th>
                <th style={thStyle}>Semantic Score</th>
            </tr>
            </thead>
            <tbody>
            {results.map((result, index) => (
                <tr key={index}>
                    <td style={tdStyle}>{result.ranking}</td>
                    <td style={tdStyle}>{result.title}</td>
                    <td style={tdStyle}>{result.bm25_score.toFixed(2)}</td>
                    <td style={tdStyle}>{result.semantic_score.toFixed(2)}</td>
                </tr>
            ))}
            </tbody>
        </table>
    );
}

const thStyle = { border: "1px solid #aaa", padding: "8px", backgroundColor: "#f2f2f2" };
const tdStyle = { border: "1px solid #aaa", padding: "8px", textAlign: "center" };

export default ResultsTable;
