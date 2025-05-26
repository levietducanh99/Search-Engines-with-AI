const API_BASE_URL = 'http://localhost:8000';

export const searchService = {
    async search(query, page = 1, pageSize = 10) {
        try {
            const response = await fetch(
                `${API_BASE_URL}/api/v1/search?query=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`,
                {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Search error:', error);
            throw error;
        }
    },

    async searchReranked(query, page = 1, pageSize = 10) {
        try {
            const response = await fetch(
                `${API_BASE_URL}/api/v1/search/reranked?query=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`,
                {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Reranked search error:', error);
            throw error;
        }
    }
}; 