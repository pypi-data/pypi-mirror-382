
import gradio as gr
from app import demo as app
import os

_docs = {'MediaGallery': {'description': 'Creates a gallery component that allows displaying a grid of images or videos, and optionally captions. If used as an input, the user can upload images or videos to the gallery.\nIf used as an output, the user can click on individual images or videos to view them at a higher resolution.\n', 'members': {'__init__': {'value': {'type': 'Sequence[\n        np.ndarray | PIL.Image.Image | str | Path | tuple\n    ]\n    | Callable\n    | None', 'default': 'None', 'description': 'List of images or videos to display in the gallery by default. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'file_types': {'type': 'list[str] | None', 'default': 'None', 'description': 'List of file extensions or types of files to be uploaded (e.g. [\'image\', \'.mp4\']), when this is used as an input component. "image" allows only image files to be uploaded, "video" allows only video files to be uploaded, ".mp4" allows only mp4 files to be uploaded, etc. If None, any image and video files types are allowed.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'visible': {'type': 'bool | Literal["hidden"]', 'default': 'True', 'description': 'If False, component will be hidden. If "hidden", component will be visually hidden and not take up space in the layout but still exist in the DOM'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'columns': {'type': 'int | None', 'default': '2', 'description': 'Represents the number of images that should be shown in one row.'}, 'rows': {'type': 'int | None', 'default': 'None', 'description': 'Represents the number of rows in the image grid.'}, 'height': {'type': 'int | float | str | None', 'default': 'None', 'description': 'The height of the gallery component, specified in pixels if a number is passed, or in CSS units if a string is passed. If more images are displayed than can fit in the height, a scrollbar will appear.'}, 'allow_preview': {'type': 'bool', 'default': 'True', 'description': 'If True, images in the gallery will be enlarged when they are clicked. Default is True.'}, 'preview': {'type': 'bool | None', 'default': 'None', 'description': 'If True, MediaGallery will start in preview mode, which shows all of the images as thumbnails and allows the user to click on them to view them in full size. Only works if allow_preview is True.'}, 'selected_index': {'type': 'int | None', 'default': 'None', 'description': 'The index of the image that should be initially selected. If None, no image will be selected at start. If provided, will set MediaGallery to preview mode unless allow_preview is set to False.'}, 'object_fit': {'type': 'Literal[\n        "contain", "cover", "fill", "none", "scale-down"\n    ]\n    | None', 'default': 'None', 'description': 'CSS object-fit property for the thumbnail images in the gallery. Can be "contain", "cover", "fill", "none", or "scale-down".'}, 'show_share_button': {'type': 'bool | None', 'default': 'None', 'description': 'If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.'}, 'show_download_button': {'type': 'bool | None', 'default': 'True', 'description': 'If True, will show a download button in the corner of the selected image. If False, the icon does not appear. Default is True.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'If True, the gallery will be interactive, allowing the user to upload images. If False, the gallery will be static. Default is True.'}, 'type': {'type': 'Literal["numpy", "pil", "filepath"]', 'default': '"filepath"', 'description': 'The format the image is converted to before being passed into the prediction function. "numpy" converts the image to a numpy array with shape (height, width, 3) and values from 0 to 255, "pil" converts the image to a PIL image object, "filepath" passes a str path to a temporary file containing the image. If the image is SVG, the `type` is ignored and the filepath of the SVG is returned.'}, 'show_fullscreen_button': {'type': 'bool', 'default': 'True', 'description': 'If True, will show a fullscreen icon in the corner of the component that allows user to view the gallery in fullscreen mode. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.'}, 'only_custom_metadata': {'type': 'bool', 'default': 'True', 'description': 'If True, the metadata popup will filter out common technical EXIF data (like ImageWidth, ColorType, etc.), showing only custom or descriptive metadata.'}, 'popup_metadata_width': {'type': 'int | str', 'default': '500', 'description': 'The width of the metadata popup modal, specified in pixels (e.g., 500) or as a CSS string (e.g., "50%").'}}, 'postprocess': {'value': {'type': 'list | None', 'description': "The output data received by the component from the user's function in the backend."}}, 'preprocess': {'return': {'type': 'Any', 'description': "The preprocessed input data sent to the user's function in the backend."}, 'value': None}}, 'events': {'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the MediaGallery. Uses event data gradio.SelectData to carry `value` referring to the label of the MediaGallery, and `selected` to refer to state of the MediaGallery. See EventData documentation on how to use this event data'}, 'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the MediaGallery changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'delete': {'type': None, 'default': None, 'description': 'This listener is triggered when the user deletes and item from the MediaGallery. Uses event data gradio.DeletedFileData to carry `value` referring to the file that was deleted as an instance of FileData. See EventData documentation on how to use this event data'}, 'preview_close': {'type': None, 'default': None, 'description': 'This event is triggered when the MediaGallery preview is closed by the user'}, 'preview_open': {'type': None, 'default': None, 'description': 'This event is triggered when the MediaGallery preview is opened by the user'}, 'load_metadata': {'type': None, 'default': None, 'description': "Triggered when the user clicks the 'Load Metadata' button in the metadata popup. The event data will be a dictionary containing the image metadata."}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'MediaGallery': []}}}

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

- **As input:** Is passed, the preprocessed input data sent to the user's function in the backend.
- **As output:** Should return, the output data received by the component from the user's function in the backend.

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
