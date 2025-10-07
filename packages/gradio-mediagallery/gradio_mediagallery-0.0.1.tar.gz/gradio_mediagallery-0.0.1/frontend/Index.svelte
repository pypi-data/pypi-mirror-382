<script context="module" lang="ts">
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
	
	type GalleryData = GalleryImage | GalleryVideo;

	export let loading_status: LoadingStatus;
	export let show_label: boolean;
	export let label: string;
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible: boolean | "hidden" = true;
    // O `value` agora é uma lista simples de arquivos
	export let value: GalleryData[] | null = null;
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let columns: number | number[] | undefined = [5];
	export let height: number | "auto" = "auto";
	export let preview: boolean = true;
	export let allow_preview = true;
	export let selected_index: number | null = null;
	export let object_fit: "contain" | "cover" | "fill" | "none" | "scale-down" = "cover";	
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
	export let show_fullscreen_button = true;
	export let show_download_button = false;
	export let show_share_button = false;
	export let fullscreen = false;
	export let popup_metadata_width: number | string = "50%";  	
	import "./Gallery.css";
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

