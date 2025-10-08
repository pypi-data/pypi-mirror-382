<script lang="ts">
  import {
    BlockLabel,
    Empty,
    ShareButton,
    IconButton,
    IconButtonWrapper,
    FullscreenButton,
  } from "@gradio/atoms";
  import type { SelectData } from "@gradio/utils";
  import { Image } from "@gradio/image/shared";
  import { Video } from "@gradio/video/shared";
  import { dequal } from "dequal";
  import { createEventDispatcher, onMount } from "svelte";
  import { tick } from "svelte";
  import type { GalleryImage, GalleryVideo } from "../types";
  import { Download, Image as ImageIcon, Clear, Play, Info } from "@gradio/icons";
  import { FileData } from "@gradio/client";
  import { format_gallery_for_sharing } from "./utils";
  import type { I18nFormatter } from "@gradio/utils";
  import * as exifr from "exifr";

  type GalleryData = GalleryImage | GalleryVideo;

  /**
   * @component Gallery
   * @description A Svelte component for displaying a gallery of images or videos with optional preview mode, fullscreen support, and metadata popup for images.
   */

  // Component props
  /** @prop {boolean} show_label - Whether to display the gallery label. Defaults to true. */
  export let show_label = true;
  /** @prop {string} label - The label text for the gallery. */
  export let label: string;
  /** @prop {GalleryData[] | null} value - Array of gallery items (images or videos). */
  export let value: GalleryData[] | null = null;
  /** @prop {number | number[] | undefined} columns - Number of grid columns or array of column counts per breakpoint. Defaults to [2]. */
  export let columns: number | number[] | undefined = [2];
  /** @prop {number | number[] | undefined} rows - Number of grid rows or array of row counts per breakpoint. */
  export let rows: number | number[] | undefined = undefined;
  /** @prop {number | "auto"} height - Gallery height in pixels or "auto". Defaults to "auto". */
  export let height: number | "auto" = "auto";
  /** @prop {boolean} preview - Whether to start in preview mode if a value is provided. */
  export let preview: boolean;
  /** @prop {boolean} allow_preview - Whether preview mode is enabled. Defaults to true. */
  export let allow_preview = true;
  /** @prop {"contain" | "cover" | "fill" | "none" | "scale-down"} object_fit - CSS object-fit for media. Defaults to "cover". */
  export let object_fit: "contain" | "cover" | "fill" | "none" | "scale-down" = "cover";
  /** @prop {boolean} show_share_button - Whether to show the share button. Defaults to false. */
  export let show_share_button = false;
  /** @prop {boolean} show_download_button - Whether to show the download button. Defaults to false. */
  export let show_download_button = false;
  /** @prop {I18nFormatter} i18n - Internationalization formatter for labels. */
  export let i18n: I18nFormatter;
  /** @prop {number | null} selected_index - Index of the selected media item. Defaults to null. */
  export let selected_index: number | null = null;
  /** @prop {boolean} interactive - Whether the gallery is interactive (not used). Defaults to false. */
  export const interactive = false;
  /** @prop {typeof fetch} _fetch - Fetch function for downloading files. */
  export let _fetch: typeof fetch;
  /** @prop {"normal" | "minimal"} mode - Display mode for the gallery. Defaults to "normal". */
  export let mode: "normal" | "minimal" = "normal";
  /** @prop {boolean} show_fullscreen_button - Whether to show the fullscreen button. Defaults to true. */
  export let show_fullscreen_button = true;
  /** @prop {boolean} display_icon_button_wrapper_top_corner - Whether to position icon buttons in the top corner. Defaults to false. */
  export let display_icon_button_wrapper_top_corner = false;
  /** @prop {boolean} fullscreen - Whether the gallery is in fullscreen mode. Defaults to false. */
  export let fullscreen = false;
  /** @prop {boolean} only_custom_metadata - Whether to show only custom metadata in the popup. Defaults to true. */
  export let only_custom_metadata: boolean = true;
  /** @prop {number | string} popup_metadata_width - Width of the metadata popup. Defaults to "50%". */
  export let popup_metadata_width: number | string = "50%";
  

  const dispatch = createEventDispatcher<{
    change: undefined;
    select: SelectData;
    preview_open: undefined;
    preview_close: undefined;
    fullscreen: boolean;
    error: string;
    load_metadata: Record<string, any>;
  }>();

  // Gallery state
  let is_full_screen = false;
  let image_container: HTMLElement;
  let was_reset = true;
  let resolved_value: GalleryData[] | null = null;
  let effective_columns: number | number[] | undefined = columns;
  let prev_value: GalleryData[] | null = value;
  let old_selected_index: number | null = selected_index;
  let el: HTMLButtonElement[] = [];
  let container_element: HTMLDivElement;
  let thumbnails_overflow = false;
  let preview_element: HTMLDivElement | null = null;

  // Metadata state
  let metadata: Record<string, any> | null = null;
  let showMetadataPopup: boolean = false;
  let is_extracting_metadata = false;
  const technicalMetadata: string[] = [
    "ImageWidth",
    "ImageHeight",
    "BitDepth",
    "ColorType",
    "Compression",
    "Filter",
    "Interlace",
  ];

  $: filteredMetadata = only_custom_metadata && metadata
    ? Object.fromEntries(
        Object.entries(metadata).filter(([key]) => !technicalMetadata.includes(key))
      )
    : metadata;

  /**
   * Extracts metadata from an image file using the exifr library.
   * @param fileData - The file data containing the image URL.
   * @returns A promise resolving to the extracted metadata or null if extraction fails or is not applicable.
   */
  async function extractMetadata(fileData: FileData): Promise<Record<string, any> | null> {
    if (!fileData?.url) return null;
    if (
      fileData.url.toLowerCase().endsWith(".png") ||
      fileData.url.toLowerCase().endsWith(".jpg") ||
      fileData.url.toLowerCase().endsWith(".jpeg")
    ) {
      try {
        const data = await exifr.parse(fileData.url, true);
        let parsed_meta: Record<string, any> = {};
        if (data) {
          for (const [key, value] of Object.entries(data)) {
            if (
              typeof value === "string" ||
              typeof value === "number" ||
              typeof value === "boolean"
            ) {
              parsed_meta[key] = value;
            }
          }
        }
        return parsed_meta;
      } catch (error) {
        return {};
      }
    }
    return null;
  }

  /**
   * Toggles the metadata popup visibility and extracts metadata if needed.
   */
  async function toggleMetadataPopup(): Promise<void> {
    if (showMetadataPopup) {
      showMetadataPopup = false;
      return;
    }
    if (!selected_media) return;
    const media_file = "image" in selected_media ? selected_media.image : null;
    if (!media_file) return;
    is_extracting_metadata = true;
    metadata = await extractMetadata(media_file);
    is_extracting_metadata = false;
    showMetadataPopup = true;
  }

  /**
   * Dispatches the load_metadata event with filtered metadata and closes the popup.
   */
  function dispatchLoadMetadata(): void {
    if (filteredMetadata !== null) {
      dispatch("load_metadata", filteredMetadata);
      closePopup();
    }
  }

  /**
   * Closes the metadata popup.
   */
  function closePopup(): void {
    showMetadataPopup = false;
  }

  $: was_reset = value == null || value.length === 0;
  $: resolved_value = value
    ? (value.map((data) =>
        "video" in data
          ? { video: data.video as FileData, caption: data.caption }
          : { image: data.image as FileData, caption: data.caption }
      ) as GalleryData[])
    : null;

  $: {
    if (resolved_value && columns) {
      const item_count = resolved_value.length;
      if (Array.isArray(columns)) {
        effective_columns = columns.map((col) => Math.min(col, item_count));
      } else {
        effective_columns = Math.min(columns, item_count);
      }
    } else {
      effective_columns = columns;
    }
  }

  $: if (!dequal(prev_value, value)) {
    selected_index = null;
    if (preview && value && value.length > 0) {
      selected_index = 0;
    }
    dispatch("change");
    prev_value = value;
  }

  $: selected_media =
    selected_index != null && resolved_value != null
      ? resolved_value[selected_index]
      : null;

  $: has_extractable_metadata =
    selected_media &&
    "image" in selected_media &&
    (selected_media.image.url?.toLowerCase().endsWith(".png") ||
      selected_media.image.url?.toLowerCase().endsWith(".jpg") ||
      selected_media.image.url?.toLowerCase().endsWith(".jpeg"));

  $: previous = ((selected_index ?? 0) + (resolved_value?.length ?? 0) - 1) % (resolved_value?.length ?? 0);
  $: next = ((selected_index ?? 0) + 1) % (resolved_value?.length ?? 0);

  /**
   * Handles click events on the preview image to navigate to the previous or next item.
   * @param event - The mouse click event.
   */
  function handle_preview_click(event: MouseEvent): void {
    const element = event.target as HTMLElement;
    const x = event.offsetX;
    const centerX = element.offsetWidth / 2;
    selected_index = x < centerX ? previous : next;
  }

  /**
   * Handles keyboard navigation in preview mode.
   * @param e - The keyboard event.
   */
  function on_keydown(e: KeyboardEvent): void {
    switch (e.code) {
      case "Escape":
        e.preventDefault();
        selected_index = null;
        dispatch("preview_close");
        break;
      case "ArrowLeft":
        e.preventDefault();
        selected_index = previous;
        break;
      case "ArrowRight":
        e.preventDefault();
        selected_index = next;
        break;
    }
  }

  $: {
    if (selected_index !== old_selected_index) {
      showMetadataPopup = false;
      metadata = null;
      old_selected_index = selected_index;
      if (selected_index !== null) {
        if (resolved_value != null) {
          selected_index = Math.max(0, Math.min(selected_index, resolved_value.length - 1));
        }
        dispatch("select", {
          index: selected_index,
          value: resolved_value?.[selected_index],
        });
      }
    }
  }

  $: if (allow_preview) {
    scroll_to_img(selected_index);
  }

  $: if (selected_index !== null && preview_element) {
    tick().then(() => {
      preview_element?.focus();
    });
  }

  /**
   * Scrolls to the selected thumbnail in the thumbnails container.
   * @param index - The index of the thumbnail to scroll to.
   */
  async function scroll_to_img(index: number | null): Promise<void> {
    if (typeof index !== "number" || !container_element) return;
    await tick();
    if (!el[index]) return;
    el[index].focus();
    const { left: container_left, width: container_width } = container_element.getBoundingClientRect();
    const { left, width } = el[index].getBoundingClientRect();
    const pos = left - container_left + width / 2 - container_width / 2 + container_element.scrollLeft;
    container_element.scrollTo({ left: pos < 0 ? 0 : pos, behavior: "smooth" });
  }

  /**
   * Downloads a file from the provided URL.
   * @param file_url - The URL of the file to download.
   * @param name - The name to use for the downloaded file.
   */
  async function download(file_url: string, name: string): Promise<void> {
    try {
      const response = await _fetch(file_url);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = name;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      if (error instanceof TypeError) {
        window.open(file_url, "_blank", "noreferrer");
        return;
      }
      throw error;
    }
  }

  /**
   * Checks if the thumbnails container overflows horizontally.
   */
  function check_thumbnails_overflow(): void {
    if (container_element) {
      thumbnails_overflow = container_element.scrollWidth > container_element.clientWidth;
    }
  }

  /**
   * Initializes the component, setting up event listeners for fullscreen and resize events.
   */
  onMount(() => {
    check_thumbnails_overflow();
    document.addEventListener("fullscreenchange", () => {
      is_full_screen = !!document.fullscreenElement;
      fullscreen = is_full_screen;
    });
    window.addEventListener("resize", check_thumbnails_overflow);
    return () => {
      window.removeEventListener("resize", check_thumbnails_overflow);
      document.removeEventListener("fullscreenchange", () => {
        is_full_screen = !!document.fullscreenElement;
        fullscreen = is_full_screen;
      });
    };
  });

  $: resolved_value, check_thumbnails_overflow();
  $: if (container_element) check_thumbnails_overflow();
</script>

<svelte:window />

{#if show_label}
  <BlockLabel {show_label} Icon={ImageIcon} label={label || "Gallery"} />
{/if}

{#if value == null || resolved_value == null || resolved_value.length === 0}
  <Empty unpadded_box={true} size="large"><ImageIcon /></Empty>
{:else}
  <div class="gallery-container" bind:this={image_container}>
    <!-- Preview Mode -->
    {#if selected_media && allow_preview}
      <button
        class="preview"
        bind:this={preview_element}
        class:minimal={mode === "minimal"}                
        aria-label="Image Preview"
        tabindex="-1"
        on:keydown={on_keydown}
      >
        <IconButtonWrapper {display_icon_button_wrapper_top_corner}>
          {#if show_download_button}
            <IconButton
              Icon={Download}
              label={i18n("common.download")}
              on:click={() => {
                const media =
                  "image" in selected_media
                    ? selected_media.image
                    : selected_media.video;
                if (media?.url) download(media.url, media.orig_name ?? "media");
              }}
            />
          {/if}
          {#if show_fullscreen_button}
            <FullscreenButton
              {fullscreen}
              on:fullscreen={() => {
                fullscreen = !fullscreen;
                if (fullscreen) {
                  preview_element?.requestFullscreen();
                } else if (document.fullscreenElement) {
                  document.exitFullscreen();
                }
              }}
            />
          {/if}
          {#if has_extractable_metadata}
            <IconButton
              Icon={Info}
              label="View Metadata"
              pending={is_extracting_metadata}
              on:click={(event) => {
                event.stopPropagation();
                toggleMetadataPopup();
              }}
            />
          {/if}
          {#if show_share_button}
            <div class="icon-button">
              <ShareButton
                {i18n}
                on:share
                on:error
                {value}
                formatter={format_gallery_for_sharing}
              />
            </div>
          {/if}
          {#if !is_full_screen}
            <IconButton
              Icon={Clear}
              label="Close"
              on:click={() => {
                selected_index = null;
                dispatch("preview_close");
              }}
            />
          {/if}
        </IconButtonWrapper>

        <button
          class="media-container"
          on:click={"image" in selected_media ? handle_preview_click : null}
        >
          {#if "image" in selected_media}
            <Image
              src={selected_media.image.url}
              alt={selected_media.caption || ""}
              loading="lazy"
            />
          {:else}
            <Video
              src={selected_media.video.url}
              alt={selected_media.caption || ""}
              loading="lazy"
              controls={true}
            />
          {/if}
      </button>

        {#if selected_media?.caption}
          <caption class="caption">{selected_media.caption}</caption>
        {/if}

        <div
          bind:this={container_element}
          class="thumbnails scroll-hide"
          style="justify-content: {thumbnails_overflow ? 'flex-start' : 'center'};"
        >
          {#each resolved_value as media, i}
            <button
              bind:this={el[i]}
              on:click={() => (selected_index = i)}
              class="thumbnail-item thumbnail-small"
              class:selected={selected_index === i && mode !== "minimal"}
              aria-label={"Thumbnail " + (i + 1) + " of " + resolved_value.length}
            >
              {#if "image" in media}
                <Image
                  src={media.image.url}
                  title={media.caption || null}
                  alt=""
                  loading="lazy"
                />
              {:else}
                <Play />
                <Video
                  src={media.video.url}
                  title={media.caption || null}
                  is_stream={false}
                  alt=""
                  loading="lazy"
                  loop={false}
                />
              {/if}
            </button>
          {/each}
        </div>

        {#if showMetadataPopup && filteredMetadata !== null}
          <div
            class="metadata-popup"
            on:click|stopPropagation
            role="presentation"
            style:width={typeof popup_metadata_width === "number" ? `${popup_metadata_width}px` : popup_metadata_width}
          >
            <div class="popup-content">
              <button class="close-button" on:click={closePopup}>X</button>
              <h3 class="popup-title">Image Metadata</h3>
              {#if Object.keys(filteredMetadata).length > 0}
                <div class="metadata-table-container">
                  <table class="metadata-table">
                    <tbody>
                      {#each Object.entries(filteredMetadata) as [key, val]}
                        {#if val}
                          <tr>
                            <td class="metadata-label">{key}</td>
                            <td class="metadata-value">{val}</td>
                          </tr>
                        {/if}
                      {/each}
                    </tbody>
                  </table>
                </div>
                <button
                  class="load-metadata-button"
                  on:click={dispatchLoadMetadata}
                >Load Metadata</button>
              {:else}
                <p class="no-metadata-message">No custom metadata found.</p>
              {/if}
            </div>
          </div>
        {/if}
      </button>
    {/if}

    <!-- Main Grid / Single Item View -->
    <div
      class="grid-wrap"
      class:minimal={mode === "minimal"}
      class:fixed-height={!height || height == "auto"}
      class:hidden={is_full_screen || (selected_media && allow_preview)}
      style:height={height !== "auto" ? `${height}px` : null}
    >
      <!-- Multi-item grid -->
      {#if resolved_value && resolved_value.length > 1}
        <div
          class="grid-container"
          style:--grid-cols={effective_columns}
          style:--grid-rows={rows}
          style:--object-fit={object_fit}
          class:pt-6={show_label}
        >
          {#each resolved_value as entry, i}
            {@const file_name = "image" in entry ? entry.image.orig_name : entry.video.orig_name}
            <div class="gallery-item-with-name">
              <div class="gallery-item">
                <button
                  class="thumbnail-item thumbnail-lg"
                  class:selected={selected_index === i}
                  on:click={() => {
                    if (selected_index === null && allow_preview)
                      dispatch("preview_open");
                    selected_index = i;
                  }}
                  aria-label={"Thumbnail " + (i + 1) + " of " + resolved_value.length}
                >
                  {#if "image" in entry}
                    <Image
                      alt={entry.caption || ""}
                      src={entry.image.url}
                      loading="lazy"
                    />
                  {:else}
                    <Play />
                    <Video
                      src={entry.video.url}
                      title={entry.caption || null}
                      is_stream={false}
                      alt=""
                      loading="lazy"
                      loop={false}
                    />
                  {/if}
                  {#if entry.caption}
                    <div class="caption-label">{entry.caption}</div>
                  {/if}
                </button>
              </div>
              {#if file_name}
                <div class="thumbnail-filename" title={file_name}>
                  {file_name}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      <!-- Single-item view -->
      {:else if resolved_value && resolved_value.length === 1}
        {@const entry = resolved_value[0]}
        {@const file_name = "image" in entry ? entry.image.orig_name : entry.video.orig_name}
        <div class="single-item-wrapper" style:--object-fit={object_fit}>
          <div class="gallery-item-with-name">
            <div class="gallery-item">
              <button
                class="thumbnail-item thumbnail-lg"
                on:click={() => {
                  if (allow_preview) {
                    dispatch("preview_open");
                    selected_index = 0;
                  }
                }}
                aria-label="View single item in preview mode"
              >
                {#if "image" in entry}
                  <Image
                    alt={entry.caption || ""}
                    src={entry.image.url}
                    loading="lazy"
                  />
                {:else}
                  <Play />
                  <Video
                    src={entry.video.url}
                    title={entry.caption || null}
                    is_stream={false}
                    alt=""
                    loading="lazy"
                    loop={false}
                  />
                {/if}
                {#if entry.caption}
                  <div class="caption-label">{entry.caption}</div>
                {/if}
              </button>
            </div>
            {#if file_name}
              <div class="thumbnail-filename" title={file_name}>
                {file_name}
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
    /**
   * Styles for the preview mode, displaying a selected media item.
   */
  .preview {
    display: flex;
    position: absolute;
    flex-direction: column;
    z-index: var(--layer-2);
    border-radius: calc(var(--block-radius) - var(--block-border-width));
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
    width: var(--size-full);
    height: var(--size-full);
  }

  .preview:focus-visible {
    outline: none;
  }

  .preview.minimal {
    width: fit-content;
    height: fit-content;
  }

  .preview::before {
    content: "";
    position: absolute;
    z-index: var(--layer-below);
    background: var(--background-fill-primary);
    opacity: 0.9;
    width: var(--size-full);
    height: var(--size-full);
  }

  /**
   * Styles for the grid wrapper with fixed height constraints.
   */
  .fixed-height {
    min-height: var(--size-80);
    max-height: 65vh;
  }

  @media (--screen-xl) {
    .fixed-height {
      min-height: 450px;
    }
  }

  /**
   * Styles for the media container in preview mode.
   */
  .media-container {
    height: calc(100% - var(--size-14));
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  .media-container :global(img),
  .media-container :global(video) {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }

  /**
   * Styles for thumbnails in the preview mode carousel.
   */
  .thumbnails :global(img) {
    object-fit: cover;
    width: var(--size-full);
    height: var(--size-full);
  }

  .thumbnails :global(svg) {
    position: absolute;
    top: var(--size-2);
    left: var(--size-2);
    width: 50%;
    height: 50%;
    opacity: 50%;
  }

  /**
   * Styles for captions in preview mode.
   */
  .caption {
    padding: var(--size-2) var(--size-3);
    overflow: hidden;
    color: var(--block-label-text-color);
    font-weight: var(--weight-semibold);
    text-align: center;
    text-overflow: ellipsis;
    white-space: nowrap;
    align-self: center;
  }

  /**
   * Styles for the thumbnails carousel in preview mode.
   */
  .thumbnails {
    display: flex;
    position: absolute;
    bottom: 0;
    justify-content: flex-start;
    align-items: center;
    gap: var(--spacing-lg);
    width: var(--size-full);
    height: var(--size-14);
    overflow-x: scroll;
  }

  /**
   * Styles for individual thumbnail items.
   */
  .thumbnail-item {
    --ring-color: transparent;
    position: relative;
    box-shadow: inset 0 0 0 1px var(--ring-color), var(--shadow-drop);
    border: 1px solid var(--border-color-primary);
    border-radius: var(--button-small-radius);
    background: var(--background-fill-secondary);
    aspect-ratio: var(--ratio-square);
    width: var(--size-full);
    height: var(--size-full);
    overflow: clip;
  }

  .thumbnail-item:hover {
    --ring-color: var(--color-accent);
    border-color: var(--color-accent);
    filter: brightness(1.1);
  }

  .thumbnail-item.selected {
    --ring-color: var(--color-accent);
    border-color: var(--color-accent);
  }

  .thumbnail-item :global(svg) {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 50%;
    height: 50%;
    opacity: 50%;
    transform: translate(-50%, -50%);
  }

  .thumbnail-item :global(video) {
    width: var(--size-full);
    height: var(--size-full);
    overflow: hidden;
    object-fit: cover;
  }

  /**
   * Styles for small thumbnails in the preview carousel.
   */
  .thumbnail-small {
    flex: none;
    transform: scale(0.9);
    transition: 0.075s;
    width: var(--size-9);
    height: var(--size-9);
  }

  .thumbnail-small.selected {
    --ring-color: var(--color-accent);
    transform: scale(1);
    border-color: var(--color-accent);
  }

  /**
   * Styles for the grid wrapper containing the gallery items.
   */
  .grid-wrap {
    position: relative;
    padding: var(--size-2);
    overflow-y: auto;
  }

  .grid-wrap.fixed-height {
    min-height: var(--size-80);
    max-height: 65vh;
  }

  /**
   * Styles for the grid container for multiple items.
   */
  .grid-container {
    display: grid;
    position: relative;
    grid-template-rows: repeat(var(--grid-rows), minmax(100px, 1fr));
    grid-template-columns: repeat(var(--grid-cols), minmax(100px, 1fr));
    grid-auto-rows: minmax(100px, 1fr);
    gap: var(--spacing-lg);
  }

  /**
   * Styles for single-item view wrapper.
   */
  .single-item-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    padding: var(--spacing-xxl);
    box-sizing: border-box;
  }

  .single-item-wrapper .gallery-item-with-name {
    width: 100%;
    height: 100%;
    max-width: min(300px, 80vw);
    max-height: min(320px, calc(80vh - var(--size-4)));
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .single-item-wrapper .gallery-item {
    width: 100%;
    height: 100%;
    max-width: 100%;
    max-height: 100%;
  }

  .single-item-wrapper .thumbnail-item.thumbnail-lg {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }

  .single-item-wrapper .thumbnail-filename {
    height: var(--size-4);
    line-height: var(--size-4);
  }

  .single-item-wrapper .thumbnail-lg > :global(img),
  .single-item-wrapper .thumbnail-lg > :global(video) {
    object-fit: var(--object-fit) !important;
  }

  /**
   * Styles for large thumbnails in the grid or single-item view.
   */
  .thumbnail-lg > :global(img),
  .thumbnail-lg > :global(video) {
    width: var(--size-full);
    height: var(--size-full);
    overflow: hidden;
    object-fit: var(--object-fit);
  }

  .thumbnail-lg:hover .caption-label {
    opacity: 0.5;
  }

  /**
   * Styles for captions in the grid or single-item view.
   */
  .caption-label {
    position: absolute;
    right: var(--block-label-margin);
    bottom: var(--block-label-margin);
    z-index: var(--layer-1);
    border-top: 1px solid var(--border-color-primary);
    border-left: 1px solid var(--border-color-primary);
    border-radius: var(--block-label-radius);
    background: var(--background-fill-secondary);
    padding: var(--block-label-padding);
    max-width: 80%;
    overflow: hidden;
    font-size: var(--block-label-text-size);
    text-align: left;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .grid-wrap.minimal {
    padding: 0;
  }

  /**
   * Styles for gallery items with associated filenames.
   */
  .gallery-item-with-name {
    display: flex;
    flex-direction: column;
    gap: var(--size-1);
    width: 100%;
    height: 100%;
  }

  .thumbnail-filename {
    font-size: var(--text-xs);
    color: var(--body-text-color);
    text-align: center;
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 0 var(--size-1);
  }

  .gallery-item {
    position: relative;
    width: 100%;
    height: 100%;
  }

  /**
   * Styles for the metadata popup displayed in preview mode.
   */
  .metadata-popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--background-fill-primary, white);
    border: 1px solid var(--border-color-primary);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    border-radius: 8px;
    max-width: min(90%, 600px);
    max-height: min(50vh, calc(100% - 2rem));
    min-height: 200px;
    display: flex;
    flex-direction: column;
    pointer-events: auto;
  }

  .popup-content {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    width: 100%;
    box-sizing: border-box;
    overflow-y: auto;
    position: relative;
  }

  .close-button {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: none;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    z-index: 20;
    color: var(--body-text-color);
    padding: 0.25rem;
    line-height: 1;
    width: 24px;
    height: 24px;
    text-align: center;
  }

  .popup-title {
    font-weight: bold;
    margin: 0 0 1rem 0;
    flex-shrink: 0;
    padding-right: 2.5rem;
  }

  .metadata-table-container {
    flex-grow: 1;
    overflow-y: auto;
    max-height: calc(100% - 5rem);
    min-height: 0;
    margin-bottom: 1rem;
  }

  .metadata-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: auto;
  }

  .metadata-label {
    background: var(--background-fill-secondary, #f5f5f5);
    padding: 0.5rem;
    font-weight: bold;
    text-align: left;
    vertical-align: top;
    width: 35%;
  }

  .metadata-value {
    text-align: left;
    padding: 0.5rem;
    white-space: pre-wrap;
    word-break: break-all;
    vertical-align: top;
  }

  .load-metadata-button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: var(--button-primary-border-color);
    color: var(--button-primary-text-color);
    border: none;
    border-radius: 4px;
    cursor: pointer;
    align-self: center;
    flex-shrink: 0;
  }

  .load-metadata-button:hover {
    background-color: var(--button-primary-background-fill-hover);
  }

  .no-metadata-message {
    flex-grow: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--body-text-color-subdued);
  }

</style>