const SERVER_URL = "ws://10.0.0.3:8887";


const sleep = ms => new Promise(r => setTimeout(r, ms));

function openWebSocket() {
    return new WebSocket(SERVER_URL);
}

let sessionId = null;
let clientId = null;


async function messageDispatcher(msg) {
    let inner = unwrap(JSON.parse(msg.data));
    let msgType = inner["type"];
    console.log(msgType);
    let content = inner["content"];
    console.log(content);
    switch (msgType) {
        case "InitSessionMessage":
            sessionId = content.session_id;
            clientId = content.client_id;
            break;
    }
}


function wrap(obj) {
    return { "inner": obj };
}


function unwrap(obj) {
    return obj["inner"];
}


function sendCreateParagraphSessionMessage(ws) {
    ws.send(JSON.stringify(wrap({
        "type": "1CreateParagraphSessionMessage", "content": {
            "session_id": sessionId,
            "client_id": clientId,
        }
    })))
}


async function main() {
    const ws = openWebSocket();
    ws.onmessage = messageDispatcher;
    ws.onopen = async () => {
        await sleep(1000);
        for (let index = 0; index < 10; index++) {
            sendCreateParagraphSessionMessage(ws);
        }
    }
}
