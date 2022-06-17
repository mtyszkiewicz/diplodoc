<button on:click>
    <slot />
</button>

<style>
    button {
        background-color: white;
        border-radius: 2rem;
        border-style: solid;
        border-width: 2px;
        border-color: #333;
        font-weight: 600;
        padding-bottom: 0.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 0.5rem;
    }

    button:hover {
        color: white;
        background-color: #64101c;
        border-color: #64101c;
    }
</style>
