// Conversation memory for follow-up questions
class ConversationMemory {
    constructor(maxHistoryPerSession = 10) {
        this.sessions = new Map();
        this.maxHistory = maxHistoryPerSession;
    }

    createSession(sessionId) {
        if (!this.sessions.has(sessionId)) {
            this.sessions.set(sessionId, {
                history: [],
                createdAt: Date.now(),
                lastActivity: Date.now()
            });
        }
        return sessionId;
    }

    addInteraction(sessionId, question, answer) {
        let session = this.sessions.get(sessionId);

        if (!session) {
            session = this.createSession(sessionId);
            session = this.sessions.get(sessionId);
        }

        session.history.push({
            question,
            answer,
            timestamp: Date.now()
        });

        // Keep only last N interactions
        if (session.history.length > this.maxHistory) {
            session.history = session.history.slice(-this.maxHistory);
        }

        session.lastActivity = Date.now();
    }

    getHistory(sessionId, limit = 5) {
        const session = this.sessions.get(sessionId);
        if (!session) return [];

        return session.history.slice(-limit);
    }

    getContext(sessionId) {
        const session = this.sessions.get(sessionId);
        if (!session || session.history.length === 0) {
            return null;
        }

        const recent = session.history.slice(-3);
        return {
            previousQuestions: recent.map(h => h.question),
            previousAnswers: recent.map(h => h.answer),
            conversationLength: session.history.length
        };
    }

    clearSession(sessionId) {
        this.sessions.delete(sessionId);
    }

    // Clean up old sessions (older than 1 hour)
    cleanup(maxAgeMs = 3600000) {
        const now = Date.now();
        for (const [sessionId, session] of this.sessions.entries()) {
            if (now - session.lastActivity > maxAgeMs) {
                this.sessions.delete(sessionId);
            }
        }
    }

    getStats() {
        return {
            activeSessions: this.sessions.size,
            sessions: Array.from(this.sessions.entries()).map(([id, session]) => ({
                sessionId: id,
                interactions: session.history.length,
                lastActivity: new Date(session.lastActivity).toISOString()
            }))
        };
    }
}

// Singleton instance
const conversationMemory = new ConversationMemory(10);

// Auto-cleanup every 30 minutes
setInterval(() => {
    conversationMemory.cleanup();
}, 30 * 60 * 1000);

module.exports = conversationMemory;
