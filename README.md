<img src="./diplodoc-client/public/diplodocus.png">

# Diplodoc is a document editor
Diplodoc is a collaborative text document editor created to solidify our academic knowledge and demonstrate the fundamentals of asynchronous applications.

The solution features a client-server architecture, utilizing the Svelte JavaScript framework for the client and Python for the server. The server handles basic locking mechanisms and manages the event loop, ensuring smooth operation. Communication between the front-end and server is achieved through the exchange of serialized messages via WebSockets, enabling a basic level of asynchronous interaction between the components.

# Setup

## diplodoc-server
```bash
cd diplodoc-server
poetry install
poetry run python3 diplodoc/server.py
```

## diplodoc-client

Update `SERVER_URL` in `diplodoc-client/src/App.svelte` to match your server's ip.
```bash
cd diplodoc-client
npm install
HOST=0.0.0.0 npm run dev
```
