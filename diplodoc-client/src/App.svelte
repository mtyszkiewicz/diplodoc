<script lang="ts">
    import Paragraph from "./Paragraph.svelte";
    import { slide } from "svelte/transition";
    export let name: string;

    const SERVER_URL = "ws://10.0.0.3:8887";

    function openWebSocket() {
        return new WebSocket(SERVER_URL);
    }

    let sessionId = null;
    let clientId = null;
    let paragraphs = {};

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
            case "UpdatedParagraphSessionMessage":
                paragraphs[content.paragraph_id] = content;
                break;
            case "ParagraphGoneSessionMessage":
                delete paragraphs[content.paragraph_id];
                paragraphs = paragraphs;
                break;
        }
    }

    function wrap(obj) {
        return { inner: obj };
    }

    function unwrap(obj) {
        return obj["inner"];
    }

    function sendCreateParagraphSessionMessage() {
        ws.send(
            JSON.stringify(
                wrap({
                    type: "CreateParagraphSessionMessage",
                    content: {
                        session_id: sessionId,
                        client_id: clientId,
                    },
                })
            )
        );
    }

    function deleteParagraph(evt) {
        ws.send(
            JSON.stringify(
                wrap({
                    type: "DeleteParagraphSessionMessage",
                    content: {
                        session_id: sessionId,
                        paragraph_id: evt.detail.paragraphId,
                        client_id: clientId,
                    },
                })
            )
        );
    }

    const ws = openWebSocket();
    ws.onmessage = messageDispatcher;
</script>

<main>
    <p>
        Session ID: {sessionId}
    </p>
    <p>
        Client ID: {clientId}
    </p>
    <ul>
        {#each Object.values(paragraphs) as p}
            <Paragraph paragraphId={p.paragraph_id} on:deleteParagraph={deleteParagraph}/>
        {/each}
    </ul>
    <button on:click={sendCreateParagraphSessionMessage} transition:slide>
        Add paragraph
    </button>
</main>

<style>
    main {
        text-align: center;
        padding: 1em;
        max-width: 240px;
        margin: 0 auto;
    }

    h1 {
        color: #ff3e00;
        text-transform: uppercase;
        font-size: 4em;
        font-weight: 100;
    }

    @media (min-width: 640px) {
        main {
            max-width: none;
        }
    }
</style>
