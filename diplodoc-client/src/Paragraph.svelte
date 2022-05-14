<script lang="ts">
    import { createEventDispatcher } from "svelte";

    import { slide } from "svelte/transition";
    export let paragraphId;

    const dispath = createEventDispatcher();

    function handleDelete() {
        dispath("deleteParagraph", { paragraphId: paragraphId });
    }
</script>

<section in:slide out:slide >
    <small>{paragraphId}</small>
    <button on:click={handleDelete}>Delete</button>
    <input type="text" />
</section>

<style>
    section {
        border-radius: 2rem;
        box-shadow: 8px 8px 24px 0px rgba(66, 68, 90, 0.21);
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>
