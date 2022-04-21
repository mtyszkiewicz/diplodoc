const SERVER_URL = "ws://10.0.0.3:8887";


function openWebSocket() {
    return new WebSocket(SERVER_URL);
}


async function messageDispatcher(msg) {
    console.log(JSON.parse(msg.data).inner);
    let inner = unwrap(JSON.parse(msg.data));
    let msgType = inner["type"];
    let content = inner["content"];
    switch (msgType) {
        case "AckMessage":
        document.getElementById("buf").value = content.buf;
        break;
    }
}


function makeEventHandler(ws) {
    function EventHandler(evt) {
        pushMsg = {
            "type": "PushMessage",
            "content": {
                "c": evt.data,
                "pos": evt.target.selectionStart - 1,
                "timestamp": 0
            }
        }
        ws.send(JSON.stringify(wrap(pushMsg)))
    }
    return EventHandler;
}


function wrap(obj) {
    return { "inner": obj };
}


function unwrap(obj) {
    return obj["inner"];
}


function sendYoMessage(ws) {
    ws.send(JSON.stringify(wrap({ "type": "YoMessage", "content": {} })))
}


async function main() {
    const ws = openWebSocket();
    ws.onmessage = messageDispatcher;
    ws.onopen = () => {
        sendYoMessage(ws);
    }
    const buf = document.getElementById("buf");
    buf.value = "";
    buf.addEventListener("input", makeEventHandler(ws));
}
