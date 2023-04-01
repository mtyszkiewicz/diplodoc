<script lang="ts">
    export let name: string;
    import { slide } from "svelte/transition";
    import Button from "./Button.svelte";
    import FaPlus from "svelte-icons/fa/FaPlus.svelte";
    import FaInfoCircle from "svelte-icons/fa/FaInfoCircle.svelte";
    import Logo from "./Logo.svelte";
    import Paragraph from "./Session/Paragraph.svelte";
    import SmallText from "./SmallText.svelte";

    const SERVER_URL = "ws://192.168.1.10:8887";

    function openWebSocket() {
        return new WebSocket(SERVER_URL);
    }

    let sessionId = null;
    let clientId = null;
    let paragraphs = {};
    let locks = {};
    let alerts = {};

    function putAlert(message) {
        const ak = Date.now();
        alerts[ak] = message;
        setTimeout(() => {
            delete alerts[ak];
            alerts = alerts;
        }, 2000);
    }

    async function messageDispatcher(msg) {
        let inner = unwrap(JSON.parse(msg.data));
        let msgType = inner["@type"];
        let content = inner["@content"];
        switch (msgType) {
            case "InitSessionMessage":
                sessionId = content.sessionId;
                clientId = content.clientId;
                putAlert(
                    `Succesfully connected to session ${sessionId} as client ${clientId}.`
                );
                break;
            case "InitMessage":
                locks[content.lockId] = content;
                locks[content.lockId].status = determineLockState(
                    content.lockId
                );
                locks[content.lockId].trying = false;
                break;
            case "BusyMessage":
                locks[content.lockId] = content;
                locks[content.lockId].status = "BUSY";
                if (locks[content.lockId].trying) {
                    locks[content.lockId].trying = false;
                    putAlert("Another user is editing this document.");
                }
                break;
            case "ReadyMessage":
                locks[content.lockId].lockedBy = clientId;
                locks[content.lockId].status = "EDITING";
                locks[content.lockId].trying = false;
                break;
            case "FreedMessage":
                locks[content.lockId].lockedBy = null;
                locks[content.lockId].status = "EDITABLE";
                break;
            case "UpdatedParagraphSessionMessage":
                paragraphs[content.paragraphId] = content;
                if (content.updatedBy === clientId) {
                    putAlert(
                        `Paragraph ${content.paragraphId} saved successfully.`
                    );
                }
                break;
            case "ParagraphGoneSessionMessage":
                delete paragraphs[content.paragraphId];
                paragraphs = paragraphs;
                if (content.deleted_by === clientId) {
                    putAlert(
                        `Paragraph ${content.paragraphId} deleted successfully.`
                    );
                }
                break;
            case "ParagraphGoneSessionMessage":
                delete paragraphs[content.paragraphId];
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
                    "@type": "CreateParagraphSessionMessage",
                    "@content": {
                        sessionId,
                        clientId,
                    },
                })
            )
        );
    }

    function deleteParagraph(evt) {
        ws.send(
            JSON.stringify(
                wrap({
                    "@type": "DeleteParagraphSessionMessage",
                    "@content": {
                        sessionId,
                        clientId,
                        paragraphId: evt.detail.paragraphId,
                    },
                })
            )
        );
    }

    function editParagraph(evt) {
        if(locks[evt.detail.paragraphId].locked_by == clientId || locks[evt.detail.paragraph_id].trying) {
            return;
        }
        locks[evt.detail.paragraphId].trying = true;
        ws.send(
            JSON.stringify(
                wrap({
                    "@type": "TryMessage",
                    "@content": {
                        clientId,
                        lockId: evt.detail.paragraphId,
                    },
                })
            )
        );
    }

    function saveParagraph(evt) {
        ws.send(
            JSON.stringify(
                wrap({
                    "@type": "UpdateParagraphSessionMessage",
                    "@content": {
                        sessionId,
                        clientId,
                        paragraphId: evt.detail.paragraphId,
                        content: evt.detail.content,
                    },
                })
            )
        );
        ws.send(
            JSON.stringify(
                wrap({
                    "@type": "FreeMessage",
                    "@content": {
                        clientId: clientId,
                        lockId: evt.detail.paragraphId,
                    },
                })
            )
        );
    }

    function determineLockState(pid) {
        if (locks[pid].lockedBy === null) {
            return "EDITABLE";
        }

        if (locks[pid].lockedBy == clientId) {
            return "EDITING";
        }

        return "BUSY";
    }

    const ws = openWebSocket();
    ws.onmessage = messageDispatcher;
    ws.onclose = () => {
        sessionId = null;
        putAlert("Connection lost.");
    };
</script>

<main>
    <Logo />
    {#if sessionId}
        <section
            class="paragraphs-shadow"
        >
            {#each Object.keys(paragraphs) as pid (pid)}
                <Paragraph
                    paragraphId={pid}
                    state={locks[pid].status}
                    content={paragraphs[pid].content}
                    editedBy={locks[pid].lockedBy}
                    on:deleteParagraph={deleteParagraph}
                    on:editParagraph={editParagraph}
                    on:saveParagraph={saveParagraph}
                />
            {/each}
        </section>
        <section class="new-paragraph-container">
            <Button on:click={sendCreateParagraphSessionMessage}>
                <span class="icon">
                    <FaPlus />
                </span>
            </Button>
        </section>
        <SmallText>
            Session ID: {sessionId} <br />
            Client ID: {clientId}
        </SmallText>
    {/if}
    <section class="alerts">
        {#each Object.keys(alerts) as ak (ak)}
            <section class="alert" in:slide out:slide>
                <span class="icon">
                    <FaInfoCircle />
                </span>&nbsp;&nbsp;{alerts[ak]}
            </section>
        {/each}
    </section>
</main>

<style>
    section.alert {
        margin: 1rem;
        padding: 1.5rem;
        background-color: white;
        border-radius: 1.5rem;
        box-shadow: 8px 8px 24px 0px rgba(66, 68, 90, 0.4);
    }
    section.alerts {
        position: fixed;
        display: flex;
        right: 0;
        bottom: 0;
        max-width: 40%;
        z-index: 2;
        flex-direction: column;
        align-items: flex-end;
        justify-items: flex-end;
    }

    .paragraphs-shadow {
        border-radius: 0.5rem;
        box-shadow: 8px 8px 24px 0px rgba(66, 68, 90, 0.4);
        margin: 0;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0;
        width: 100%;
        block-size: fit-content;
    }

    main {
        max-width: 480px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .icon {
        height: 1rem;
        display: inline-block;
        vertical-align: text-bottom;
    }

    .new-paragraph-container {
        margin-top: 1rem;
        margin-bottom: 1rem;
        width: fit-content;
    }
</style>
