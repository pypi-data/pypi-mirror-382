import dash as ds
from dash import Input, Output, dcc, html
from typing import Union, List, Dict
from .SliderComponents import SliderWithTextInput


class MaterialSelector:
    """
    A custom Dash component that combines material selection controls in a horizontal layout.

    This component creates a horizontal row containing:
    - A dropdown menu for selecting material names
    - An input box for specifying weight fraction of the material
    - Two SliderWithTextInput components for specific cost and density

    The component is designed for material composition interfaces where users need to
    select materials and specify their properties and proportions.

    Attributes:
        id_base (dict): Base identifier dictionary used to construct unique IDs for child components
        material_options (List[Dict]): List of material options for the dropdown
        default_material (str): Default selected material name
        default_weight_fraction (float): Default weight fraction value
        cost_config (dict): Configuration for the cost slider (min_val, max_val, step, etc.)
        density_config (dict): Configuration for the density slider (min_val, max_val, step, etc.)
        property_name (str): Property identifier used in component ID construction
        title (str): Display title for the component
        slider_disable (bool): Whether the sliders should be disabled
        dropdown_id (dict): Computed ID for the dropdown component
        weight_fraction_id (dict): Computed ID for the weight fraction input
        cost_slider (SliderWithTextInput): Cost slider component
        density_slider (SliderWithTextInput): Density slider component

    Example:
        >>> material_selector = MaterialSelector(
        ...     id_base={'type': 'material', 'index': 0},
        ...     material_options=[
        ...         {'label': 'Aluminum', 'value': 'aluminum'},
        ...         {'label': 'Steel', 'value': 'steel'},
        ...         {'label': 'Carbon Fiber', 'value': 'carbon_fiber'}
        ...     ],
        ...     default_material='aluminum',
        ...     default_weight_fraction=0.5,
        ...     cost_config={
        ...         'min_val': 0.0,
        ...         'max_val': 100.0,
        ...         'step': 0.1,
        ...         'mark_interval': 10.0,
        ...         'default_val': 25.0,
        ...         'title': 'Cost ($/kg)'
        ...     },
        ...     density_config={
        ...         'min_val': 0.0,
        ...         'max_val': 10.0,
        ...         'step': 0.01,
        ...         'mark_interval': 1.0,
        ...         'default_val': 2.7,
        ...         'title': 'Density (g/cm³)'
        ...     },
        ...     property_name='material_1',
        ...     title='Material 1'
        ... )
        >>> layout_element = material_selector()  # Returns Dash HTML Div component
    """

    def __init__(
        self,
        id_base: dict,
        material_options: List[Dict] = None,
        slider_configs: dict = None,
        cost_config: dict = None,
        density_config: dict = None,
        title: str = "Material",
        default_material: str = None,
        default_weight_percent: float = 0,
        slider_disable: bool = False,
        div_width: str = "100%",
        hidden: bool = False,
    ):
        """
        Initialize the MaterialSelector component.

        Args:
            id_base (dict): Base dictionary for generating component IDs.
            material_options (List[Dict], optional): List of material options for dropdown.
                                         Each dict should have 'label' and 'value' keys.
                                         If None, defaults to empty list (no options).
            slider_configs (dict, optional): Output from create_slider_config with arrays where:
                                           - Index 0 = density configuration
                                           - Index 1 = cost configuration
                                           If provided, cost_config and density_config are ignored.
                                           If empty dictionary {}, uses sensible defaults with preset values.
                                           If None (default), uses sensible defaults with no initial values.
            cost_config (dict, optional): Legacy cost slider configuration. Ignored if slider_config provided.
            density_config (dict, optional): Legacy density slider configuration. Ignored if slider_config provided.
            title (str, optional): Title displayed for the component. Defaults to "Material".
            default_material (str, optional): Default selected material. If None, no material
                                             will be initially selected in the dropdown.
            default_weight_percent (float, optional): Default weight percentage (0.0-100.0). Defaults to 100.0.
            slider_disable (bool, optional): Whether to disable sliders. Defaults to False.
            div_width (str, optional): CSS width specification for the container div.
                                     Defaults to '100%'.
            hidden (bool, optional): Whether to hide the entire component. When True,
                                   the component will be rendered with display: none.
                                   Defaults to False.
        """
        self.id_base = id_base
        self.material_options = material_options or []  # Default to empty list if None
        self.default_material = default_material  # Keep as None if not provided
        self.default_weight_percent = default_weight_percent
        self.cost_config = cost_config
        self.density_config = density_config
        self.title = title
        self.slider_disable = slider_disable
        self.div_width = div_width
        self.hidden = hidden

        # Generate component IDs
        self.dropdown_id = self._make_id("dropdown")
        self.weight_fraction_id = self._make_id("weight_fraction")

        # Normalize configurations to handle both legacy and create_slider_config formats
        if slider_configs is not None and slider_configs:  # Check if not empty
            # Use slider_configs arrays (index 0 = density, index 1 = cost)
            density_normalized = self._normalize_config_from_arrays(
                slider_configs, 0, "Density (g/cm³)"
            )
            cost_normalized = self._normalize_config_from_arrays(
                slider_configs, 1, "Specific Cost ($/kg)"
            )
        elif slider_configs is not None and not slider_configs:  # Empty dictionary
            # Use sensible defaults for materials
            density_normalized = {
                "min_val": 0.0,
                "max_val": 0.1,
                "step": 0.01,
                "mark_interval": 0.1,
                "title": "Density (g/cm³)",
                "default_val": 0.05,
            }
            cost_normalized = {
                "min_val": 0.0,
                "max_val": 0.1,
                "step": 0.01,
                "mark_interval": 0.1,
                "title": "Specific Cost ($/kg)",
                "default_val": 0.05,
            }
        else:
            # slider_configs is None - use sensible defaults with None values
            density_normalized = {
                "min_val": 0.0,
                "max_val": 0.1,
                "step": 0.01,
                "mark_interval": 0.1,
                "title": "Density (g/cm³)",
                "default_val": None,  # No initial value
            }
            cost_normalized = {
                "min_val": 0.0,
                "max_val": 0.1,
                "step": 0.01,
                "mark_interval": 0.1,
                "title": "Specific Cost ($/kg)",
                "default_val": None,  # No initial value
            }

        # Create slider components
        cost_slider_kwargs = {
            "id_base": id_base,
            "min_val": cost_normalized["min_val"],
            "max_val": cost_normalized["max_val"],
            "step": cost_normalized["step"],
            "mark_interval": cost_normalized["mark_interval"],
            "property_name": "specific_cost",
            "title": cost_normalized["title"],
            "default_val": cost_normalized.get(
                "default_val", cost_normalized["min_val"]
            ),
            "with_slider_titles": True,
            "slider_disable": slider_disable,
            "div_width": "100%",
        }
        # Add marks if available
        if "marks" in cost_normalized:
            cost_slider_kwargs["marks"] = cost_normalized["marks"]

        self.cost_slider = SliderWithTextInput(**cost_slider_kwargs)

        density_slider_kwargs = {
            "id_base": id_base,
            "min_val": density_normalized["min_val"],
            "max_val": density_normalized["max_val"],
            "step": density_normalized["step"],
            "mark_interval": density_normalized["mark_interval"],
            "property_name": "density",
            "title": density_normalized["title"],
            "default_val": density_normalized.get(
                "default_val", density_normalized["min_val"]
            ),
            "with_slider_titles": True,
            "slider_disable": slider_disable,
            "div_width": "100%",
        }
        # Add marks if available
        if "marks" in density_normalized:
            density_slider_kwargs["marks"] = density_normalized["marks"]

        self.density_slider = SliderWithTextInput(**density_slider_kwargs)

    def _normalize_config_from_arrays(
        self, config: dict, index: int, default_title: str
    ) -> dict:
        """
        Normalize slider configuration from create_slider_config output arrays.

        Args:
            config (dict): create_slider_config output with array values
            index (int): Index to extract from each array (0 = density, 1 = cost)
            default_title (str): Default title if not provided

        Returns:
            dict: Normalized configuration with min_val, max_val, step, mark_interval, title keys
        """
        normalized = {
            "min_val": config["min_vals"][index],
            "max_val": config["max_vals"][index],
            "step": config["step_vals"][index],
            "title": default_title,  # Use provided title
        }

        # Get pre-computed marks if available, otherwise calculate mark_interval
        if "mark_vals" in config and len(config["mark_vals"]) > index:
            marks = config["mark_vals"][index]
            normalized["marks"] = marks  # Pass the actual marks dictionary
            if len(marks) >= 2:
                # Calculate interval from first two marks
                mark_positions = sorted(marks.keys())
                normalized["mark_interval"] = mark_positions[1] - mark_positions[0]
            else:
                # Fallback: use step as mark interval
                normalized["mark_interval"] = normalized["step"]
        else:
            normalized["mark_interval"] = normalized["step"]

        # Add default value if available from grid values
        if "grid_slider_vals" in config and len(config["grid_slider_vals"]) > index:
            normalized["default_val"] = config["grid_slider_vals"][index]
        else:
            normalized["default_val"] = normalized["min_val"]

        return normalized

    def _normalize_config(self, config: dict, config_type: str) -> dict:
        """
        Normalize slider configuration to handle both legacy and create_slider_config formats.

        Args:
            config (dict): Either legacy format or create_slider_config output
            config_type (str): Type identifier ('cost' or 'density') for default title

        Returns:
            dict: Normalized configuration with min_val, max_val, step, mark_interval, title keys
        """
        # Check if this is a create_slider_config output (has min_vals, max_vals, etc.)
        if "min_vals" in config and "max_vals" in config:
            # This is create_slider_config output - use first element from arrays
            normalized = {
                "min_val": config["min_vals"][0],
                "max_val": config["max_vals"][0],
                "step": config["step_vals"][0],
                "title": config_type.capitalize(),  # Default title
            }

            # Get pre-computed marks if available, otherwise calculate mark_interval
            if "mark_vals" in config and len(config["mark_vals"]) > 0:
                marks = config["mark_vals"][0]
                normalized["marks"] = marks  # Pass the actual marks dictionary
                if len(marks) >= 2:
                    # Calculate interval from first two marks
                    mark_positions = sorted(marks.keys())
                    normalized["mark_interval"] = mark_positions[1] - mark_positions[0]
                else:
                    # Fallback: use step as mark interval
                    normalized["mark_interval"] = normalized["step"]
            else:
                normalized["mark_interval"] = normalized["step"]

            # Add default value if available from grid values
            if "grid_slider_vals" in config and len(config["grid_slider_vals"]) > 0:
                normalized["default_val"] = config["grid_slider_vals"][0]
            else:
                normalized["default_val"] = normalized["min_val"]

        else:
            # This is legacy format - use as-is but ensure all required keys exist
            normalized = config.copy()
            if "title" not in normalized:
                normalized["title"] = config_type.capitalize()
            if "default_val" not in normalized:
                normalized["default_val"] = normalized.get("min_val", 0)

        return normalized

    def _make_id(self, subtype: str):
        """
        Generate a unique ID dictionary for component sub-elements.

        Args:
            subtype (str): The specific component subtype.

        Returns:
            dict: Complete ID dictionary containing base ID information plus subtype.
        """
        return {**self.id_base, "subtype": subtype}

    def _make_dropdown(self):
        """
        Create and configure the material selection dropdown.

        Returns:
            dash.dcc.Dropdown: Configured dropdown component for material selection.
        """
        return dcc.Dropdown(
            id=self.dropdown_id,
            options=self.material_options,
            value=self.default_material,  # Can be None for no initial selection
            disabled=self.slider_disable,
            style={"width": "100%", "margin-bottom": "10px"},
        )

    def _make_weight_fraction_input(self):
        """
        Create and configure the weight percentage input.

        Returns:
            dash.dcc.Input: Configured numeric input for weight percentage.
        """
        return dcc.Input(
            id=self.weight_fraction_id,
            type="number",
            value=self.default_weight_percent,  # Use percentage directly
            min=0.0,
            max=100.0,
            step=0.1,
            disabled=self.slider_disable,
            style={"width": "100%", "margin-bottom": "10px"},
        )

    def __call__(self):
        """
        Generate the complete component layout as a callable object.

        Creates and returns a Dash HTML Div containing all components arranged
        in a horizontal layout with proper spacing and styling.

        Returns:
            dash.html.Div: Complete component layout with horizontal arrangement.
        """
        return html.Div(
            [
                # Main horizontal layout
                html.Div(
                    [
                        # Material selection column
                        html.Div(
                            [
                                html.P(
                                    "Material:",
                                    style={
                                        "margin": "0px 0px 5px 0px",
                                        "font-weight": "bold",
                                    },
                                ),
                                self._make_dropdown(),
                            ],
                            style={
                                "width": "20%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "padding-right": "25px",
                            },
                        ),
                        # Weight percentage column
                        html.Div(
                            [
                                html.P(
                                    "Weight (%):",
                                    style={
                                        "margin": "0px 0px 5px 0px",
                                        "font-weight": "bold",
                                    },
                                ),
                                self._make_weight_fraction_input(),
                            ],
                            style={
                                "width": "15%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "padding-right": "25px",
                            },
                        ),
                        # Density slider column
                        html.Div(
                            [self.density_slider()],
                            style={
                                "width": "30%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "padding-right": "25px",
                            },
                        ),
                        # Cost slider column
                        html.Div(
                            [self.cost_slider()],
                            style={
                                "width": "30%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "align-items": "flex-start",
                        "width": "100%",
                        "gap": "15px",
                    },
                )
            ],
            id=self.id_base,
            style={
                "border": "1px solid #ddd",
                "border-radius": "5px",
                "padding": "15px",
                "margin": "10px 0px",
                "background-color": "#f9f9f9",
                "width": self.div_width,
                "display": "none" if self.hidden else "block",
            },
        )

    @property
    def components(self):
        """
        Get a dictionary mapping component types to their IDs.

        Returns:
            dict: Dictionary with component type keys mapping to their ID dictionaries.
        """
        return {
            "dropdown": self.dropdown_id,
            "weight_fraction": self.weight_fraction_id,
            "cost_slider": self.cost_slider.slider_id,
            "cost_input": self.cost_slider.input_id,
            "density_slider": self.density_slider.slider_id,
            "density_input": self.density_slider.input_id,
        }

    def get_all_inputs(self):
        """
        Get Input objects for all component values.

        Returns:
            list: List containing Input objects for all components.
        """
        return [
            Input(self.dropdown_id, "value"),
            Input(self.weight_fraction_id, "value"),
            Input(self.cost_slider.slider_id, "value"),
            Input(self.cost_slider.input_id, "value"),
            Input(self.density_slider.slider_id, "value"),
            Input(self.density_slider.input_id, "value"),
        ]

    def get_all_outputs(self):
        """
        Get Output objects for updating all component values.

        Returns:
            list: List containing Output objects for all components.
        """
        return [
            Output(self.dropdown_id, "value"),
            Output(self.weight_fraction_id, "value"),
            Output(self.cost_slider.slider_id, "value"),
            Output(self.cost_slider.input_id, "value"),
            Output(self.density_slider.slider_id, "value"),
            Output(self.density_slider.input_id, "value"),
        ]


class ActiveMaterialSelector(MaterialSelector):
    """
    A custom Dash component for active material selection with capacity controls.

    This component extends MaterialSelector functionality by adding reversible and
    irreversible capacity sliders alongside the standard density and cost controls.
    It creates a horizontal row containing:
    - A dropdown menu for selecting material names
    - An input box for specifying weight percentage of the material
    - Four SliderWithTextInput components for:
        * Density
        * Specific cost
        * Reversible capacity scaling
        * Irreversible capacity scaling

    This component is designed for battery active material interfaces where users need to
    specify both physical properties (cost, density) and electrochemical scaling factors
    (reversible/irreversible capacity scaling).
    """

    def __init__(
        self,
        id_base: dict,
        material_options: List[Dict] = None,
        slider_configs: dict = None,
        title: str = "Active Material",
        default_material: str = None,
        default_weight_percent: float = 0,
        slider_disable: bool = False,
        div_width: str = "100%",
        hidden: bool = False,
    ):
        """
        Initialize the ActiveMaterialSelector component.

        Args:
            id_base (dict): Base dictionary for generating component IDs.
            material_options (List[Dict], optional): List of material options for dropdown.
                                         Each dict should have 'label' and 'value' keys.
                                         If None, defaults to empty list (no options).
            slider_configs (dict): Output from create_slider_config with arrays where:
                                 - Index 0 = density configuration
                                 - Index 1 = cost configuration
                                 - Index 2 = reversible capacity scaling configuration
                                 - Index 3 = irreversible capacity scaling configuration
                                 If empty dictionary {}, uses sensible defaults with preset values.
                                 If None (default), uses sensible defaults with no initial values.
            title (str, optional): Title displayed for the component. Defaults to "Active Material".
            default_material (str, optional): Default selected material. If None, no material
                                             will be initially selected in the dropdown.
            default_weight_percent (float, optional): Default weight percentage (0.0-100.0). Defaults to 100.0.
            slider_disable (bool, optional): Whether to disable sliders. Defaults to False.
            div_width (str, optional): CSS width specification for the container div.
                                     Defaults to '100%'.
            hidden (bool, optional): Whether to hide the entire component. When True,
                                   the component will be rendered with display: none.
                                   Defaults to False.
        """
        # Handle different slider_configs scenarios
        if slider_configs is not None and slider_configs:
            # Use provided configuration
            pass  # slider_configs will be passed to parent
        elif slider_configs is not None and not slider_configs:
            # Empty dictionary - create sensible defaults with preset values
            from ..Utils.SliderControls import create_slider_config

            min_vals = [
                0.0,
                0.0,
                0.0,
                0.0,
            ]  # density, cost, rev_cap_scaling, irrev_cap_scaling
            max_vals = [
                0.1,
                0.1,
                0.1,
                0.1,
            ]  # density, cost, rev_cap_scaling, irrev_cap_scaling
            default_vals = [
                0.05,
                0.05,
                0.05,
                0.05,
            ]  # density, cost, rev_cap_scaling, irrev_cap_scaling
            slider_configs = create_slider_config(min_vals, max_vals, default_vals)
        else:
            # slider_configs is None - create sensible defaults with None values
            # Create manual config since create_slider_config doesn't handle None values
            slider_configs = {
                "min_vals": [0.0, 0.0, 0.0, 0.0],
                "max_vals": [0.1, 0.1, 0.1, 0.1],
                "step_vals": [0.01, 0.01, 0.01, 0.01],
                "grid_slider_vals": [None, None, None, None],
                "mark_vals": [
                    {0.0: "", 0.1: ""},  # density
                    {0.0: "", 0.1: ""},  # cost
                    {0.0: "", 0.1: ""},  # rev_cap_scaling
                    {0.0: "", 0.1: ""},  # irrev_cap_scaling
                ],
            }

        # Initialize the parent MaterialSelector with first two sliders (density, cost)
        super().__init__(
            id_base=id_base,
            material_options=material_options,
            slider_configs=slider_configs,  # Parent will use indices 0 and 1
            title=title,
            default_material=default_material,
            default_weight_percent=default_weight_percent,
            slider_disable=slider_disable,
            div_width=div_width,
            hidden=hidden,
        )

        # Add the additional capacity sliders (indices 2 and 3)
        reversible_capacity_normalized = self._normalize_config_from_arrays(
            slider_configs, 2, "Reversible Capacity Scaling"
        )
        irreversible_capacity_normalized = self._normalize_config_from_arrays(
            slider_configs, 3, "Irreversible Capacity Scaling"
        )

        # Create additional slider components
        reversible_capacity_slider_kwargs = {
            "id_base": id_base,
            "min_val": reversible_capacity_normalized["min_val"],
            "max_val": reversible_capacity_normalized["max_val"],
            "step": reversible_capacity_normalized["step"],
            "mark_interval": reversible_capacity_normalized["mark_interval"],
            "property_name": "reversible_capacity_scaling",
            "title": reversible_capacity_normalized["title"],
            "default_val": reversible_capacity_normalized.get(
                "default_val", reversible_capacity_normalized["min_val"]
            ),
            "with_slider_titles": True,
            "slider_disable": slider_disable,
            "div_width": "100%",
        }
        if "marks" in reversible_capacity_normalized:
            reversible_capacity_slider_kwargs["marks"] = reversible_capacity_normalized[
                "marks"
            ]
        self.reversible_capacity_slider = SliderWithTextInput(
            **reversible_capacity_slider_kwargs
        )

        irreversible_capacity_slider_kwargs = {
            "id_base": id_base,
            "min_val": irreversible_capacity_normalized["min_val"],
            "max_val": irreversible_capacity_normalized["max_val"],
            "step": irreversible_capacity_normalized["step"],
            "mark_interval": irreversible_capacity_normalized["mark_interval"],
            "property_name": "irreversible_capacity_scaling",
            "title": irreversible_capacity_normalized["title"],
            "default_val": irreversible_capacity_normalized.get(
                "default_val", irreversible_capacity_normalized["min_val"]
            ),
            "with_slider_titles": True,
            "slider_disable": slider_disable,
            "div_width": "100%",
        }
        if "marks" in irreversible_capacity_normalized:
            irreversible_capacity_slider_kwargs[
                "marks"
            ] = irreversible_capacity_normalized["marks"]
        self.irreversible_capacity_slider = SliderWithTextInput(
            **irreversible_capacity_slider_kwargs
        )

    def __call__(self):
        """
        Generate the complete component layout as a callable object.

        Creates and returns a Dash HTML Div containing all components arranged
        in a horizontal layout with proper spacing and styling.

        Returns:
            dash.html.Div: Complete component layout with horizontal arrangement.
        """
        return html.Div(
            [
                # Main horizontal layout
                html.Div(
                    [
                        # Material selection column (15%)
                        html.Div(
                            [
                                html.P(
                                    "Material:",
                                    style={
                                        "margin": "0px 0px 5px 0px",
                                        "font-weight": "bold",
                                    },
                                ),
                                self._make_dropdown(),
                            ],
                            style={
                                "width": "15%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "padding-right": "15px",
                            },
                        ),
                        # Weight percentage column (15%)
                        html.Div(
                            [
                                html.P(
                                    "Weight (%):",
                                    style={
                                        "margin": "0px 0px 5px 0px",
                                        "font-weight": "bold",
                                    },
                                ),
                                self._make_weight_fraction_input(),
                            ],
                            style={
                                "width": "15%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "padding-right": "15px",
                            },
                        ),
                        # Density slider column (17.5%)
                        html.Div(
                            [self.density_slider()],
                            style={
                                "width": "17.5%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "padding-right": "15px",
                            },
                        ),
                        # Cost slider column (17.5%)
                        html.Div(
                            [self.cost_slider()],
                            style={
                                "width": "17.5%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "padding-right": "15px",
                            },
                        ),
                        # Reversible capacity slider column (17.5%)
                        html.Div(
                            [self.reversible_capacity_slider()],
                            style={
                                "width": "17.5%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "padding-right": "15px",
                            },
                        ),
                        # Irreversible capacity slider column (17.5%)
                        html.Div(
                            [self.irreversible_capacity_slider()],
                            style={
                                "width": "17.5%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "align-items": "flex-start",
                        "width": "100%",
                        "gap": "10px",
                    },
                )
            ],
            id=self.id_base,
            style={
                "border": "1px solid #ddd",
                "border-radius": "5px",
                "padding": "15px",
                "margin": "10px 0px",
                "background-color": "#f9f9f9",
                "width": self.div_width,
                "display": "none" if self.hidden else "block",
            },
        )

    @property
    def components(self):
        """
        Get a dictionary mapping component types to their IDs.

        Returns:
            dict: Dictionary with component type keys mapping to their ID dictionaries.
        """
        # Get base components from parent
        base_components = super().components

        # Add the additional capacity slider components
        base_components.update(
            {
                "reversible_capacity_scaling_slider": self.reversible_capacity_slider.slider_id,
                "reversible_capacity_scaling_input": self.reversible_capacity_slider.input_id,
                "irreversible_capacity_scaling_slider": self.irreversible_capacity_slider.slider_id,
                "irreversible_capacity_scaling_input": self.irreversible_capacity_slider.input_id,
            }
        )

        return base_components

    def get_all_inputs(self):
        """
        Get Input objects for all component values.

        Returns:
            list: List containing Input objects for all components.
        """
        # Get base inputs from parent
        base_inputs = super().get_all_inputs()

        # Add the additional capacity slider inputs
        capacity_inputs = [
            Input(self.reversible_capacity_slider.slider_id, "value"),
            Input(self.reversible_capacity_slider.input_id, "value"),
            Input(self.irreversible_capacity_slider.slider_id, "value"),
            Input(self.irreversible_capacity_slider.input_id, "value"),
        ]

        return base_inputs + capacity_inputs

    def get_all_outputs(self):
        """
        Get Output objects for updating all component values.

        Returns:
            list: List containing Output objects for all components.
        """
        # Get base outputs from parent
        base_outputs = super().get_all_outputs()

        # Add the additional capacity slider outputs
        capacity_outputs = [
            Output(self.reversible_capacity_slider.slider_id, "value"),
            Output(self.reversible_capacity_slider.input_id, "value"),
            Output(self.irreversible_capacity_slider.slider_id, "value"),
            Output(self.irreversible_capacity_slider.input_id, "value"),
        ]

        return base_outputs + capacity_outputs
