from __future__ import annotations
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, Union
from urllib.parse import urlparse
import PIL.Image
import numpy as np
from gradio_client import handle_file, utils as client_utils
from gradio_client.utils import is_http_url_like
from gradio import processing_utils, utils
from gradio.components.base import Component
from gradio.data_classes import FileData, GradioModel, GradioRootModel, ImageData
from gradio.events import Events, EventListener
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer

class GalleryImage(GradioModel):
    """Data model for a gallery image."""
    image: ImageData
    caption: str | None = None

class GalleryVideo(GradioModel):
    """Data model for a gallery video."""
    video: FileData
    caption: str | None = None

class GalleryData(GradioRootModel):
    """Root data model for gallery items, containing a list of images or videos."""
    root: list[Union[GalleryImage, GalleryVideo]]

class MediaGallery(Component):
    """
    A Gradio component for displaying a grid of images or videos with optional captions.
    Supports preview mode for enlarged viewing and metadata extraction for images.
    Can be used as an input for uploading media or as an output for displaying media.

    Demos: fake_gan, gif_maker
    """

    EVENTS = [
        Events.select,
        Events.change,
        Events.delete,
        EventListener(
            "preview_close",
            doc="Triggered when the MediaGallery preview is closed by the user."
        ),
        EventListener(
            "preview_open",
            doc="Triggered when the MediaGallery preview is opened by the user."
        ),
        EventListener(
            "load_metadata",
            doc="Triggered when the user clicks the 'Load Metadata' button in the metadata popup. Returns a dictionary of image metadata."
        ),
    ]

    data_model = GalleryData

    def __init__(
        self,
        value: (
            Sequence[np.ndarray | PIL.Image.Image | str | Path | tuple]
            | Callable
            | None
        ) = None,
        *,
        file_types: list[str] | None = None,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool | Literal["hidden"] = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        columns: int | None = 2,
        rows: int | None = None,
        height: int | float | str | None = None,
        allow_preview: bool = True,
        preview: bool | None = None,
        selected_index: int | None = None,
        object_fit: (
            Literal["contain", "cover", "fill", "none", "scale-down"] | None
        ) = None,
        show_share_button: bool | None = None,
        show_download_button: bool | None = True,
        interactive: bool | None = None,
        type: Literal["numpy", "pil", "filepath"] = "filepath",
        show_fullscreen_button: bool = True,
        only_custom_metadata: bool = True,
        popup_metadata_width: int | str = 500
    ):
        """
        Initializes the MediaGallery component.

        Args:
            value: Initial list of images or videos, or a function to generate them.
            file_types: List of allowed file extensions or types for uploads (e.g., ['image', '.mp4']).
            label: Label displayed above the component.
            every: Interval or Timer to refresh `value` if it's a function.
            inputs: Components used as inputs to recalculate `value` if it's a function.
            show_label: Whether to display the label.
            container: Whether to place the component in a padded container.
            scale: Relative size compared to adjacent components.
            min_width: Minimum pixel width of the component.
            visible: Whether the component is visible or hidden.
            elem_id: HTML ID for the component.
            elem_classes: HTML classes for the component.
            render: Whether to render the component in the Blocks context.
            key: Identifier for preserving component state across re-renders.
            preserved_by_key: Parameters to preserve during re-renders.
            columns: Number of columns in the grid.
            rows: Number of rows in the grid.
            height: Height of the gallery in pixels or CSS units.
            allow_preview: Whether images can be enlarged on click.
            preview: Whether to start in preview mode (requires allow_preview=True).
            selected_index: Index of the initially selected media item.
            object_fit: CSS object-fit for thumbnails ("contain", "cover", etc.).
            show_share_button: Whether to show a share button (auto-enabled on Hugging Face Spaces).
            show_download_button: Whether to show a download button for the selected media.
            interactive: Whether the gallery allows uploads.
            type: Format for images passed to the prediction function ("numpy", "pil", "filepath").
            show_fullscreen_button: Whether to show a fullscreen button.
            only_custom_metadata: Whether to filter out technical EXIF metadata in the popup.
            popup_metadata_width: Width of the metadata popup (pixels or CSS string).
        """
        self.columns = columns
        self.rows = rows
        self.height = height
        self.preview = preview
        self.object_fit = object_fit
        self.allow_preview = allow_preview
        self.show_download_button = (
            (utils.get_space() is not None)
            if show_download_button is None
            else show_download_button
        )
        self.selected_index = selected_index
        if type not in ["numpy", "pil", "filepath"]:
            raise ValueError(
                f"Invalid type: {type}. Must be one of ['numpy', 'pil', 'filepath']"
            )
        self.type = type
        self.show_fullscreen_button = show_fullscreen_button
        self.file_types = file_types
        self.only_custom_metadata = only_custom_metadata
        self.popup_metadata_width = popup_metadata_width
        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
            interactive=interactive,
        )
        self._value_description = f"a list of {'string filepaths' if type == 'filepath' else 'numpy arrays' if type == 'numpy' else 'PIL images'}"

    def preprocess(self, payload: GalleryData | None) -> Any:
        """
        Preprocesses the gallery data for use in a prediction function.

        Args:
            payload: Gallery data containing images or videos.

        Returns:
            List of tuples containing file paths and captions, or None if payload is None.
        """
        if payload is None:
            return None
        return [
            (item.video.path if isinstance(item, GalleryVideo) else item.image.path, item.caption)
            for item in payload.root
        ]

    def postprocess(self, value: list | None) -> GalleryData:
        """
        Postprocesses input media to create a GalleryData object for display.

        Args:
            value: List of media items (images, videos, or tuples with captions).

        Returns:
            GalleryData object containing processed media items.
        """
        if value is None:
            return GalleryData(root=[])
        
        if isinstance(value, str):
            raise ValueError(
                "The `value` passed into `gr.Gallery` must be a list of images or videos, or list of (media, caption) tuples."
            )
            
        output_items = []

        def _save_item(item):
            img, caption = (item, None) if not isinstance(item, (tuple, list)) else item
            orig_name = Path(img.filename).name if hasattr(img, 'filename') and img.filename else None

            if isinstance(img, np.ndarray):
                file = processing_utils.save_img_array_to_cache(img, cache_dir=self.GRADIO_CACHE, format="png")
                file_path = str(utils.abspath(file))
                url = None
            elif isinstance(img, PIL.Image.Image):
                file = processing_utils.save_pil_to_cache(img, cache_dir=self.GRADIO_CACHE, format=str(img.format).lower())
                file_path = str(utils.abspath(file))
                url = None
            elif isinstance(img, (str, Path)):
                file_path = str(img)
                if not orig_name:
                    orig_name = Path(file_path).name
                url = file_path if is_http_url_like(file_path) else None
            else:
                raise ValueError(f"Cannot process type: {type(img)}")

            mime_type = client_utils.get_mimetype(file_path)

            if mime_type and "video" in mime_type:
                file = processing_utils.save_file_to_cache(img, cache_dir=self.GRADIO_CACHE)
                file_path = str(utils.abspath(file))
                return GalleryVideo(
                    video=FileData(path=file_path, url=url, orig_name=orig_name, mime_type=mime_type),
                    caption=caption
                )
            else:
                return GalleryImage(
                    image=ImageData(path=file_path, url=url, orig_name=orig_name, mime_type=mime_type),
                    caption=caption
                )

        with ThreadPoolExecutor() as executor:
            for item in executor.map(_save_item, value):
                if item:
                    output_items.append(item)

        return GalleryData(root=output_items)

    @staticmethod
    def convert_to_type(img: str, type: Literal["filepath", "numpy", "pil"]):
        """
        Converts an image to the specified format.

        Args:
            img: Path to the image file.
            type: Target format ("filepath", "numpy", or "pil").

        Returns:
            Image in the specified format.
        """
        if type == "filepath":
            return img
        else:
            converted_image = PIL.Image.open(img)
            if type == "numpy":
                converted_image = np.array(converted_image)
            return converted_image

    def example_payload(self) -> Any:
        """
        Provides an example payload for the gallery.

        Returns:
            List containing a sample image dictionary.
        """
        return [
            {
                "image": handle_file(
                    "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
                )
            },
        ]

    def example_value(self) -> Any:
        """
        Provides an example value for the gallery.

        Returns:
            List containing a sample image URL.
        """
        return [
            "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
        ]