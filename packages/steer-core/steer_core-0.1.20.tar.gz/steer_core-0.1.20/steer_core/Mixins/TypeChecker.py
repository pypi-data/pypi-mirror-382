from typing import Type
import pandas as pd
import numpy as np
import plotly.graph_objects as go


ALLOWED_REFERENCE = ["Na/Na+", "Li/Li+"]


class ValidationMixin:

    @staticmethod
    def validate_plotly_trace(value: object, name: str) -> None:
        """
        Validate that a value is a Plotly trace object.

        Parameters
        ----------
        value : object
            The value to validate.
        name : str
            The name of the parameter for error messages.

        Raises
        ------
        TypeError
            If the value is not a Plotly trace object.
        """
        return (
            hasattr(value, '__module__') and
            value.__module__ and 
            value.__module__.startswith('plotly.graph_objs')
        )
        
    @staticmethod
    def validate_type(value: Type, expected_type: Type, name: str) -> None:
        """
        Validate that a value is of the expected type.

        Parameters
        ----------
        value : Type
            The value to validate.
        expected_type : Type
            The expected type of the value.
        name : str
            The name of the parameter for error messages.

        Raises
        ------
        TypeError
            If the value is not of the expected type.
        """
        if not isinstance(value, expected_type):
            raise TypeError(f"{name} must be of type {expected_type.__name__}. Provided: {type(value).__name__}.")

    @staticmethod
    def validate_percentage(value: float, name: str) -> None:
        """
        Validate that a value is a percentage (between 0 and 100).

        Parameters
        ----------
        value : float
            The value to validate.
        name : str
            The name of the parameter for error messages.

        Raises
        ------
        ValueError
            If the value is not a percentage.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number. Provided: {value}.")

        if not (0 <= value <= 100):
            raise ValueError(
                f"{name} must be a percentage between 0 and 100. Provided: {value}."
            )

    @staticmethod
    def validate_fraction(value: float, name: str) -> None:
        """
        Validate that a value is a fraction (between 0 and 1).

        Parameters
        ----------
        value : float
            The value to validate.
        name : str
            The name of the parameter for error messages.

        Raises
        ------
        ValueError
            If the value is not a fraction.
        """
        if not (0 <= value <= 1):
            raise ValueError(
                f"{name} must be a fraction between 0 and 1. Provided: {value}."
            )

    @staticmethod
    def validate_pandas_dataframe(
        df: pd.DataFrame, name: str, column_names: list = None
    ) -> None:
        """
        Validate that the input is a pandas DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to validate.
        name : str
            The name of the DataFrame for error messages.

        Raises
        ------
        TypeError
            If the input is not a pandas DataFrame.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"{name} must be a pandas DataFrame. Provided: {type(df)}.")

        if column_names is not None:
            missing_columns = [col for col in column_names if col not in df.columns]
            if missing_columns:
                raise ValueError(
                    f"{name} is missing required columns: {missing_columns}. "
                    f"Available columns: {df.columns.tolist()}."
                )

    @staticmethod
    def validate_electrochemical_reference(reference: str) -> None:
        """
        Validate the electrochemical reference electrode.

        Parameters
        ----------
        reference : str
            The reference electrode to validate.

        Raises
        ------
        ValueError
            If the reference is not a valid electrochemical reference.
        """
        ValidationMixin.validate_string(reference, "Electrochemical reference")

        if reference not in ALLOWED_REFERENCE:
            raise ValueError(
                f"Invalid electrochemical reference: {reference}. "
                f"Must be one of {ALLOWED_REFERENCE}."
            )

    @staticmethod
    def validate_datum(datum: np.ndarray) -> None:
        """
        Validate the datum point for extrusion.

        Parameters
        ----------
        datum : np.ndarray
            Datum point for extrusion (shape (3,))

        Raises
        ------
        ValueError
            If the datum does not have exactly 3 coordinates.
        """
        if type(datum) is not tuple and len(datum) != 3:
            raise ValueError("Datum must be a 3D point with exactly 3 coordinates.")

        if not all(isinstance(coord, (int, float)) for coord in datum):
            raise TypeError("All coordinates in datum must be numbers.")

    @staticmethod
    def validate_positive_float(value: float, name: str) -> None:
        """
        Validate that a value is a positive float.

        Parameters
        ----------
        value : float
            The value to validate.
        name : str
            The name of the parameter for error messages.

        Raises
        ------
        ValueError
            If the value is not a positive float.
        """
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a positive float. Provided: {value}.")

    @staticmethod
    def validate_string(value: str, name: str) -> None:
        """
        Validate that a value is a string.

        Parameters
        ----------
        value : str
            The value to validate.
        name : str
            The name of the parameter for error messages.

        Raises
        ------
        TypeError
            If the value is not a string.
        """
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string. Provided: {value}.")

    @staticmethod
    def validate_two_iterable_of_floats(value: tuple, name: str) -> None:
        """
        Validate that a value is a tuple of two iterables.

        Parameters
        ----------
        value : tuple
            The value to validate.
        name : str
            The name of the parameter for error messages.

        Raises
        ------
        TypeError
            If the value is not a tuple of two floats.
        """
        # Accept both tuples and lists
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise TypeError(
                f"{name} must be a tuple or list of two numbers. Provided: {value}."
            )

        # Check if all values are numeric (int or float)
        if not all(isinstance(v, (int, float)) for v in value):
            raise TypeError(
                f"{name} must be a tuple or list of two numbers. Provided: {value}."
            )

        # Check if all values are non-negative
        if not all(v >= 0 for v in value):
            raise ValueError(
                f"{name} must be a tuple or list of two non-negative numbers. Provided: {value}."
            )

    @staticmethod
    def validate_positive_float_list(value: list, name: str) -> None:
        """
        Validate that a value is a list of positive floats.

        Parameters
        ----------
        value : list
            The value to validate.
        name : str
            The name of the parameter for error messages.

        Raises
        ------
        TypeError
            If the value is not a list of positive floats.
        """
        if not isinstance(value, list) or not all(
            isinstance(v, (int, float)) and v > 0 for v in value
        ):
            raise TypeError(
                f"{name} must be a list of positive floats. Provided: {value}."
            )

        if len(value) == 0:
            raise ValueError(f"{name} must not be an empty list. Provided: {value}.")
