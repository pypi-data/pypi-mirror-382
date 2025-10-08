
import gradio as gr
from app import demo as app
import os

_docs = {'MediaGallery': {'description': 'A Gradio component for displaying a grid of images or videos with optional captions.\nSupports preview mode for enlarged viewing and metadata extraction for images.\nCan be used as an input for uploading media or as an output for displaying media.\n', 'members': {'__init__': {'value': {'type': 'Sequence[\n        np.ndarray | PIL.Image.Image | str | Path | tuple\n    ]\n    | Callable\n    | None', 'default': 'None', 'description': 'Initial list of images or videos, or a function to generate them.'}, 'file_types': {'type': 'list[str] | None', 'default': 'None', 'description': "List of allowed file extensions or types for uploads (e.g., ['image', '.mp4'])."}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'Label displayed above the component.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': "Interval or Timer to refresh `value` if it's a function."}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': "Components used as inputs to recalculate `value` if it's a function."}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'Whether to display the label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'Whether to place the component in a padded container.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'Relative size compared to adjacent components.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'Minimum pixel width of the component.'}, 'visible': {'type': 'bool | Literal["hidden"]', 'default': 'True', 'description': 'Whether the component is visible or hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'HTML ID for the component.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'HTML classes for the component.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'Whether to render the component in the Blocks context.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': 'Identifier for preserving component state across re-renders.'}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': 'Parameters to preserve during re-renders.'}, 'columns': {'type': 'int | None', 'default': '2', 'description': 'Number of columns in the grid.'}, 'rows': {'type': 'int | None', 'default': 'None', 'description': 'Number of rows in the grid.'}, 'height': {'type': 'int | float | str | None', 'default': 'None', 'description': 'Height of the gallery in pixels or CSS units.'}, 'allow_preview': {'type': 'bool', 'default': 'True', 'description': 'Whether images can be enlarged on click.'}, 'preview': {'type': 'bool | None', 'default': 'None', 'description': 'Whether to start in preview mode (requires allow_preview=True).'}, 'selected_index': {'type': 'int | None', 'default': 'None', 'description': 'Index of the initially selected media item.'}, 'object_fit': {'type': 'Literal[\n        "contain", "cover", "fill", "none", "scale-down"\n    ]\n    | None', 'default': 'None', 'description': 'CSS object-fit for thumbnails ("contain", "cover", etc.).'}, 'show_share_button': {'type': 'bool | None', 'default': 'None', 'description': 'Whether to show a share button (auto-enabled on Hugging Face Spaces).'}, 'show_download_button': {'type': 'bool | None', 'default': 'True', 'description': 'Whether to show a download button for the selected media.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'Whether the gallery allows uploads.'}, 'type': {'type': 'Literal["numpy", "pil", "filepath"]', 'default': '"filepath"', 'description': 'Format for images passed to the prediction function ("numpy", "pil", "filepath").'}, 'show_fullscreen_button': {'type': 'bool', 'default': 'True', 'description': 'Whether to show a fullscreen button.'}, 'only_custom_metadata': {'type': 'bool', 'default': 'True', 'description': 'Whether to filter out technical EXIF metadata in the popup.'}, 'popup_metadata_width': {'type': 'int | str', 'default': '500', 'description': 'Width of the metadata popup (pixels or CSS string).'}}, 'postprocess': {'value': {'type': 'list | None', 'description': 'List of media items (images, videos, or tuples with captions).'}}, 'preprocess': {'return': {'type': 'Any', 'description': 'List of tuples containing file paths and captions, or None if payload is None.'}, 'value': None}}, 'events': {'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the MediaGallery. Uses event data gradio.SelectData to carry `value` referring to the label of the MediaGallery, and `selected` to refer to state of the MediaGallery. See EventData documentation on how to use this event data'}, 'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the MediaGallery changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'delete': {'type': None, 'default': None, 'description': 'This listener is triggered when the user deletes and item from the MediaGallery. Uses event data gradio.DeletedFileData to carry `value` referring to the file that was deleted as an instance of FileData. See EventData documentation on how to use this event data'}, 'preview_close': {'type': None, 'default': None, 'description': 'Triggered when the MediaGallery preview is closed by the user.'}, 'preview_open': {'type': None, 'default': None, 'description': 'Triggered when the MediaGallery preview is opened by the user.'}, 'load_metadata': {'type': None, 'default': None, 'description': "Triggered when the user clicks the 'Load Metadata' button in the metadata popup. Returns a dictionary of image metadata."}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'MediaGallery': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_mediagallery`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_mediagallery/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_mediagallery"></a>  
</div>

Python library for easily interacting with trained machine learning models
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_mediagallery
```

## Usage

```python
from typing import Any, List
import gradio as gr
from gradio_folderexplorer import FolderExplorer
from gradio_folderexplorer.helpers import load_media_from_folder
from gradio_mediagallery import MediaGallery
from gradio_mediagallery.helpers import transfer_metadata

# Configuration constant for the root directory containing media files
ROOT_DIR_PATH = "./src/examples"

def handle_load_metadata(image_data: gr.EventData) -> List[Any]:
    \"\"\"
    Processes image metadata by calling the `transfer_metadata` helper.

    Args:
        image_data (gr.EventData): Event data containing metadata from the MediaGallery component.

    Returns:
        List[Any]: A list of values to populate the output fields, or skipped updates if no data is provided.
    \"\"\"
    if not image_data or not hasattr(image_data, "_data"):
        return [gr.skip()] * len(output_fields)

    return transfer_metadata(
        output_fields=output_fields,
        metadata=image_data._data,
        remove_prefix_from_keys=True
    )

# UI layout and logic
with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    \"\"\"
    A Gradio interface for browsing and displaying media files with metadata extraction.
    \"\"\"
    gr.Markdown("# MediaGallery with Metadata Extraction")
    gr.Markdown(
        \"\"\"
        **To Test:**
        1. Use the **FolderExplorer** on the left to select a folder containing images with metadata.
        2. Click on an image in the **Media Gallery** to open the preview mode.
        3. In the preview toolbar, click the 'Info' icon (ⓘ) to open the metadata popup.
        4. Click the **'Load Metadata'** button inside the popup.
        5. The fields in the **Metadata Viewer** below will be populated with the data from the image.
        \"\"\"
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
    \"\"\"
    Launches the Gradio interface in debug mode.
    \"\"\"
    demo.launch(debug=True)
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `MediaGallery`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["MediaGallery"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["MediaGallery"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, list of tuples containing file paths and captions, or None if payload is None.
- **As output:** Should return, list of media items (images, videos, or tuples with captions).

 ```python
def predict(
    value: Any
) -> list | None:
    return value
```
""", elem_classes=["md-custom", "MediaGallery-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          MediaGallery: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
