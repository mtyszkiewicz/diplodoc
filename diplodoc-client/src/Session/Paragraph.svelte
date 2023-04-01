<script lang="ts">
    import { createEventDispatcher } from "svelte";

    import { slide, fade } from "svelte/transition";
    import LButton from "../LButton.svelte";
    import Button from "../Button.svelte";
    import RButton from "../RButton.svelte";
    import SmallText from "../SmallText.svelte";
    import FaRegTrashAlt from "svelte-icons/fa/FaRegTrashAlt.svelte";
    import FaEdit from "svelte-icons/fa/FaEdit.svelte";
    import FaSave from "svelte-icons/fa/FaSave.svelte";
    import snarkdown from "snarkdown";

    export let paragraphId;
    export let content: string = "";
    export let state: string;
    export let editedBy: string;
    let editElement: HTMLParagraphElement;
    $: renderedContent = snarkdown(content);
    $: editElement === undefined || editElement === null || (editElement.innerText = content)

    const dispath = createEventDispatcher();

    function handleDelete(evt) {
        evt.stopPropagation();
        dispath("deleteParagraph", { paragraphId });
    }

    function handleEdit(evt) {
        evt.stopPropagation();
        dispath("editParagraph", { paragraphId });
    }

    function handleSave(evt) {
        evt.stopPropagation();
        dispath("saveParagraph", {
            paragraphId,
            content: editElement.innerText,
        });
    }
</script>

<section
    class="paragraph"
    class:paragraph-hover={state == "EDITABLE"}
    on:click={handleEdit}
>
    {#if state === "EDITABLE" || state === "BUSY"}
        <p in:slide={{ duration: 200 }} out:slide={{ duration: 200 }}>
            {@html renderedContent}
        </p>
    {/if}
    {#if state === "EDITING"}
        <p
            contenteditable
            class="editing"
            bind:this={editElement}
            in:slide={{ duration: 200 }}
            out:slide={{ duration: 200 }}
        />
        <section
            class="bottom"
            in:slide={{ duration: 200 }}
            out:slide={{ duration: 200 }}
        >
            <LButton on:click={handleDelete}>
                <span class="icon">
                    <FaRegTrashAlt />
                </span>
            </LButton>
            <RButton on:click={handleSave}>
                <span class="icon">
                    <FaSave />
                </span>
            </RButton>
        </section>
    {:else if state == "BUSY"}
        <section
            class="bottom busy"
            in:slide={{ duration: 200 }}
            out:slide={{ duration: 200 }}
        >
            <section
                class="paragraph-id"
                in:fade={{ duration: 200, delay: 200 }}
            >
                <SmallText>
                    Client {editedBy} is editing this paragraph
                </SmallText>
            </section>
        </section>
    {/if}
</section>

<style>
    .paragraph {
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        width: 100%;
        transition: 300ms;
    }

    section.bottom.busy {
        height: 0;
        margin: 0;
    }

    .paragraph-hover:hover {
        background-color: #f5f5f5;
    }

    p {
        margin: 2rem;
        /* text-align: justify; */
        padding: 1rem;
    }

    p.editing {
        outline: 1px solid #ececec;
        border-radius: 0.25rem;
    }

    .bottom {
        margin: 2rem;
        margin-top: 0;
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
        position: relative;
        right: -20rem;
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
        box-shadow: 8px 8px 24px 0px rgba(66, 68, 90, 0.12);
        padding: 2rem;
    }

    .editor {
        width: 100%;
        margin-left: -2rem;
        margin-right: -2rem;
        box-sizing: content-box;
    }
</style>
