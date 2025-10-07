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