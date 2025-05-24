import React from "react";
import "./ResultTable.css"; // tạo thêm file css riêng nếu muốn

const ResultsTable = ({ results, loading }) => {
  if (loading) {
    return <div className="loading">Đang tìm kiếm...</div>;
  }

  if (!results || results.length === 0) {
    return <div className="no-results">Không tìm thấy kết quả nào</div>;
  }

  return (
    <div className="results-container">
      <table className="results-table">
        <thead>
          <tr>
            <th>Tiêu đề</th>
            <th>Nội dung</th>
            <th>Điểm BM25</th>
            <th>Điểm ngữ nghĩa</th>
            <th>Từ khóa</th>
            <th>Ngữ cảnh</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result) => (
            <tr key={result.id} className="result-row">
              <td className="title-cell">{result.title}</td>
              <td className="content-cell">{result.content}</td>
              <td className="score-cell">
                {result.bm25_score ? result.bm25_score.toFixed(2) : '-'}
              </td>
              <td className="score-cell">
                {result.semantic_score ? (result.semantic_score * 100).toFixed(1) + '%' : '-'}
              </td>
              <td className="keywords-cell">
                {result.keywords ? (
                  <div className="keywords-list">
                    {result.keywords.map((keyword, index) => (
                      <span key={index} className="keyword-tag">
                        {keyword}
                      </span>
                    ))}
                  </div>
                ) : '-'}
              </td>
              <td className="context-cell">
                {result.semantic_context ? (
                  <div className="context-list">
                    {result.semantic_context.map((context, index) => (
                      <span key={index} className="context-tag">
                        {context}
                      </span>
                    ))}
                  </div>
                ) : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;
