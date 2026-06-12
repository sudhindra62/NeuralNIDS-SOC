// frontend/src/services/websocket.js
const WS_URL = 'ws://127.0.0.1:8000/ws';

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.listeners = new Set();
        this.retryCount = 0;
        this.reconnectTimeout = null;
        this.isConnecting = false;
        this.intentionalClose = false;
        this.disconnectTimeout = null; // Used to survive React StrictMode unmount/remount
    }

    connect() {
        // Prevent overlapping connection attempts and ignore if already connected
        if (this.isConnecting || (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING))) {
            return;
        }

        // If a new connection is explicitly requested, clear any pending timeouts
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }

        this.intentionalClose = false;
        this.isConnecting = true;
        console.log('[WS] Attempting connection...');
        this.socket = new WebSocket(WS_URL);

        this.socket.onopen = () => {
            console.log('[WS] Connected Successfully');
            this.isConnecting = false;
            this.retryCount = 0; // Reset retry count on successful connection
            this.listeners.forEach(callback => callback({ type: 'WS_STATUS', data: 'Connected' }));
        };

        this.socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                if (message.type === 'PING') return;
                this.listeners.forEach(callback => callback(message));
            } catch (e) {
                console.error('[WS] Malformed Message:', event.data);
            }
        };

        this.socket.onclose = (event) => {
            this.isConnecting = false;
            this.socket = null;
            this.listeners.forEach(callback => callback({ type: 'WS_STATUS', data: 'Disconnected' }));
            
            if (this.intentionalClose) {
                console.log(`[WS] Connection closed intentionally.`);
                return; // Do not reconnect if closed intentionally
            }
            
            console.log(`[WS] Disconnected (code: ${event.code}). Attempting reconnect.`);
            this.scheduleReconnect();
        };

        this.socket.onerror = (error) => {
            console.error('[WS] Error:', error);
            // Error triggers onclose automatically
        };
    }

    scheduleReconnect() {
        if (this.intentionalClose) return;
        if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
        
        // Exponential backoff: 1s, 2s, 4s, 8s, 16s, up to 30s
        const delay = Math.min(1000 * Math.pow(2, this.retryCount), 30000);
        console.log(`[WS] Reconnecting in ${delay/1000}s (Attempt ${this.retryCount + 1})`);
        
        this.reconnectTimeout = setTimeout(() => {
            this.retryCount++;
            this.connect();
        }, delay);
    }

    subscribe(callback) {
        this.listeners.add(callback);
        
        // Clear any pending disconnect since we have a new subscriber
        if (this.disconnectTimeout) {
            clearTimeout(this.disconnectTimeout);
            this.disconnectTimeout = null;
        }
        
        // Ensure we are connected
        this.connect();
        
        return () => {
            this.listeners.delete(callback);
            
            // If no more listeners, set a timeout to close the socket
            // This 3-second delay allows the socket to survive React StrictMode unmount/remount
            if (this.listeners.size === 0) {
                this.disconnectTimeout = setTimeout(() => {
                    this.close();
                }, 3000);
            }
        };
    }

    close() {
        this.intentionalClose = true;
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        if (this.disconnectTimeout) {
            clearTimeout(this.disconnectTimeout);
            this.disconnectTimeout = null;
        }
        
        if (this.socket) {
            this.socket.onclose = null; // Prevent onclose from triggering a reconnect loop
            this.socket.close();
            this.socket = null;
        }
        this.isConnecting = false;
        console.log('[WS] Connection completely closed.');
    }
}

export const wsManager = new WebSocketManager();