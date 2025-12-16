const axios = require('axios');

class PythonAIClient {
    constructor() {
        this.baseURL = process.env.PYTHON_AI_SERVICE_URL || 'http://localhost:8000';
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 30000, // 30 seconds
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    /**
     * Analyze a natural language question
     * @param {Object} params - { store_id, question, access_token }
     * @returns {Promise<Object>} AI analysis response
     */
    async analyze({ store_id, question, access_token }) {
        try {
            console.log(`🤖 Calling Python AI service at ${this.baseURL}/analyze`);

            const response = await this.client.post('/analyze', {
                store_id,
                question,
                access_token: access_token || null,
                use_mock: process.env.USE_MOCK_DATA === 'true'
            });

            return response.data;

        } catch (error) {
            if (error.code === 'ECONNREFUSED') {
                throw new Error(
                    `Cannot connect to Python AI service at ${this.baseURL}. ` +
                    'Ensure the service is running.'
                );
            }

            if (error.response) {
                // Service returned an error response
                console.error(`Python AI service error: ${error.response.status}`, error.response.data);
                throw error;
            }

            throw new Error(`Python AI service error: ${error.message}`);
        }
    }

    /**
     * Health check for Python AI service
     * @returns {Promise<boolean>}
     */
    async healthCheck() {
        try {
            const response = await this.client.get('/health');
            return response.data.status === 'ok';
        } catch (error) {
            return false;
        }
    }
}

module.exports = PythonAIClient;
