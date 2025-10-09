"""gr.HTML() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


class CreditsPanel(Component):
    """
    A Gradio component for displaying credits with customizable visual effects, such as scrolling or Star Wars-style animations.
    This component is configured via a single dictionary `value` that holds all settings.
    It supports displaying a logo, licenses, sections, and various text styling options.

    Attributes:
        EVENTS (list): Supported events for the component, currently only `change`.
    """

    EVENTS = [Events.change]

    def __init__(
        self,
        value: Dict[str, Any] | None = None,
        *,
        # Structural parameters
        height: int | str | None = None,
        width: int | str | None = None,
        # Configuration parameters (will be part of the `value` dictionary)
        credits: List[Dict[str, str]] | Callable | None = None,
        licenses: Dict[str, str | Path] | None = None,
        effect: Literal["scroll", "starwars", "matrix"] = "scroll",
        speed: float = 40.0,
        base_font_size: float = 1.5,
        intro_title: str | None = None,
        intro_subtitle: str | None = None,
        sidebar_position: Literal["right", "bottom"] = "right",
        logo_path: str | Path | None = None,
        show_logo: bool = True,
        show_licenses: bool = True,
        show_credits: bool = True,
        logo_position: Literal["center", "left", "right"] = "center",
        logo_sizing: Literal["stretch", "crop", "resize"] = "resize",
        logo_width: int | str | None = None,
        logo_height: int | str | None = None,
        scroll_background_color: str | None = None,
        scroll_title_color: str | None = None,
        scroll_name_color: str | None = None,
        scroll_section_title_color: str | None = None,
        layout_style: Literal["stacked", "two-column"] = "stacked",
        title_uppercase: bool = False,
        name_uppercase: bool = False,
        section_title_uppercase: bool = True,
        swap_font_sizes_on_two_column: bool = False,
        scroll_logo_path: str | Path | None = None,
        scroll_logo_height: str = "120px",
        # Standard Gradio parameters
        label: str | I18nData | None = None,
        every: float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool = False,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Initialize the CreditsPanel component.

        Args:
            value (Dict[str, Any], optional): The dictionary containing the component's full configuration. 
                                              If provided, it overrides all other configuration parameters.
            height (int | str | None, optional): The structural height of the component.
            width (int | str | None, optional): The structural width of the component.
            credits (List[Dict[str, str]] | Callable | None, optional): List of credits, can include section headers.
            licenses (Dict[str, str | Path] | None, optional): Dictionary mapping license names to file paths.
            effect (Literal["scroll", "starwars", "matrix"], optional): Visual effect for the credits. Defaults to "scroll".
            speed (float, optional): Animation speed in seconds. Defaults to 40.0.
            base_font_size (float, optional): Base font size in rem. Defaults to 1.5.
            intro_title (str | None, optional): Title for the intro sequence.
            intro_subtitle (str | None, optional): Subtitle for the intro sequence.
            sidebar_position (Literal["right", "bottom"], optional): Position of the licenses sidebar. Defaults to "right".
            logo_path (str | Path | None, optional): Path or URL to the main static logo.
            show_logo (bool, optional): Whether to display the main logo. Defaults to True.
            show_licenses (bool, optional): Whether to display licenses. Defaults to True.
            show_credits (bool, optional): Whether to display the credits panel. Defaults to True.
            logo_position (Literal["center", "left", "right"], optional): Main logo alignment. Defaults to "center".
            logo_sizing (Literal["stretch", "crop", "resize"], optional): Main logo sizing mode. Defaults to "resize".
            logo_width (int | str | None, optional): Main logo width.
            logo_height (int | str | None, optional): Main logo height.
            scroll_background_color (str | None, optional): Background color for the scroll effect.
            scroll_title_color (str | None, optional): Color for credit titles.
            scroll_name_color (str | None, optional): Color for credit names.
            scroll_section_title_color (str | None, optional): Color for section titles in the scroll effect.
            layout_style (Literal["stacked", "two-column"], optional): Layout for credits. Defaults to "stacked".
            title_uppercase (bool, optional): Whether to display titles in uppercase. Defaults to False.
            name_uppercase (bool, optional): Whether to display names in uppercase. Defaults to False.
            section_title_uppercase (bool, optional): Whether to display section titles in uppercase. Defaults to True.
            swap_font_sizes_on_two_column (bool, optional): Swaps title and name font sizes in two-column layout. Defaults to False.
            scroll_logo_path (str | Path | None, optional): Path or URL to a logo inside the scrolling credits.
            scroll_logo_height (str, optional): The height of the scrolling logo. Defaults to "120px".
            (Other standard Gradio arguments)
        """
        # Structural parameters are stored directly on self.
        self.height = height
        self.width = width
        
        # All other configuration parameters are bundled into a dictionary.
        # This dictionary is the component's main `value`.
        self._config = {
            "credits": credits if credits is not None else [],
            "licenses": licenses or {},
            "effect": effect,
            "speed": speed,
            "base_font_size": base_font_size,
            "intro_title": intro_title,
            "intro_subtitle": intro_subtitle,
            "sidebar_position": sidebar_position,
            "logo_path": logo_path,
            "show_logo": show_logo,
            "show_licenses": show_licenses,
            "show_credits": show_credits,
            "logo_position": logo_position,
            "logo_sizing": logo_sizing,
            "logo_width": logo_width,
            "logo_height": logo_height,
            "scroll_background_color": scroll_background_color,
            "scroll_title_color": scroll_title_color,
            "scroll_name_color": scroll_name_color,
            "scroll_section_title_color": scroll_section_title_color,
            "layout_style": layout_style,
            "title_uppercase": title_uppercase,
            "name_uppercase": name_uppercase,
            "section_title_uppercase": section_title_uppercase,
            "swap_font_sizes_on_two_column": swap_font_sizes_on_two_column,
            "scroll_logo_path": scroll_logo_path,
            "scroll_logo_height": scroll_logo_height,
        }
        
        # If a `value` dictionary is passed directly, it overrides the individual parameters.
        initial_value = value if value is not None else self._config
        
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            visible=visible,
            preserved_by_key=preserved_by_key,
            value=initial_value, # The component's state is its configuration dictionary.
        )

    def _process_image_path(self, image_path: str | Path | None) -> Dict[str, Any] | None:
        """Helper function to process an image path, handling local files and URLs."""
        if not image_path:
            return None
        path = str(image_path)
        if is_http_url_like(path):
            return {"path": None, "url": path, "orig_name": Path(path).name, "mime_type": None}
        if os.path.exists(path):
            return handle_file(path)
        return None

    def preprocess(self, payload: Dict[str, Any] | None) -> Dict[str, Any] | None:
        """
        Passes the payload from the frontend through, unmodified.
        """
        return payload

    def postprocess(self, value: Dict[str, Any] | None) -> Dict[str, Any] | None:
        """
        Processes the component's `value` dictionary to prepare data for the frontend.
        This involves resolving file paths for licenses and images.
        
        Args:
            value (Dict[str, Any] | None): The component's configuration dictionary.

        Returns:
            Dict[str, Any] | None: The processed dictionary ready to be sent to the frontend.
        """
        if not value:
            return None
        
        processed_value = value.copy()
        
        # Process license file paths from the 'licenses' dictionary
        license_paths = processed_value.get("licenses", {})
        processed_licenses = {}
        if isinstance(license_paths, dict): # Check if licenses are in the expected format
            for name, path in license_paths.items():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        processed_licenses[name] = f.read()
                except Exception as e:
                    # Silently fail or log, to avoid crashing the app for a missing license file
                    processed_licenses[name] = f"Error loading license file '{path}':\n{e}"
        processed_value["licenses"] = processed_licenses

        # Process image paths
        processed_value["logo_path"] = self._process_image_path(processed_value.get("logo_path"))
        processed_value["scroll_logo_path"] = self._process_image_path(processed_value.get("scroll_logo_path"))

        return processed_value
    
    def api_info(self) -> Dict[str, Any]:
        """Returns API info for the component."""
        return {"type": "object"}

    def example_payload(self) -> Any:
        """Returns an example payload for the component's API."""
        # This now directly returns a dictionary matching the `value` structure.
        return {
            "credits": [{"title": "API Example", "name": "Credit"}],
            "licenses": {"MIT": "MIT License text..."},
            "effect": "scroll",
            "speed": 20,
            "sidebar_position": "right",
            "logo_path": None,
            "show_logo": True,
            "show_licenses": True,
            "show_credits": True,
            "logo_position": "center",
            "logo_sizing": "resize",
            "logo_width": None,
            "logo_height": None,
            "scroll_background_color": None,
            "scroll_title_color": None,
            "scroll_name_color": None,
            "scroll_section_title_color": None,
            "layout_style": "stacked",
            "title_uppercase": False,
            "name_uppercase": False,
            "section_title_uppercase": True,
            "swap_font_sizes_on_two_column": False,
            "scroll_logo_path": None,
            "scroll_logo_height": "120px",
        }

    def example_value(self) -> Any:
        """Returns an example value for the component."""
        # The example value is now the entire configuration dictionary.
        return self.example_payload()
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
        from gradio.components.base import Component

    
    def change(self,
        fn: Callable[..., Any] | None = None,
        inputs: Block | Sequence[Block] | set[Block] | None = None,
        outputs: Block | Sequence[Block] | None = None,
        api_name: str | None | Literal[False] = None,
        scroll_to_output: bool = False,
        show_progress: Literal["full", "minimal", "hidden"] = "full",
        show_progress_on: Component | Sequence[Component] | None = None,
        queue: bool | None = None,
        batch: bool = False,
        max_batch_size: int = 4,
        preprocess: bool = True,
        postprocess: bool = True,
        cancels: dict[str, Any] | list[dict[str, Any]] | None = None,
        every: Timer | float | None = None,
        trigger_mode: Literal["once", "multiple", "always_last"] | None = None,
        js: str | Literal[True] | None = None,
        concurrency_limit: int | None | Literal["default"] = "default",
        concurrency_id: str | None = None,
        show_api: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        api_description: str | None | Literal[False] = None,
        validator: Callable[..., Any] | None = None,
    
        ) -> Dependency:
        """
        Parameters:
            fn: the function to call when this event is triggered. Often a machine learning model's prediction function. Each parameter of the function corresponds to one input component, and the function should return a single value or a tuple of values, with each element in the tuple corresponding to one output component.
            inputs: list of gradio.components to use as inputs. If the function takes no inputs, this should be an empty list.
            outputs: list of gradio.components to use as outputs. If the function returns no outputs, this should be an empty list.
            api_name: defines how the endpoint appears in the API docs. Can be a string, None, or False. If False, the endpoint will not be exposed in the api docs. If set to None, will use the functions name as the endpoint route. If set to a string, the endpoint will be exposed in the api docs with the given name.
            scroll_to_output: if True, will scroll to output component on completion
            show_progress: how to show the progress animation while event is running: "full" shows a spinner which covers the output component area as well as a runtime display in the upper right corner, "minimal" only shows the runtime display, "hidden" shows no progress animation at all
            show_progress_on: Component or list of components to show the progress animation on. If None, will show the progress animation on all of the output components.
            queue: if True, will place the request on the queue, if the queue has been enabled. If False, will not put this event on the queue, even if the queue has been enabled. If None, will use the queue setting of the gradio app.
            batch: if True, then the function should process a batch of inputs, meaning that it should accept a list of input values for each parameter. The lists should be of equal length (and be up to length `max_batch_size`). The function is then *required* to return a tuple of lists (even if there is only 1 output component), with each list in the tuple corresponding to one output component.
            max_batch_size: maximum number of inputs to batch together if this is called from the queue (only relevant if batch=True)
            preprocess: if False, will not run preprocessing of component data before running 'fn' (e.g. leaving it as a base64 string if this method is called with the `Image` component).
            postprocess: if False, will not run postprocessing of component data before returning 'fn' output to the browser.
            cancels: a list of other events to cancel when this listener is triggered. For example, setting cancels=[click_event] will cancel the click_event, where click_event is the return value of another components .click method. Functions that have not yet run (or generators that are iterating) will be cancelled, but functions that are currently running will be allowed to finish.
            every: continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            trigger_mode: if "once" (default for all events except `.change()`) would not allow any submissions while an event is pending. If set to "multiple", unlimited submissions are allowed while pending, and "always_last" (default for `.change()` and `.key_up()` events) would allow a second submission after the pending event is complete.
            js: optional frontend js method to run before running 'fn'. Input arguments for js method are values of 'inputs' and 'outputs', return should be a list of values for output components.
            concurrency_limit: if set, this is the maximum number of this event that can be running simultaneously. Can be set to None to mean no concurrency_limit (any number of this event can be running simultaneously). Set to "default" to use the default concurrency limit (defined by the `default_concurrency_limit` parameter in `Blocks.queue()`, which itself is 1 by default).
            concurrency_id: if set, this is the id of the concurrency group. Events with the same concurrency_id will be limited by the lowest set concurrency_limit.
            show_api: whether to show this event in the "view API" page of the Gradio app, or in the ".view_api()" method of the Gradio clients. Unlike setting api_name to False, setting show_api to False will still allow downstream apps as well as the Clients to use this event. If fn is None, show_api will automatically be set to False.
            key: A unique key for this event listener to be used in @gr.render(). If set, this value identifies an event as identical across re-renders when the key is identical.
            api_description: Description of the API endpoint. Can be a string, None, or False. If set to a string, the endpoint will be exposed in the API docs with the given description. If None, the function's docstring will be used as the API endpoint description. If False, then no description will be displayed in the API docs.
            validator: Optional validation function to run before the main function. If provided, this function will be executed first with queue=False, and only if it completes successfully will the main function be called. The validator receives the same inputs as the main function.
        
        """
        ...
