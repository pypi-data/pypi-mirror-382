import plotly.graph_objects as go
from typing import Dict, Any, Tuple, List, Union


class PlotterMixin:
    
    @staticmethod
    def plot_breakdown_sunburst(
        breakdown_dict: Dict[str, Any],
        title: str = "Breakdown",
        root_label: str = "Total",
        unit: str = "",
        **kwargs,
    ) -> go.Figure:
        """
        Create a sunburst plot for any generic nested breakdown dictionary.

        Parameters
        ----------
        breakdown_dict : Dict[str, Any]
            Nested dictionary where values can be either numbers or nested dictionaries.
            Each nesting level becomes a ring in the sunburst plot.
        title : str, optional
            Title for the plot. Defaults to "Breakdown".
        root_label : str, optional
            Label for the root node. Defaults to "Total".
        unit : str, optional
            Unit string to display in hover text (e.g., "g", "kg", "%"). Defaults to "".

        Returns
        -------
        go.Figure
            Plotly sunburst figure
        """

        def _flatten_breakdown_values(data: Dict[str, Any]) -> List[float]:
            """Recursively flatten all numeric values from nested breakdown dictionary"""
            values = []
            for value in data.values():
                if isinstance(value, dict):
                    values.extend(_flatten_breakdown_values(value))
                elif isinstance(value, (int, float)):
                    values.append(float(value))
            return values

        def _calculate_subtotal(data: Dict[str, Any]) -> float:
            """Calculate the total value for a dictionary (sum of all nested numeric values)"""
            total = 0.0
            for value in data.values():
                if isinstance(value, dict):
                    total += _calculate_subtotal(value)
                elif isinstance(value, (int, float)):
                    total += float(value)
            return total

        def _prepare_sunburst_data(
            data: Dict[str, Any], parent_id: str = "", current_path: str = ""
        ) -> Tuple[List[str], List[str], List[str], List[float]]:
            """Recursively prepare data for sunburst plot with proper hierarchy"""
            ids = []
            labels = []
            parents = []
            values = []

            for key, value in data.items():
                # Create unique ID for this node
                node_id = f"{current_path}/{key}" if current_path else key

                ids.append(node_id)
                labels.append(key)
                parents.append(parent_id)

                if isinstance(value, dict):
                    # This is a nested dictionary - calculate its total value
                    subtotal = _calculate_subtotal(value)
                    values.append(subtotal)

                    # Recursively process nested dictionary
                    (
                        nested_ids,
                        nested_labels,
                        nested_parents,
                        nested_values,
                    ) = _prepare_sunburst_data(
                        value, parent_id=node_id, current_path=node_id
                    )

                    # Add nested data to our lists
                    ids.extend(nested_ids)
                    labels.extend(nested_labels)
                    parents.extend(nested_parents)
                    values.extend(nested_values)

                elif isinstance(value, (int, float)):
                    # This is a leaf node with a numeric value
                    values.append(float(value))

            return ids, labels, parents, values

        # Calculate total value for root node
        total_value = _calculate_subtotal(breakdown_dict)

        # Prepare hierarchical data starting with root
        ids, labels, parents, values = _prepare_sunburst_data(
            breakdown_dict, parent_id=""
        )

        # Add root node at the beginning
        ids.insert(0, root_label)
        labels.insert(0, root_label)
        parents.insert(0, "")
        values.insert(0, total_value)

        # Update parent references to point to root
        for i in range(1, len(parents)):
            if parents[i] == "":
                parents[i] = root_label

        # Create custom hover text with percentages
        hover_text = []
        for i, (label, value) in enumerate(zip(labels, values)):
            if label == root_label:
                unit_str = f" {unit}" if unit else ""
                hover_text.append(f"<b>{root_label}</b><br>{value:.2f}{unit_str}")
            else:
                percentage = (value / total_value * 100) if total_value > 0 else 0
                unit_str = f" {unit}" if unit else ""
                hover_text.append(
                    f"<b>{label}</b><br>{value:.2f}{unit_str}<br>{percentage:.1f}% of total"
                )

        # Create the sunburst plot
        fig = go.Figure(
            go.Sunburst(
                ids=ids,
                labels=labels,
                parents=parents,
                values=values,
                branchvalues="total",
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hover_text,
            )
        )

        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)), font_size=12, **kwargs
        )

        return fig
