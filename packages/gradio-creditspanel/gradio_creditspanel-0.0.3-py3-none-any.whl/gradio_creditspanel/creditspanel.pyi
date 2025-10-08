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
    Supports displaying a logo, licenses, and configurable text styling.

    Attributes:
        EVENTS (list): Supported events for the component, currently only `change`.
    """

    EVENTS = [Events.change]

    def __init__(
        self,
        value: Any = None,
        credits: List[Dict[str, str]] | Callable | None = None,
        *,
        height: int | str | None = None,
        width: int | str | None = None,
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
        layout_style: Literal["stacked", "two-column"] = "stacked",
        title_uppercase: bool = False,
        name_uppercase: bool = False,
        section_title_uppercase: bool = True,
        swap_font_sizes_on_two_column: bool = False,
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
            value (Any, optional): Initial value for the component.
            credits (List[Dict[str, str]] | Callable | None, optional): List of credits as dictionaries with 'title' and 'name' keys, or a callable that returns such a list.
            height (int | str | None, optional): Height of the component (e.g., in pixels or CSS units).
            width (int | str | None, optional): Width of the component (e.g., in pixels or CSS units).
            licenses (Dict[str, str | Path] | None, optional): Dictionary mapping license names to file paths or content strings.
            effect (Literal["scroll", "starwars", "matrix"], optional): Visual effect for credits display. Defaults to "scroll".
            speed (float, optional): Animation speed in seconds. Defaults to 40.0.
            base_font_size (float, optional): Base font size in rem for credits text. Defaults to 1.5.
            intro_title (str | None, optional): Title for the intro section, if any.
            intro_subtitle (str | None, optional): Subtitle for the intro section, if any.
            sidebar_position (Literal["right", "bottom"], optional): Position of the licenses sidebar. Defaults to "right".
            logo_path (str | Path | None, optional): Path or URL to the logo image.
            show_logo (bool, optional): Whether to display the logo. Defaults to True.
            show_licenses (bool, optional): Whether to display licenses. Defaults to True.
            show_credits (bool, optional): Whether to display the credits. Defaults to True.
            logo_position (Literal["center", "left", "right"], optional): Logo alignment. Defaults to "center".
            logo_sizing (Literal["stretch", "crop", "resize"], optional): Logo sizing mode. Defaults to "resize".
            logo_width (int | str | None, optional): Logo width (e.g., in pixels or CSS units).
            logo_height (int | str | None, optional): Logo height (e.g., in pixels or CSS units).
            scroll_background_color (str | None, optional): Background color for scroll effect.
            scroll_title_color (str | None, optional): Color for credit titles.
            scroll_name_color (str | None, optional): Color for credit names.
            layout_style (Literal["stacked", "two-column"], optional): Layout for credits ('title' above 'name' or side-by-side). Defaults to "stacked".
            title_uppercase (bool, optional): Whether to display titles in uppercase. Defaults to False.
            name_uppercase (bool, optional): Whether to display names in uppercase. Defaults to False.            
            section_title_uppercase (bool, optional): Whether to display section titles in uppercase. Defaults to True.
            swap_font_sizes_on_two_column (bool, optional): If True and layout is 'two-column', swap the font sizes of title and name. Defaults to False.
            label (str | I18nData | None, optional): Component label.
            every (float | None, optional): Interval for periodic updates.
            inputs (Component | Sequence[Component] | set[Component] | None, optional): Input components for events.
            show_label (bool, optional): Whether to show the label. Defaults to False.
            container (bool, optional): Whether to render in a container. Defaults to True.
            scale (int | None, optional): Scaling factor for the component.
            min_width (int, optional): Minimum width in pixels. Defaults to 160.
            interactive (bool | None, optional): Whether the component is interactive.
            visible (bool, optional): Whether the component is visible. Defaults to True.
            elem_id (str | None, optional): Custom HTML element ID.
            elem_classes (list[str] | str | None, optional): CSS classes for the component.
            render (bool, optional): Whether to render the component. Defaults to True.
            key (int | str | tuple[int | str, ...] | None, optional): Component key for state preservation.
            preserved_by_key (list[str] | str | None, optional): Properties preserved by key. Defaults to "value".
        """
        self.height = height
        self.width = width
        self.credits_data = credits if credits is not None else []
        self.licenses_paths = licenses or {}
        self.effect = effect
        self.speed = speed
        self.base_font_size = base_font_size
        self.intro_title = intro_title
        self.intro_subtitle = intro_subtitle
        self.sidebar_position = sidebar_position
        self.logo_path = logo_path
        self.show_logo = show_logo
        self.show_licenses = show_licenses
        self.show_credits = show_credits
        self.logo_position = logo_position
        self.logo_sizing = logo_sizing
        self.logo_width = logo_width
        self.logo_height = logo_height
        self.scroll_background_color = scroll_background_color
        self.scroll_title_color = scroll_title_color
        self.scroll_name_color = scroll_name_color
        self.layout_style = layout_style
        self.title_uppercase = title_uppercase
        self.name_uppercase = name_uppercase
        self.section_title_uppercase = section_title_uppercase
        self.swap_font_sizes_on_two_column = swap_font_sizes_on_two_column
        
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
            value=value,
        )

    def _process_license_files(self) -> Dict[str, str]:
        """
        Process license files into a dictionary of name-content pairs.

        Returns:
            Dict[str, str]: Dictionary mapping license names to their content or error messages if loading fails.
        """
        processed = {}
        for name, path in self.licenses_paths.items():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    processed[name] = f.read()
            except Exception as e:
                processed[name] = f"Error loading license file '{path}':\n{e}"
        return processed

    def _process_logo_path(self) -> Dict[str, Any] | None:
        """
        Process the logo path, handling both local files and URLs.

        Returns:
            Dict[str, Any] | None: Dictionary with logo details (path, url, orig_name, mime_type) or None if no logo_path is provided or the file is not found.
        """
        if not self.logo_path:
            return None
        path = str(self.logo_path)
        if is_http_url_like(path):
            return {"path": None, "url": path, "orig_name": Path(path).name, "mime_type": None}
        if os.path.exists(path):
            return handle_file(path)
        return None

    def preprocess(self, payload: Dict[str, Any] | None) -> Dict[str, Any] | None:
        """
        Preprocess the input payload.

        Args:
            payload (Dict[str, Any] | None): Input data to preprocess.

        Returns:
            Dict[str, Any] | None: The input payload, returned unchanged.
        """
        return payload

    def postprocess(self, value: Any) -> Dict[str, Any] | None:
        """
        Postprocess the component's value to prepare data for rendering.

        Args:
            value (Any): Input value, typically a list of credits.

        Returns:
            Dict[str, Any] | None: Dictionary containing processed credits, licenses, and configuration, or None if no credits or licenses are provided.
        """
        credits_source = value if isinstance(value, list) else self.credits_data
        if not credits_source and not self.licenses_paths:
            return None
        return {
            "credits": credits_source,
            "licenses": self._process_license_files() if self.show_licenses else {},
            "effect": self.effect,
            "speed": self.speed,
            "base_font_size": self.base_font_size,
            "intro_title": self.intro_title,
            "intro_subtitle": self.intro_subtitle,
            "sidebar_position": self.sidebar_position,
            "logo_path": self._process_logo_path(),
            "show_logo": self.show_logo,
            "show_licenses": self.show_licenses,
            "show_credits": self.show_credits,
            "logo_position": self.logo_position,
            "logo_sizing": self.logo_sizing,
            "logo_width": self.logo_width,
            "logo_height": self.logo_height,
            "scroll_background_color": self.scroll_background_color,
            "scroll_title_color": self.scroll_title_color,
            "scroll_name_color": self.scroll_name_color,
            "layout_style": self.layout_style,
            "title_uppercase": self.title_uppercase,
            "name_uppercase": self.name_uppercase,
            "section_title_uppercase": self.section_title_uppercase,
            "swap_font_sizes_on_two_column": self.swap_font_sizes_on_two_column,
        }

    def api_info(self) -> Dict[str, Any]:
        """
        Provide API information for the component.

        Returns:
            Dict[str, Any]: Dictionary indicating the component's data type ("object").
        """
        return {"type": "object"}

    def example_payload(self) -> Any:
        """
        Provide an example payload for the component.

        Returns:
            Dict[str, Any]: Example data structure for the component's payload.
        """
        return {
            "credits": [{"title": "Example", "name": "Credit"}],
            "licenses": {},
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
            "layout_style": "stacked",
            "title_uppercase": False,
            "name_uppercase": False,
            "section_title_uppercase": True,
            "swap_font_sizes_on_two_column": False,
        }

    def example_value(self) -> Any:
        """
        Provide an example value for the component.

        Returns:
            List[Dict[str, str]]: Example list of credits.
        """
        return [{"title": "Example", "name": "Credit"}]
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
