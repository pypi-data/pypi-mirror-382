class EncryptionService {
  constructor(secretKey) {
    this.secretKey = secretKey;
    this.cryptoKey = null;
  }

  async initialize() {
    this.cryptoKey = await this.importKey(this.secretKey);
    return this;
  }

  async importKey(keyString) {
    const encoder = new TextEncoder();
    const keyData = encoder.encode(keyString);

    // Generate a 32-byte key using SHA-256
    const hash = await window.crypto.subtle.digest('SHA-256', keyData);

    return await window.crypto.subtle.importKey(
      "raw",
      hash,
      { name: "AES-GCM" },
      false,
      ["encrypt", "decrypt"]
    );
  }

  async encryptData(data) {
    const encoder = new TextEncoder();
    const encodedData = encoder.encode(JSON.stringify(data));

    // Generate a 12-byte IV
    const iv = window.crypto.getRandomValues(new Uint8Array(12));

    // Encrypt the data using AES-GCM
    const encryptedBuffer = await window.crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv: iv,
        tagLength: 128 // Specify tag length as 128 bits
      },
      this.cryptoKey,
      encodedData
    );

    // Convert to Uint8Array for consistent handling
    const encryptedArray = new Uint8Array(encryptedBuffer);

    return {
      encrypted: Array.from(encryptedArray), // Full encrypted data including auth tag
      iv: Array.from(iv)
    };
  }

  async decryptData(encryptedData) {
    try {
      // Convert arrays to Uint8Array
      const encrypted = new Uint8Array(encryptedData.encrypted);
      const iv = new Uint8Array(encryptedData.iv);

      // Decrypt the data
      const decryptedBuffer = await window.crypto.subtle.decrypt(
        {
          name: "AES-GCM",
          iv: iv,
          tagLength: 128 // Match the encryption tag length
        },
        this.cryptoKey,
        encrypted
      );

      // Decode the decrypted data
      const decoder = new TextDecoder();
      const decodedData = decoder.decode(decryptedBuffer);

      return JSON.parse(decodedData);
    } catch (error) {
      console.error('Decryption error:', error);
      throw new Error('Failed to decrypt data');
    }
  }
};


class User {
  constructor(uid, access_token, crypto_key) {
    this.uid = uid;
    this.access_token = access_token;
    this.crypto_key = crypto_key;
  }

  encryptData = async data => {
    const encrypter = await new EncryptionService(this.crypto_key).initialize();
    return await encrypter.encryptData({ access_token: this.access_token, ...data })
  }

  decryptData = async responseData => {
    const encrypter = await new EncryptionService(this.crypto_key).initialize();

    // If the response is encrypted, decrypt it
    if (responseData.encrypted) {
      return await encrypter.decryptData(responseData.data);
    }

    return responseData;
  }
}


class WebSocketManager {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.pendingRequests = new Map();
    this.rotationInterval = 20 * 60 * 1000; // Rotate every 20 minutes
    this.requestIdCounter = 0;
    this.isDev = import.meta.env.DEV || window.location.hostname === 'localhost';
    this.interval = null;
    this.isWindowFocused = true;
    this.focusListenersAttached = false;
    this.isInitialized = false;

    this.init();
  }

  async init() {
    while(typeof window === 'undefined') {
        await new Promise(r => setTimeout(r, 500));
        console.log('Waiting on Window');
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

    console.log('wsUrl', wsUrl);

    this.url = wsUrl;
    
    // Check actual focus state before initializing
    this.isWindowFocused = !document.hidden && document.hasFocus();
    console.log('Initial focus state:', this.isWindowFocused);
    
    this._attachFocusListeners();
    this.isInitialized = true;
    this._init();
  }

  _init() {
    this._connect();
    this.interval = setInterval(() => this._rotateConnection(), this.rotationInterval);
  }

  _cleanup() {
    if(this.interval) clearInterval(this.interval);
    if(this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Attaches window focus/blur event listeners
   */
  _attachFocusListeners() {
    if (this.focusListenersAttached) return;

    window.addEventListener('focus', () => {
      console.log('🔆 Window gained focus');
      this.isWindowFocused = true;
      this._handleFocusChange();
    });

    window.addEventListener('blur', () => {
      console.log('🌙 Window lost focus');
      this.isWindowFocused = false;
      this._handleFocusChange();
    });

    // Also listen to visibility change (for tab switching)
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        console.log('👁️ Tab hidden');
        this.isWindowFocused = false;
      } else {
        console.log('👁️ Tab visible');
        this.isWindowFocused = true;
      }
      this._handleFocusChange();
    });

    this.focusListenersAttached = true;
  }

  /**
   * Handles window focus changes
   */
  _handleFocusChange() {
    // Don't handle focus changes until fully initialized
    if (!this.isInitialized) return;
    
    if (this.isWindowFocused) {
      // Window gained focus - reconnect if disconnected
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        console.log('🔌 Reconnecting due to window focus...');
        this._connect();
      }
    } else {
      // Window lost focus - disconnect
      console.log('🔌 Disconnecting due to window blur...');
      this._cleanup();
    }
  }

  changeUrl(url) {
    this.url = url;
    this._cleanup();
    this._init();
  }

  changeRotationInterval(rotationInterval) {
    this.rotationInterval = rotationInterval;
    this._cleanup();
    this._init();
  }

  /**
   * Establishes the WebSocket connection.
   */
  _connect() {
    console.log("🔌 Attempting to connect...");
    const socket = new WebSocket(this.url);

    socket.onopen = () => {
      console.log("✅ WebSocket connection established.");
      this.ws = socket;
    };

    socket.onmessage = (event) => {
      this._handleMessage(event);
    };

    socket.onclose = () => {
      console.warn("⚠️ WebSocket connection closed.");
      this.ws = null;
      
      // Only auto-reconnect if window is focused
      if (this.isWindowFocused) {
        console.log("Reconnecting in 3 seconds...");
        setTimeout(() => {
          if (this.isWindowFocused) {
            this._connect();
          }
        }, 3000);
      } else {
        console.log("Not reconnecting - window is not focused");
      }
    };

    socket.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
      socket.close(); // This will trigger the onclose handler
    };
    
    // Return the socket so the rotation logic can use it
    return socket;
  }

  /**
   * Handles incoming messages and resolves pending promises.
   */
  _handleMessage(event) {
    try {
      const response = JSON.parse(event.data);
      if (this.pendingRequests.has(response.request_id)) {
        const promise = this.pendingRequests.get(response.request_id);
        if (response.error) {
          promise.reject(new Error(response.error));
        } else {
            user.decryptData(response.body)
            .then(promise.resolve)
            .catch(response.error);
        }
        this.pendingRequests.delete(response.request_id);
      }
    } catch (e) {
      console.error("Error parsing message:", e);
    }
  }

  /**
   * Gracefully rotates the WebSocket connection to avoid timeouts.
   */
  _rotateConnection() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        console.log("Skipping rotation, connection not open.");
        return;
    }
    
    // Don't rotate if window is not focused
    if (!this.isWindowFocused) {
        console.log("Skipping rotation, window not focused.");
        return;
    }
    
    console.log("🔄 Initiating connection rotation...");
    const oldSocket = this.ws;
    
    // Create the new connection and set it as the primary
    this.ws = this._connect();
    
    // After a grace period, close the old socket. This gives time for any
    // in-flight responses to be received by its onmessage handler.
    setTimeout(() => {
        console.log("⏲️ Closing old socket after grace period.");
        oldSocket.close();
    }, 30 * 1000); // 30-second grace period
  }

  /**
   * Sends a request to the server and returns a promise that resolves with the response.
   * @param {string} method - The method to be called on the server.
   * @param {object} body - The data payload for the method.
   * @returns {Promise<any>}
   */
  api(method, body) {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        return reject(new Error("WebSocket is not connected."));
      }

      const requestId = this.requestIdCounter++;
      this.pendingRequests.set(requestId, { resolve, reject });

      // Timeout for the request
      setTimeout(() => {
        if (this.pendingRequests.has(requestId)) {
          this.pendingRequests.delete(requestId);
          reject(new Error(`Request ${requestId} timed out.`));
        }
      }, 60 * 1000); // 60-second timeout

      
      user.encryptData(body)
      .then(encryptedData => {
        this.ws.send(JSON.stringify({
          uid: user.uid,
          request_id: requestId,
          method: method,
          body: encryptedData,
        }));
      })
    });
  }
}


const user = new User(null, null, null);
const wsManager = new WebSocketManager(null);


const setup = ({
  url,
  uid, 
  access_token, 
  crypto_key,
}) => {
  user.uid = uid;
  user.access_token = access_token;
  user.crypto_key = crypto_key;

  wsManager.changeUrl(url);
};


const api = async ({ method, body }) => {
  return await wsManager.api(method, body);
}


export {
  user,
  wsManager,
  setup,
  api,
};