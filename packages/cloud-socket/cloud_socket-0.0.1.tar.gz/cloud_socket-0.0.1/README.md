# ☁️ cloud-socket

A lightweight, encrypted WebSocket communication library for Python and JavaScript that enables secure real-time client-server communication with automatic connection management and end-to-end encryption.

## ✨ Features

- 🔒 **End-to-end encryption** using AES-GCM
- 🔄 **Automatic connection rotation** to prevent timeouts
- 🎯 **Smart reconnection** with window focus detection
- 📦 **Type-safe request/response** with dataclass support
- 🪝 **Decorator-based method registration**
- 🔑 **Flexible authentication** - bring your own auth system
- 📝 **Built-in logging** with customizable handlers
- ❄️ **No cold starts** when hosted in cloud functions
- 🎨 **Framework agnostic** - works with FastAPI or standalone

-----

## 🚀 Installation

```bash
pip install cloud-socket
```

You'll also need the provided `cloudSocket.js` file in your frontend project.

-----

## 📖 Learn by Example

Let's build a simple, secure echo service. This example will show you how to set up the backend, connect from the frontend, and call a Python function from JavaScript.

### Step 1: Create the Python Backend

Create a file named `main.py`. This will be our server.

The server needs two key pieces of logic from you:

1.  A function to get a user-specific secret key for encryption.
2.  A function to validate a user's access token.

<!-- end list -->

```python
# main.py
import asyncio
from dataclasses import dataclass

from cloud_socket.auth import User
from cloud_socket.app import aserve
from cloud_socket.registry import register

# This is where you'd integrate your auth system (e.g., check a JWT)
# For this example, we'll just check if the token is not empty.
async def validate_access_token(user: User) -> bool:
    print(f"Validating token for user {user.uid}...")
    return bool(user.access_token)

# This function retrieves the secret key used for E2E encryption.
# IMPORTANT: This key should be securely managed and known only to the
# user and the server.
async def get_crypto_key(user: User) -> str:
    print(f"Fetching crypto key for user {user.uid}...")
    # In a real app, you might derive this from a user-specific secret.
    return f"super-secret-key-for-{user.uid}"

# Define the structure of the request body using a dataclass.
# The `body` argument in the client's `api` call must match this.
@dataclass
class EchoPayload:
    message: str

# Use the @register decorator to expose this function to clients.
# The function signature is flexible; `cloud-socket` injects the
# arguments it needs, like the validated `user` and the `body`.
@register("echo")
async def echo(user: User, body: EchoPayload):
    print(f"User {user.uid} sent message: {body.message}")
    return {"status": "ok", "response": f"Your message was: '{body.message}'"}

# Start the server
if __name__ == "__main__":
    print("Starting Cloud Socket server on ws://localhost:8003/ws")
    asyncio.run(
        aserve(
            get_crypto_key,
            validate_access_token,
            host="localhost",
            port=8003,
        )
    )
```

### Step 2: Set Up the JavaScript Client

Place `cloudSocket.js` in your frontend source folder. Here's how you can use it in a simple React component.

```javascript
// src/App.js
import { useEffect, useState } from 'react';
import { setup, api } from './cloudSocket'; // Adjust the import path

function App() {
  const [inputValue, setInputValue] = useState('Hello, world!');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Setup the connection when the component mounts
  useEffect(() => {
    const uid = 'user-123';
    
    // In a real app, the uid, access_token, and crypto_key
    // would come from your authentication flow after a user logs in.
    setup({
      url: 'ws://localhost:8003/ws',
      uid: uid,
      access_token: 'a-valid-user-token',
      crypto_key: `super-secret-key-for-${uid}`, // Must match the backend logic
    });
  }, []);

  const handleEcho = async () => {
    if (!inputValue) return;
    setIsLoading(true);
    setResult(null);
    try {
      // Call the backend function registered as "echo"
      const response = await api({
        method: 'echo',
        body: {
          message: inputValue, // This object must match the `EchoPayload` dataclass
        },
      });
      setResult(response);
    } catch (error) {
      console.error('API call failed:', error);
      setResult({ error: error.message });
    }
    setIsLoading(false);
  };

  return (
    <div>
      <h1>Cloud Socket Echo</h1>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Enter a message"
      />
      <button onClick={handleEcho} disabled={isLoading}>
        {isLoading ? 'Sending...' : 'Send Echo'}
      </button>
      {result && (
        <pre>
          <strong>Response from server:</strong>
          <br />
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default App;
```

### Step 3: Run It\!

1.  **Start the backend server:**

    ```bash
    python main.py
    ```

2.  **Start your frontend application:**

    ```bash
    npm start 
    ```

Now, open your browser, type a message, and click the button. You'll see the response from the Python server appear on the screen\! 🎉

-----

## ⚙️ API Reference

### Backend (Python)

#### `serve()` & `aserve()`

This is the main function to start the WebSocket server.

```python
aserve(
    get_crypto_key: Callable[[User], str | Awaitable[str]],
    validate_access_token: Callable[[User], bool | Awaitable[bool]],
    host: str = 'localhost',
    port: int = 8003,
    log_handler: Callable[[CloudSocketLog], None] | None = None,
    get_user_info: Callable[[User], dict | Awaitable[dict]] | None = None,
)
```

  * **`get_crypto_key`** (required): An `async` or regular function that takes a `User` object and returns the user-specific **secret string** for deriving the encryption key.
  * **`validate_access_token`** (required): An `async` or regular function that takes a `User` object and returns `True` if their `access_token` is valid, `False` otherwise.
  * **`log_handler`** (optional): A function to process structured logs from the server.
  * **`get_user_info`** (optional): An `async` or regular function to fetch and cache additional user details, available via `await user.get_info()`.

#### `@register(method_name)`

A decorator to expose a function as an RPC endpoint. The arguments for the decorated function are automatically injected based on their type annotations.

**Supported injectable arguments:**

  * `user: User`: The authenticated `User` object, containing `uid`, `access_token`, and user info.
  * `body: <YourDataclass>` or `body: dict`: The entire decrypted payload sent from the client.
  * `<param_name>: <YourDataclass>`: If your client sends `{ "body": { "param_name": { ... } } }`, `cloud-socket` will automatically extract, validate, and deserialize `param_name` into your dataclass.

### Frontend (JavaScript)

#### `setup(config)`

Initializes and configures the WebSocket manager. Call this once when your application loads.

```javascript
setup({
    url: 'ws://your-server/ws',
    uid: 'user-id-from-auth',
    access_token: 'user-token-from-auth',
    crypto_key: 'user-secret-for-encryption',
});
```

#### `api(request)`

Sends a secure request to the backend and returns a `Promise` that resolves with the server's response.

```javascript
const response = await api({
    method: 'method_name', // The string name from @register()
    body: { /* your JSON-serializable payload */ }
});
```

-----

## 🔒 A Note on Security

`cloud-socket` is designed to provide **transport-level security**. It encrypts the *payload* of your messages end-to-end.

However, you are responsible for the initial secure handling of credentials:

  * **Authentication**: The user's `uid` and `access_token` should be obtained through a standard, secure authentication flow (e.g., OAuth, OIDC).
  * **Key Management**: The `crypto_key` is a shared secret. You must have a secure way for the client to obtain this key. It should **never** be hardcoded in the client-side source code. A common pattern is to fetch it from a secure API endpoint after the user has authenticated.