import React, { useState, useEffect } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [searchHistory, setSearchHistory] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);

    // Load search history from local storage on component mount
    useEffect(() => {
        const savedHistory = localStorage.getItem('searchHistory');
        if (savedHistory) {
            try {
                setSearchHistory(JSON.parse(savedHistory).slice(0, 5));
            } catch (e) {
                console.error('Error parsing search history', e);
                setSearchHistory([]);
            }
        }
    }, []);

    // Save search to history
    const saveToHistory = (searchQuery) => {
        const trimmedQuery = searchQuery.trim();
        const updatedHistory = [
            trimmedQuery,
            ...searchHistory.filter(item => item !== trimmedQuery)
        ].slice(0, 5);

        setSearchHistory(updatedHistory);
        localStorage.setItem('searchHistory', JSON.stringify(updatedHistory));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);
        try {
            await onSearch(query);
            saveToHistory(query);
        } finally {
            setIsLoading(false);
            setShowSuggestions(false);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setQuery(suggestion);
        setShowSuggestions(false);
        onSearch(suggestion);
        saveToHistory(suggestion);
    };

    const handleInputFocus = () => {
        if (searchHistory.length > 0) {
            setShowSuggestions(true);
        }
    };

    const handleClearSearch = () => {
        setQuery('');
    };

    return (
        <div className="search-bar-container">
            <form onSubmit={handleSubmit} className="search-form">
                <div className="search-container">
                    <div className="search-input-wrapper">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onFocus={handleInputFocus}
                            placeholder="Nhập từ khóa tìm kiếm..."
                            className="search-input"
                            disabled={isLoading}
                        />
                        {query && (
                            <button
                                type="button"
                                className="clear-button"
                                onClick={handleClearSearch}
                            >
                                ×
                            </button>
                        )}
                    </div>
                    <button
                        type="submit"
                        className={`search-button ${isLoading ? 'loading' : ''}`}
                        disabled={isLoading || !query.trim()}
                    >
                        {isLoading ? 'Đang tìm...' : 'Tìm kiếm'}
                    </button>
                </div>

                {/* Search suggestions */}
                {showSuggestions && searchHistory.length > 0 && (
                    <div className="search-suggestions">
                        <div className="suggestions-header">
                            <span>Lịch sử tìm kiếm</span>
                            <button
                                className="clear-history-button"
                                onClick={() => {
                                    setSearchHistory([]);
                                    localStorage.removeItem('searchHistory');
                                    setShowSuggestions(false);
                                }}
                            >
                                Xóa lịch sử
                            </button>
                        </div>
                        <ul className="suggestions-list">
                            {searchHistory.map((item, index) => (
                                <li
                                    key={index}
                                    className="suggestion-item"
                                    onClick={() => handleSuggestionClick(item)}
                                >
                                    <span className="history-icon">↑</span>
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </form>

            <div className="search-tips">
                <p>Gợi ý: Sử dụng các từ khóa cụ thể để có kết quả tìm kiếm tốt hơn</p>
            </div>
        </div>
    );
};

export default SearchBar;
