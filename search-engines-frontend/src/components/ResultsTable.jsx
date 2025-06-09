import React from "react";
import "./ResultTable.css";
import PropTypes from "prop-types";

// Danh sách các stopwords phổ biến cần loại bỏ khi highlight
const stopwords = [
  "a", "an", "and", "are", "as", "at", "be", "but", "by", "for",
  "if", "in", "into", "is", "it", "no", "not", "of", "on", "or",
  "such", "that", "the", "their", "then", "there", "these", "they",
  "this", "to", "was", "will", "with", "has", "have", "had"
];

// Helper function to highlight query terms in text
const highlightQueryTerms = (text, query) => {
  if (!text || !query) return text || '';

  // Xử lý truy vấn để lấy các từ khóa cần highlight
  const queryTerms = query
    .toLowerCase()
    .split(/\s+/)
    .filter(term => term.length > 2) // Bỏ qua các từ quá ngắn
    .filter(term => !stopwords.includes(term.toLowerCase())) // Loại bỏ stopwords
    .map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')); // Escape các ký tự đặc biệt

  if (queryTerms.length === 0) return text;

  // Tạo regex để tìm các từ khóa (không phân biệt hoa thường)
  const queryRegex = new RegExp(`\\b(${queryTerms.join('|')})\\b`, 'gi');

  // Thay thế các từ khóa bằng phiên bản được gạch chân
  return text.replace(queryRegex, match => {
    return `<span class="highlight-query-term">${match}</span>`;
  });
};

// Render content with query terms highlighted
const RenderContentWithHighlight = ({ content, query }) => {
  if (!content) return <span>-</span>;

  const highlightedContent = highlightQueryTerms(content, query);
  return <div dangerouslySetInnerHTML={{ __html: highlightedContent }} />;
};

// Render title with query terms highlighted
const RenderTitleWithHighlight = ({ title, query }) => {
  if (!title) return <span>-</span>;

  const highlightedTitle = highlightQueryTerms(title, query);
  return <div dangerouslySetInnerHTML={{ __html: highlightedTitle }} />;
};

// Render rank badge with special styling based on ranking position
const RenderRankBadge = ({ ranking }) => {
  if (!ranking && ranking !== 0) return <span>-</span>;

  let badgeClass = 'rank-badge';

  // Special styling for top 3 positions
  if (ranking === 1) {
    badgeClass += ' rank-badge-1';
  } else if (ranking === 2) {
    badgeClass += ' rank-badge-2';
  } else if (ranking === 3) {
    badgeClass += ' rank-badge-3';
  } else {
    badgeClass += ' rank-badge-other';
  }

  return <div className={badgeClass}>{ranking}</div>;
};

const ResultsTable = ({ results, loading, type, onResultClick, query }) => {
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
          <tr key={result.id} className="result-row" onClick={() => onResultClick(result)}>
            <td className="title-cell">
              <RenderTitleWithHighlight title={result.title} query={query} />
            </td>
            <td className="content-cell">
              <RenderContentWithHighlight content={result.content} query={query} />
            </td>
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
          <tr key={result.id} className="result-row" onClick={() => onResultClick(result)}>
            <td className="title-cell">
              <RenderTitleWithHighlight title={result.title} query={query} />
            </td>
            <td className="content-cell">
              <RenderContentWithHighlight content={result.content} query={query} />
            </td>
            <td className="score-cell">
              {result.semantic_score ? (result.semantic_score * 100).toFixed(1) + '%' : '-'}
            </td>
          </tr>
        );
      case 'rrf':
        return (
          <tr key={result.id} className="result-row" onClick={() => onResultClick(result)}>
            <td className="title-cell">
              <RenderTitleWithHighlight title={result.title} query={query} />
            </td>
            <td className="content-cell">
              <RenderContentWithHighlight content={result.content} query={query} />
            </td>
            <td className="score-cell">{result.bm25_score?.toFixed(2) || '-'}</td>
            <td className="score-cell">
              {result.semantic_score ? (result.semantic_score * 100).toFixed(1) + '%' : '-'}
            </td>
            <td className="score-cell">{result.rrf_score?.toFixed(2) || '-'}</td>
            <td className="rank-cell">
              <RenderRankBadge ranking={result.ranking} />
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
      <div className="results-info">
        <p>Nhấp vào một kết quả để xem thêm chi tiết</p>
      </div>
    </div>
  );
};

ResultsTable.propTypes = {
  results: PropTypes.array.isRequired,
  loading: PropTypes.bool.isRequired,
  type: PropTypes.string.isRequired,
  onResultClick: PropTypes.func.isRequired,
  query: PropTypes.string.isRequired
};

export default ResultsTable;
