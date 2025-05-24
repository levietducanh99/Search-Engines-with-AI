import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import ResultsTable from './components/ResultsTable';
import { searchService } from './api/searchService';
import './App.css';

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (query) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchService.search(query);
      setResults(data.results || []);
    } catch (err) {
      setError('Có lỗi xảy ra khi tìm kiếm. Vui lòng thử lại sau.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Tìm kiếm thông minh</h1>
      </header>
      <main className="app-main">
        <SearchBar onSearch={handleSearch} />
        {error && <div className="error-message">{error}</div>}
        <ResultsTable results={results} loading={loading} />
      </main>
    </div>
  );
}

export default App;
