---
tags: [gradio-custom-component, gallery]
title: gradio_mediagallery
short_description: A gradio custom component
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_mediagallery`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20blue"> <a href="https://huggingface.co/spaces/elismasilva/gradio_mediagallery"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Demo-blue"></a><p><span>💻 <a href='https://github.com/DEVAIEXP/gradio_component_mediagallery'>Component GitHub Code</a></span></p>

Python library for easily interacting with trained machine learning models

## Installation

```bash
pip install gradio_mediagallery gradio_folderexplorer
```

## Usage

```python
from typing import Any, List
import gradio as gr
from gradio_folderexplorer import FolderExplorer
from gradio_folderexplorer.helpers import load_media_from_folder
from gradio_mediagallery import MediaGallery
from gradio_mediagallery.helpers import extract_metadata, transfer_metadata
import os



# --- Configuration Constants ---
ROOT_DIR_PATH = "./examples" # Use uma pasta com imagens com metadados para teste

# --- Event Callback Function ---

# Esta função é chamada quando o evento `load_metadata` é disparado do frontend.
def handle_load_metadata(image_data: gr.EventData) -> List[Any]:
    """
    Processes image metadata by calling the agnostic `transfer_metadata` helper.
    """
    if not image_data or not hasattr(image_data, "_data"):
        return [gr.skip()] * len(output_fields)

    # Call the agnostic helper function to do the heavy lifting.
    return transfer_metadata(
        output_fields=output_fields,
        metadata=image_data._data,      
        remove_prefix_from_keys=True
    )

# --- UI Layout and Logic ---

with gr.Blocks() as demo:
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
            # Usando nosso MediaGallery customizado
            gallery = MediaGallery(
                label="Media in Folder",
                columns=6,
                height="auto",
                preview=False,
                show_download_button=False,
                only_custom_metadata=False, # Agora mostra todos os metadados
                popup_metadata_width="40%",  # Popup mais largo
                
            )

    gr.Markdown("## Metadata Viewer")
    with gr.Row():
        model_box = gr.Textbox(label="Model")
        fnumber_box = gr.Textbox(label="FNumber")
        iso_box = gr.Textbox(label="ISOSpeedRatings")
        s_churn = gr.Slider(label="Schurn", minimum=0.0, maximum=1.0, step=0.01)
        description_box = gr.Textbox(label="Description", lines=2)
    # --- Event Handling ---

    # Evento para popular a galeria quando a pasta muda
    folder_explorer.change(
        fn=load_media_from_folder,
        inputs=folder_explorer,
        outputs=gallery
    )
    
    # Evento para popular a galeria no carregamento inicial
    demo.load(
        fn=load_media_from_folder,
        inputs=folder_explorer,
        outputs=gallery
    )
    
    output_fields = [
        model_box,
        fnumber_box,
        iso_box,
        s_churn,
        description_box
    ]

    # --- NOVO EVENTO DE METADADOS ---
    # Liga o evento `load_metadata` do nosso MediaGallery à função de callback.
    gallery.load_metadata(
        fn=handle_load_metadata,
        inputs=None, # O dado vem do payload do evento, não de um input explícito.
        outputs=output_fields
    )

if __name__ == "__main__":
    demo.launch(debug=True)
```

## `MediaGallery`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
Sequence[
        np.ndarray | PIL.Image.Image | str | Path | tuple
    ]
    | Callable
    | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">List of images or videos to display in the gallery by default. If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>file_types</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">List of file extensions or types of files to be uploaded (e.g. ['image', '.mp4']), when this is used as an input component. "image" allows only image files to be uploaded, "video" allows only video files to be uploaded, ".mp4" allows only mp4 files to be uploaded, etc. If None, any image and video files types are allowed.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will display label.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will place the component in a container - providing some extra padding around the border.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool | Literal["hidden"]
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden. If "hidden", component will be visually hidden and not take up space in the layout but still exist in the DOM</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>

<tr>
<td align="left"><code>columns</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>2</code></td>
<td align="left">Represents the number of images that should be shown in one row.</td>
</tr>

<tr>
<td align="left"><code>rows</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Represents the number of rows in the image grid.</td>
</tr>

<tr>
<td align="left"><code>height</code></td>
<td align="left" style="width: 25%;">

```python
int | float | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The height of the gallery component, specified in pixels if a number is passed, or in CSS units if a string is passed. If more images are displayed than can fit in the height, a scrollbar will appear.</td>
</tr>

<tr>
<td align="left"><code>allow_preview</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, images in the gallery will be enlarged when they are clicked. Default is True.</td>
</tr>

<tr>
<td align="left"><code>preview</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If True, MediaGallery will start in preview mode, which shows all of the images as thumbnails and allows the user to click on them to view them in full size. Only works if allow_preview is True.</td>
</tr>

<tr>
<td align="left"><code>selected_index</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The index of the image that should be initially selected. If None, no image will be selected at start. If provided, will set MediaGallery to preview mode unless allow_preview is set to False.</td>
</tr>

<tr>
<td align="left"><code>object_fit</code></td>
<td align="left" style="width: 25%;">

```python
Literal[
        "contain", "cover", "fill", "none", "scale-down"
    ]
    | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">CSS object-fit property for the thumbnail images in the gallery. Can be "contain", "cover", "fill", "none", or "scale-down".</td>
</tr>

<tr>
<td align="left"><code>show_share_button</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.</td>
</tr>

<tr>
<td align="left"><code>show_download_button</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will show a download button in the corner of the selected image. If False, the icon does not appear. Default is True.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If True, the gallery will be interactive, allowing the user to upload images. If False, the gallery will be static. Default is True.</td>
</tr>

<tr>
<td align="left"><code>type</code></td>
<td align="left" style="width: 25%;">

```python
Literal["numpy", "pil", "filepath"]
```

</td>
<td align="left"><code>"filepath"</code></td>
<td align="left">The format the image is converted to before being passed into the prediction function. "numpy" converts the image to a numpy array with shape (height, width, 3) and values from 0 to 255, "pil" converts the image to a PIL image object, "filepath" passes a str path to a temporary file containing the image. If the image is SVG, the `type` is ignored and the filepath of the SVG is returned.</td>
</tr>

<tr>
<td align="left"><code>show_fullscreen_button</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will show a fullscreen icon in the corner of the component that allows user to view the gallery in fullscreen mode. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.</td>
</tr>

<tr>
<td align="left"><code>only_custom_metadata</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, the metadata popup will filter out common technical EXIF data (like ImageWidth, ColorType, etc.), showing only custom or descriptive metadata.</td>
</tr>

<tr>
<td align="left"><code>popup_metadata_width</code></td>
<td align="left" style="width: 25%;">

```python
int | str
```

</td>
<td align="left"><code>500</code></td>
<td align="left">The width of the metadata popup modal, specified in pixels (e.g., 500) or as a CSS string (e.g., "50%").</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `select` | Event listener for when the user selects or deselects the MediaGallery. Uses event data gradio.SelectData to carry `value` referring to the label of the MediaGallery, and `selected` to refer to state of the MediaGallery. See EventData documentation on how to use this event data |
| `change` | Triggered when the value of the MediaGallery changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `delete` | This listener is triggered when the user deletes and item from the MediaGallery. Uses event data gradio.DeletedFileData to carry `value` referring to the file that was deleted as an instance of FileData. See EventData documentation on how to use this event data |
| `preview_close` | This event is triggered when the MediaGallery preview is closed by the user |
| `preview_open` | This event is triggered when the MediaGallery preview is opened by the user |
| `load_metadata` | Triggered when the user clicks the 'Load Metadata' button in the metadata popup. The event data will be a dictionary containing the image metadata. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, the preprocessed input data sent to the user's function in the backend.
- **As input:** Should return, the output data received by the component from the user's function in the backend.

 ```python
 def predict(
     value: Any
 ) -> list | None:
     return value
 ```
 
