<script lang="ts">
    import { createEventDispatcher } from "svelte";

    import { slide, fly } from "svelte/transition";
    import LButton from "../LButton.svelte";
    import Button from "../Button.svelte";
    import RButton from "../RButton.svelte";
    import SmallText from "../SmallText.svelte";
    import FaRegTrashAlt from "svelte-icons/fa/FaRegTrashAlt.svelte";
    import FaEdit from "svelte-icons/fa/FaEdit.svelte";
    import FaSave from "svelte-icons/fa/FaSave.svelte";
    import FaInfoCircle from "svelte-icons/fa/FaInfoCircle.svelte";

    export let paragraphId;
    export let content: string = "";
    export let state: string;
    export let editedBy: string;

    const dispath = createEventDispatcher();

    function handleDelete(evt) {
        evt.stopPropagation();
        dispath("deleteParagraph", { paragraphId: paragraphId });
    }

    function handleEdit(evt) {
        evt.stopPropagation();
        dispath("editParagraph", { paragraphId: paragraphId });
    }

    function handleSave(evt) {
        evt.stopPropagation();
        dispath("saveParagraph", {
            paragraphId: paragraphId,
            content: content,
        });
    }
</script>

<section in:slide out:slide class="paragraph">
    {#if state === "EDITING"}
        <span in:slide={{ delay: 100 }} out:slide={{ delay: 100 }}>
            <SmallText>PREVIEW</SmallText>
        </span>
    {/if}
    <p in:slide={{ delay: 100 }} out:slide={{ delay: 100 }}>
        {content}
    </p>
    {#if state === "EDITING"}
        <span in:slide={{ delay: 100 }} out:slide={{ delay: 100 }}>
            <SmallText>EDITOR</SmallText>
            <br />
            <textarea bind:value={content} cols="40" />
        </span>
    {/if}
    <br />
    {#if state === "EDITABLE"}
        <section
            class="bottom"
            in:slide={{ delay: 100 }}
            out:slide={{ delay: 100 }}
        >
            <section class="paragraph-id">
                <SmallText>Paragraph ID: {paragraphId}</SmallText>
            </section>
            <Button on:click={handleEdit}>
                <span class="icon">
                    <FaEdit />
                </span>
                Edit
            </Button>
        </section>
    {:else if state == "EDITING"}
        <section
            class="bottom"
            in:slide={{ delay: 100 }}
            out:slide={{ delay: 100 }}
        >
            <section class="paragraph-id">
                <SmallText>Paragraph ID: {paragraphId}</SmallText>
            </section>
            <LButton on:click={handleDelete}>
                <span class="icon">
                    <FaRegTrashAlt />
                </span>
                Delete
            </LButton>
            <RButton on:click={handleSave}>
                <span class="icon">
                    <FaSave />
                </span>
                Save
            </RButton>
        </section>
    {:else if state == "BUSY"}
        <section
            class="bottom"
            in:slide={{ delay: 100 }}
            out:slide={{ delay: 100 }}
        >
            <section class="paragraph-id">
                <SmallText>Paragraph ID: {paragraphId}</SmallText> <br />
                <SmallText>
                    Client {editedBy} is editing this paragraph
                </SmallText>
            </section>
        </section>
    {/if}
</section>

<style>
    .paragraph {
        border-radius: 2rem;
        box-shadow: 8px 8px 24px 0px rgba(66, 68, 90, 0.21);
        margin: 2rem 0;
        padding: 2rem;
        display: flex;
        flex-direction: column;
        width: 100%;
    }

    p {
        margin-top: 0;
        text-align: justify;
    }

    .bottom {
        display: flex;
        flex-direction: row;
        align-items: flex-end;
        justify-content: flex-end;
    }

    .icon {
        height: 1rem;
        display: inline-block;
    }

    .paragraph-id {
        justify-self: start;
        flex-grow: 1;
    }

    textarea {
        width: 100%;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        box-sizing: border-box;
        resize: none;
        height: 12rem;
        border-radius: 0.5rem;
        border-style: none;
        box-shadow: 8px 8px 24px 0px rgba(66, 68, 90, 0.21);
        padding: 2rem;
    }
</style>
