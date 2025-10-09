from typing import Dict, List, Optional, Set

import pandas as pd

from nbastatpy.config import DateFields, IDFields


class ValidationResult:
    """Container for validation results."""

    def __init__(self):
        """Initialize validation result."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: bool = True

    def add_error(self, message: str) -> None:
        """Add an error message.

        Args:
            message: Error message to add
        """
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str) -> None:
        """Add a warning message.

        Args:
            message: Warning message to add
        """
        self.warnings.append(message)

    def __str__(self) -> str:
        """String representation of validation result."""
        if self.passed and not self.warnings:
            return "Validation passed with no issues"

        result = []
        if self.errors:
            result.append(f"Errors ({len(self.errors)}):")
            for error in self.errors:
                result.append(f"  - {error}")

        if self.warnings:
            result.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                result.append(f"  - {warning}")

        return "\n".join(result)


def validate_id_format(df: pd.DataFrame) -> ValidationResult:
    """Validate that ID fields are properly formatted.

    Args:
        df: DataFrame to validate

    Returns:
        ValidationResult with any issues found
    """
    result = ValidationResult()

    for id_field in IDFields.ID_FIELDS:
        if id_field in df.columns:
            # Check if IDs are 10 digits
            non_null = df[id_field].dropna()
            if len(non_null) > 0:
                # Check length
                invalid_length = non_null.astype(str).str.len() != 10
                if invalid_length.any():
                    count = invalid_length.sum()
                    result.add_error(
                        f"Column '{id_field}' has {count} values not formatted as 10-digit IDs"
                    )

                # Check if numeric (after padding)
                try:
                    pd.to_numeric(non_null, errors="raise")
                except ValueError:
                    result.add_error(f"Column '{id_field}' contains non-numeric values")

    return result


def validate_date_fields(df: pd.DataFrame) -> ValidationResult:
    """Validate that date fields are properly parsed.

    Args:
        df: DataFrame to validate

    Returns:
        ValidationResult with any issues found
    """
    result = ValidationResult()

    for date_field in DateFields.DATE_FIELDS:
        if date_field in df.columns:
            # Check if dates are parsed
            if df[date_field].dtype == "object":
                result.add_warning(
                    f"Column '{date_field}' is still object type, may not be properly parsed"
                )

            # Check for null values
            null_count = df[date_field].isna().sum()
            if null_count > 0:
                total = len(df)
                pct = (null_count / total) * 100
                if pct > 50:
                    result.add_error(
                        f"Column '{date_field}' has {null_count}/{total} ({pct:.1f}%) null values"
                    )
                elif pct > 10:
                    result.add_warning(
                        f"Column '{date_field}' has {null_count}/{total} ({pct:.1f}%) null values"
                    )

    return result


def validate_required_columns(
    df: pd.DataFrame, required_columns: Set[str]
) -> ValidationResult:
    """Validate that required columns are present.

    Args:
        df: DataFrame to validate
        required_columns: Set of required column names

    Returns:
        ValidationResult with any issues found
    """
    result = ValidationResult()

    missing = required_columns - set(df.columns)
    if missing:
        result.add_error(f"Missing required columns: {', '.join(sorted(missing))}")

    return result


def validate_numeric_ranges(
    df: pd.DataFrame, range_rules: Dict[str, tuple]
) -> ValidationResult:
    """Validate that numeric columns are within expected ranges.

    Args:
        df: DataFrame to validate
        range_rules: Dict mapping column names to (min, max) tuples

    Returns:
        ValidationResult with any issues found
    """
    result = ValidationResult()

    for col, (min_val, max_val) in range_rules.items():
        if col in df.columns:
            try:
                numeric_col = pd.to_numeric(df[col], errors="coerce")
                non_null = numeric_col.dropna()

                if len(non_null) > 0:
                    if (non_null < min_val).any():
                        count = (non_null < min_val).sum()
                        result.add_warning(
                            f"Column '{col}' has {count} values below minimum ({min_val})"
                        )

                    if (non_null > max_val).any():
                        count = (non_null > max_val).sum()
                        result.add_warning(
                            f"Column '{col}' has {count} values above maximum ({max_val})"
                        )
            except Exception as e:
                result.add_error(f"Could not validate range for column '{col}': {e}")

    return result


def validate_completeness(
    df: pd.DataFrame, max_null_pct: float = 50.0
) -> ValidationResult:
    """Validate data completeness (check for excessive null values).

    Args:
        df: DataFrame to validate
        max_null_pct: Maximum acceptable percentage of null values per column

    Returns:
        ValidationResult with any issues found
    """
    result = ValidationResult()

    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            total = len(df)
            pct = (null_count / total) * 100

            if pct > max_null_pct:
                result.add_error(
                    f"Column '{col}' has {null_count}/{total} ({pct:.1f}%) null values"
                )
            elif pct > 25:
                result.add_warning(
                    f"Column '{col}' has {null_count}/{total} ({pct:.1f}%) null values"
                )

    return result


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: Optional[Set[str]] = None,
    range_rules: Optional[Dict[str, tuple]] = None,
    max_null_pct: float = 50.0,
) -> ValidationResult:
    """Run all validations on a DataFrame.

    Args:
        df: DataFrame to validate
        required_columns: Set of required column names (optional)
        range_rules: Dict mapping column names to (min, max) tuples (optional)
        max_null_pct: Maximum acceptable percentage of null values per column

    Returns:
        Combined ValidationResult from all checks

    Example:
        >>> result = validate_dataframe(
        ...     df,
        ...     required_columns={'player_id', 'team_id'},
        ...     range_rules={'age': (15, 50), 'pts': (0, 100)}
        ... )
        >>> if not result.passed:
        ...     print(result)
    """
    combined_result = ValidationResult()

    # Run ID format validation
    id_result = validate_id_format(df)
    combined_result.errors.extend(id_result.errors)
    combined_result.warnings.extend(id_result.warnings)

    # Run date validation
    date_result = validate_date_fields(df)
    combined_result.errors.extend(date_result.errors)
    combined_result.warnings.extend(date_result.warnings)

    # Run required columns validation
    if required_columns:
        req_result = validate_required_columns(df, required_columns)
        combined_result.errors.extend(req_result.errors)
        combined_result.warnings.extend(req_result.warnings)

    # Run range validation
    if range_rules:
        range_result = validate_numeric_ranges(df, range_rules)
        combined_result.errors.extend(range_result.errors)
        combined_result.warnings.extend(range_result.warnings)

    # Run completeness validation
    comp_result = validate_completeness(df, max_null_pct)
    combined_result.errors.extend(comp_result.errors)
    combined_result.warnings.extend(comp_result.warnings)

    # Update passed status
    combined_result.passed = len(combined_result.errors) == 0

    return combined_result


# Common range rules for NBA data
NBA_RANGE_RULES = {
    "age": (15, 50),
    "pts": (0, 200),
    "reb": (0, 50),
    "ast": (0, 50),
    "stl": (0, 20),
    "blk": (0, 20),
    "fg_pct": (0.0, 1.0),
    "fg3_pct": (0.0, 1.0),
    "ft_pct": (0.0, 1.0),
    "minutes": (0, 60),
    "height_inches": (60, 96),
    "weight": (150, 350),
}
