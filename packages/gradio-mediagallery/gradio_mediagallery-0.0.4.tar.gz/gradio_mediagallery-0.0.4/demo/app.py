from typing import Any, List
import gradio as gr
from gradio_folderexplorer import FolderExplorer
from gradio_folderexplorer.helpers import load_media_from_folder
from gradio_mediagallery import MediaGallery
from gradio_mediagallery.helpers import transfer_metadata

# Configuration constant for the root directory containing media files
ROOT_DIR_PATH = "./src/examples"

def handle_load_metadata(image_data: gr.EventData) -> List[Any]:
    """
    Processes image metadata by calling the `transfer_metadata` helper.

    Args:
        image_data (gr.EventData): Event data containing metadata from the MediaGallery component.

    Returns:
        List[Any]: A list of values to populate the output fields, or skipped updates if no data is provided.
    """
    if not image_data or not hasattr(image_data, "_data"):
        return [gr.skip()] * len(output_fields)

    return transfer_metadata(
        output_fields=output_fields,
        metadata=image_data._data,
        remove_prefix_from_keys=True
    )

# UI layout and logic
with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    """
    A Gradio interface for browsing and displaying media files with metadata extraction.
    """
    gr.Markdown("# MediaGallery with Metadata Extraction")
    gr.Markdown(
        """
        **To Test:**
        1. Use the **FolderExplorer** on the left to select a folder containing images with metadata.
        2. Click on an image in the **Media Gallery** to open the preview mode.
        3. In the preview toolbar, click the 'Info' icon (ⓘ) to open the metadata popup.
        4. Click the **'Load Metadata'** button inside the popup.
        5. The fields in the **Metadata Viewer** below will be populated with the data from the image.
        """
    )
    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=300):
            folder_explorer = FolderExplorer(
                label="Select a Folder",
                root_dir=ROOT_DIR_PATH,
                value=ROOT_DIR_PATH
            )

        with gr.Column(scale=3):
            gallery = MediaGallery(
                label="Media in Folder",
                columns=6,
                height="auto",
                preview=False,
                show_download_button=False,
                only_custom_metadata=False,
                popup_metadata_width="40%",
            )

    gr.Markdown("## Metadata Viewer")
    with gr.Row():
        model_box = gr.Textbox(label="Model")
        fnumber_box = gr.Textbox(label="FNumber")
        iso_box = gr.Textbox(label="ISOSpeedRatings")
        s_churn = gr.Slider(label="Schurn", minimum=0.0, maximum=1.0, step=0.01)
        description_box = gr.Textbox(label="Description", lines=2)

    # Event handling
    output_fields = [
        model_box,
        fnumber_box,
        iso_box,
        s_churn,
        description_box
    ]

    # Populate the gallery when the folder changes
    folder_explorer.change(
        fn=load_media_from_folder,
        inputs=folder_explorer,
        outputs=gallery
    )

    # Populate the gallery on initial load
    demo.load(
        fn=load_media_from_folder,
        inputs=folder_explorer,
        outputs=gallery
    )

    # Handle the load_metadata event from MediaGallery
    gallery.load_metadata(
        fn=handle_load_metadata,
        inputs=None,
        outputs=output_fields
    )

if __name__ == "__main__":
    """
    Launches the Gradio interface in debug mode.
    """
    demo.launch(debug=True)