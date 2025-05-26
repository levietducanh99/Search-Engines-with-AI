import React from "react";
import "./ResultTable.css"; // tạo thêm file css riêng nếu muốn

const ResultsTable = ({ results, loading, type }) => {
  if (loading) {
    return <div className="loading">Đang tìm kiếm...</div>;
  }

  if (!results || results.length === 0) {
    return <div className="no-results">Không tìm thấy kết quả nào</div>;
  }

  const getTableHeaders = () => {
    switch (type) {
      case 'keyword':
        return (
          <tr>
            <th>Tiêu đề</th>
            <th>Nội dung</th>
            <th>Điểm BM25</th>
            <th>Từ khóa</th>
            <th>Số từ khóa khớp</th>
          </tr>
        );
      case 'semantic':
        return (
          <tr>
            <th>Tiêu đề</th>
            <th>Nội dung</th>
            <th>Điểm ngữ nghĩa</th>
            <th>Ngữ cảnh</th>
            <th>Số khái niệm khớp</th>
          </tr>
        );
      case 'rrf':
        return (
          <tr>
            <th>Tiêu đề</th>
            <th>Nội dung</th>
            <th>Điểm BM25</th>
            <th>Điểm ngữ nghĩa</th>
            <th>Điểm RRF</th>
            <th>Thứ hạng</th>
            <th>Từ khóa</th>
            <th>Ngữ cảnh</th>
          </tr>
        );
      default:
        return null;
    }
  };

  const renderResultRow = (result) => {
    switch (type) {
      case 'keyword':
        return (
          <tr key={result.id} className="result-row">
            <td className="title-cell">{result.title}</td>
            <td className="content-cell">{result.content}</td>
            <td className="score-cell">{result.bm25_score?.toFixed(2) || '-'}</td>
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
            <td className="count-cell">{result.matched_count || '-'}</td>
          </tr>
        );
      case 'semantic':
        return (
          <tr key={result.id} className="result-row">
            <td className="title-cell">{result.title}</td>
            <td className="content-cell">{result.content}</td>
            <td className="score-cell">
              {result.semantic_score ? (result.semantic_score * 100).toFixed(1) + '%' : '-'}
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
            <td className="count-cell">{result.matched_count || '-'}</td>
          </tr>
        );
      case 'rrf':
        return (
          <tr key={result.id} className="result-row">
            <td className="title-cell">{result.title}</td>
            <td className="content-cell">{result.content}</td>
            <td className="score-cell">{result.bm25_score?.toFixed(2) || '-'}</td>
            <td className="score-cell">
              {result.semantic_score ? (result.semantic_score * 100).toFixed(1) + '%' : '-'}
            </td>
            <td className="score-cell">{result.rrf_score?.toFixed(2) || '-'}</td>
            <td className="rank-cell">{result.ranking || '-'}</td>
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
        );
      default:
        return null;
    }
  };

  return (
    <div className="results-container">
      <table className="results-table">
        <thead>{getTableHeaders()}</thead>
        <tbody>
          {results.map(renderResultRow)}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;
