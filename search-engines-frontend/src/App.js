import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import ResultsTable from './components/ResultsTable';
import { searchService } from './api/searchService';
import './App.css';

function App() {
  const [searchType, setSearchType] = useState('full'); // 'full' or 'reranked'
  const [results, setResults] = useState({
    keyword_results: [],
    semantic_results: [],
    rrf_results: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  const handleSearch = async (query) => {
    setLoading(true);
    setError(null);
    try {
      let data;
      if (searchType === 'full') {
        data = await searchService.search(query, page, pageSize);
        setResults({
          keyword_results: data.keyword_results || [],
          semantic_results: data.semantic_results || [],
          rrf_results: data.rrf_results || []
        });
      } else {
        data = await searchService.searchReranked(query, page, pageSize);
        setResults({
          keyword_results: [],
          semantic_results: [],
          rrf_results: data || []
        });
      }
    } catch (err) {
      setError('Có lỗi xảy ra khi tìm kiếm. Vui lòng thử lại sau.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
    // Trigger search again with new page
    if (results.rrf_results.length > 0) {
      handleSearch(results.rrf_results[0].query);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Tìm kiếm thông minh</h1>
      </header>
      <main className="app-main">
        <SearchBar onSearch={handleSearch} />

        <div className="search-type-tabs">
          <button
            className={`tab-button ${searchType === 'full' ? 'active' : ''}`}
            onClick={() => setSearchType('full')}
          >
            Tìm kiếm đầy đủ
          </button>
          <button
            className={`tab-button ${searchType === 'reranked' ? 'active' : ''}`}
            onClick={() => setSearchType('reranked')}
          >
            Chỉ kết quả RRF
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {searchType === 'full' ? (
          <>
            <h2>Kết quả từ khóa</h2>
            <ResultsTable
              results={results.keyword_results}
              loading={loading}
              type="keyword"
            />

            <h2>Kết quả ngữ nghĩa</h2>
            <ResultsTable
              results={results.semantic_results}
              loading={loading}
              type="semantic"
            />

            <h2>Kết quả kết hợp (RRF)</h2>
            <ResultsTable
              results={results.rrf_results}
              loading={loading}
              type="rrf"
            />
          </>
        ) : (
          <>
            <h2>Kết quả RRF</h2>
            <ResultsTable
              results={results.rrf_results}
              loading={loading}
              type="rrf"
            />
          </>
        )}

        {results.rrf_results.length > 0 && (
          <div className="pagination">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
            >
              Trang trước
            </button>
            <span>Trang {page}</span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={results.rrf_results.length < pageSize}
            >
              Trang sau
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
