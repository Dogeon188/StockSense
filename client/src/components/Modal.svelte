<script lang="ts">
    let {
        showModal = $bindable(),
        closeString = 'Close',
        header,
        children,
        onclose,
    }: {
        showModal: boolean;
        closeString?: string;
        header?: () => any;
        children?: () => any;
        onclose?: (e: Event) => void;
    } = $props();

    let dialog: HTMLDialogElement = $state() as HTMLDialogElement;

    $effect(() => {
        if (showModal) {
            dialog.showModal();
        }
    });
</script>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
<dialog
    bind:this={dialog}
    onclose={(e) => (showModal = false, onclose?.(e))}
    onclick={(e) => {
        if (e.target === dialog) dialog.close();
    }}
>
    <article>
        {@render header?.()}
        <hr />
        {@render children?.()}
        <hr />
        <footer>
            <button onclick={() => dialog.close()}>{closeString}</button>
        </footer>
    </article>
</dialog>

<style lang="sass">
    dialog
        flex-direction: column
        & > div
            padding: 1em
    dialog[open]
        display: flex
        animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)
        &::backdrop
            animation: fade 0.2s ease-out
    @keyframes zoom
        from
            transform: scale(0.95)
        to 
            transform: scale(1)
    @keyframes fade 
        from 
            opacity: 0		
        to 
            opacity: 1
</style>
