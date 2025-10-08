<script context="module" lang="ts">
    /** Exports the base Gallery and Example components for use in other modules. */
    export { default as BaseGallery } from "./shared/Gallery.svelte";
    export { default as BaseExample } from "./Example.svelte";
</script>

<script lang="ts">
    import type { GalleryImage, GalleryVideo } from "./types";
    import type { Gradio, SelectData } from "@gradio/utils";
    import { Block, Empty } from "@gradio/atoms";
    import Gallery from "./shared/Gallery.svelte";
    import type { LoadingStatus } from "@gradio/statustracker";
    import { StatusTracker } from "@gradio/statustracker";
    import { Image } from "@gradio/icons";
    import "./Gallery.css";

    /** Union type for gallery items, either images or videos. */
    type GalleryData = GalleryImage | GalleryVideo;

    /** @prop {LoadingStatus} loading_status - Status of the component's loading state. */
    export let loading_status: LoadingStatus;
    /** @prop {boolean} show_label - Whether to display the gallery label. */
    export let show_label: boolean;
    /** @prop {string} label - The label text for the gallery. */
    export let label: string;
    /** @prop {string} elem_id - HTML ID for the component. Defaults to "". */
    export let elem_id = "";
    /** @prop {string[]} elem_classes - HTML classes for the component. Defaults to []. */
    export let elem_classes: string[] = [];
    /** @prop {boolean | "hidden"} visible - Whether the component is visible or hidden. Defaults to true. */
    export let visible: boolean | "hidden" = true;
    /** @prop {GalleryData[] | null} value - Array of gallery items (images or videos). Defaults to null. */
    export let value: GalleryData[] | null = null;
    /** @prop {boolean} container - Whether to place the component in a padded container. Defaults to true. */
    export let container = true;
    /** @prop {number | null} scale - Relative size compared to adjacent components. Defaults to null. */
    export let scale: number | null = null;
    /** @prop {number | undefined} min_width - Minimum pixel width of the component. Defaults to undefined. */
    export let min_width: number | undefined = undefined;
    /** @prop {number | number[] | undefined} columns - Number of grid columns or array of column counts per breakpoint. Defaults to [5]. */
    export let columns: number | number[] | undefined = [5];
    /** @prop {number | "auto"} height - Gallery height in pixels or "auto". Defaults to "auto". */
    export let height: number | "auto" = "auto";
    /** @prop {boolean} preview - Whether to start in preview mode. Defaults to true. */
    export let preview: boolean = true;
    /** @prop {boolean} allow_preview - Whether preview mode is enabled. Defaults to true. */
    export let allow_preview = true;
    /** @prop {number | null} selected_index - Index of the selected media item. Defaults to null. */
    export let selected_index: number | null = null;
    /** @prop {"contain" | "cover" | "fill" | "none" | "scale-down"} object_fit - CSS object-fit for media. Defaults to "cover". */
    export let object_fit: "contain" | "cover" | "fill" | "none" | "scale-down" = "cover";
    /** @prop {Gradio} gradio - Gradio interface for dispatching events. */
    export let gradio: Gradio<{
        change: typeof value;
        select: SelectData;
        share: ShareData;
        error: string;
        prop_change: Record<string, any>;
        clear_status: LoadingStatus;
        preview_open: never;
        preview_close: never;
        load_metadata: Record<string, any>;
    }>;
    /** @prop {boolean} show_fullscreen_button - Whether to show the fullscreen button. Defaults to true. */
    export let show_fullscreen_button = true;
    /** @prop {boolean} show_download_button - Whether to show the download button. Defaults to false. */
    export let show_download_button = false;
    /** @prop {boolean} show_share_button - Whether to show the share button. Defaults to false. */
    export let show_share_button = false;
    /** @prop {boolean} fullscreen - Whether the gallery is in fullscreen mode. Defaults to false. */
    export let fullscreen = false;
    /** @prop {number | string} popup_metadata_width - Width of the metadata popup. Defaults to "50%". */
    export let popup_metadata_width: number | string = "50%";
</script>

<Block
    {visible}
    variant={value === null || value.length === 0 ? "dashed" : "solid"}
    padding={false}
    {elem_id}
    {elem_classes}
    {container}
    {scale}
    {min_width}
    allow_overflow={false}
    height={typeof height === "number" ? height : undefined}
    bind:fullscreen
>
    <StatusTracker
        autoscroll={gradio.autoscroll}
        i18n={gradio.i18n}
        {...loading_status}
    />
    {#if value === null || value.length === 0}
        <Empty unpadded_box={true} size="large"><Image /></Empty>
    {:else}
        <Gallery
            on:change={() => gradio.dispatch("change", value)}
            on:select={(e) => gradio.dispatch("select", e.detail)}
            on:share={(e) => gradio.dispatch("share", e.detail)}
            on:error={(e) => gradio.dispatch("error", e.detail)}
            on:preview_open={() => gradio.dispatch("preview_open")}
            on:preview_close={() => gradio.dispatch("preview_close")}
            on:fullscreen={({ detail }) => {
                fullscreen = detail;
            }}
            on:load_metadata={(e) => gradio.dispatch("load_metadata", e.detail)}
            {label}
            {show_label}
            {columns}
            height={"auto"}
            {preview}
            {object_fit}
            {allow_preview}
            bind:selected_index
            bind:value
            i18n={gradio.i18n}
            _fetch={(...args) => gradio.client.fetch(...args)}
            {show_fullscreen_button}
            {show_download_button}
            {show_share_button}
            {fullscreen}
            {popup_metadata_width}
        />
    {/if}
</Block>