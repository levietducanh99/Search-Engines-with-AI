import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);
        try {
            await onSearch(query);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="search-form">
            <div className="search-container">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Nhập từ khóa tìm kiếm..."
                    className="search-input"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    className={`search-button ${isLoading ? 'loading' : ''}`}
                    disabled={isLoading}
                >
                    {isLoading ? 'Đang tìm...' : 'Tìm kiếm'}
                </button>
            </div>
        </form>
    );
};

export default SearchBar;
