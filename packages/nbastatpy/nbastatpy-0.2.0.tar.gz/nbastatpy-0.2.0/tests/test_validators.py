import pandas as pd

from nbastatpy.validators import (
    NBA_RANGE_RULES,
    ValidationResult,
    validate_completeness,
    validate_dataframe,
    validate_date_fields,
    validate_id_format,
    validate_numeric_ranges,
    validate_required_columns,
)


class TestValidationResult:
    """Test the ValidationResult class."""

    def test_init(self):
        """Test ValidationResult initialization."""
        result = ValidationResult()
        assert result.passed is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error(self):
        """Test adding an error."""
        result = ValidationResult()
        result.add_error("Test error")
        assert result.passed is False
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"

    def test_add_warning(self):
        """Test adding a warning."""
        result = ValidationResult()
        result.add_warning("Test warning")
        assert result.passed is True  # Warnings don't fail validation
        assert len(result.warnings) == 1

    def test_str_no_issues(self):
        """Test string representation with no issues."""
        result = ValidationResult()
        assert "no issues" in str(result).lower()

    def test_str_with_errors(self):
        """Test string representation with errors."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_error("Error 2")
        result_str = str(result)
        assert "Error 1" in result_str
        assert "Error 2" in result_str


class TestValidateIdFormat:
    """Test the validate_id_format function."""

    def test_valid_ids(self):
        """Test validation of properly formatted IDs."""
        df = pd.DataFrame(
            {
                "player_id": ["0000000123", "0000000456"],
                "team_id": ["0000000001", "0000000002"],
            }
        )
        result = validate_id_format(df)
        assert result.passed is True
        assert len(result.errors) == 0

    def test_invalid_id_length(self):
        """Test validation catches improperly formatted IDs."""
        df = pd.DataFrame({"player_id": ["123", "456"]})
        result = validate_id_format(df)
        assert result.passed is False
        assert len(result.errors) > 0

    def test_non_numeric_ids(self):
        """Test validation catches non-numeric IDs."""
        df = pd.DataFrame({"player_id": ["000000abc1", "000000def2"]})
        result = validate_id_format(df)
        assert result.passed is False


class TestValidateDateFields:
    """Test the validate_date_fields function."""

    def test_valid_dates(self):
        """Test validation of properly parsed dates."""
        df = pd.DataFrame(
            {"game_date": pd.to_datetime(["2024-01-15", "2024-02-20"]).date}
        )
        result = validate_date_fields(df)
        assert len(result.errors) == 0

    def test_unparsed_dates_warning(self):
        """Test that unparsed dates generate a warning."""
        df = pd.DataFrame({"game_date": ["2024-01-15", "2024-02-20"]})
        result = validate_date_fields(df)
        assert len(result.warnings) > 0

    def test_many_null_dates_error(self):
        """Test that many null dates generate an error."""
        df = pd.DataFrame({"game_date": [None] * 60 + ["2024-01-15"] * 40})
        result = validate_date_fields(df)
        assert len(result.errors) > 0


class TestValidateRequiredColumns:
    """Test the validate_required_columns function."""

    def test_all_required_present(self):
        """Test when all required columns are present."""
        df = pd.DataFrame({"player_id": [1], "team_id": [2], "game_id": [3]})
        result = validate_required_columns(df, {"player_id", "team_id", "game_id"})
        assert result.passed is True

    def test_missing_required_columns(self):
        """Test when required columns are missing."""
        df = pd.DataFrame({"player_id": [1]})
        result = validate_required_columns(df, {"player_id", "team_id", "game_id"})
        assert result.passed is False
        assert len(result.errors) > 0


class TestValidateNumericRanges:
    """Test the validate_numeric_ranges function."""

    def test_valid_ranges(self):
        """Test validation with values in valid ranges."""
        df = pd.DataFrame({"age": [25, 30, 35], "pts": [20, 25, 30]})
        rules = {"age": (15, 50), "pts": (0, 100)}
        result = validate_numeric_ranges(df, rules)
        assert len(result.errors) == 0

    def test_values_below_minimum(self):
        """Test detection of values below minimum."""
        df = pd.DataFrame({"age": [10, 25, 30]})
        rules = {"age": (15, 50)}
        result = validate_numeric_ranges(df, rules)
        assert len(result.warnings) > 0

    def test_values_above_maximum(self):
        """Test detection of values above maximum."""
        df = pd.DataFrame({"pts": [50, 100, 150, 250]})
        rules = {"pts": (0, 100)}
        result = validate_numeric_ranges(df, rules)
        assert len(result.warnings) > 0


class TestValidateCompleteness:
    """Test the validate_completeness function."""

    def test_complete_data(self):
        """Test validation of complete data with no nulls."""
        df = pd.DataFrame({"player_id": [1, 2, 3], "pts": [20, 25, 30]})
        result = validate_completeness(df)
        assert result.passed is True

    def test_some_nulls_warning(self):
        """Test that some nulls generate a warning."""
        # Create DataFrame with 30% nulls (warning threshold is 25%)
        df = pd.DataFrame({"player_id": [1, 2, 3, None, None, None, 7, 8, 9, 10]})
        result = validate_completeness(df, max_null_pct=50.0)
        assert len(result.warnings) > 0

    def test_many_nulls_error(self):
        """Test that many nulls generate an error."""
        df = pd.DataFrame({"player_id": [1] + [None] * 99})
        result = validate_completeness(df, max_null_pct=50.0)
        assert result.passed is False
        assert len(result.errors) > 0


class TestValidateDataframe:
    """Test the validate_dataframe function."""

    def test_full_validation(self):
        """Test full validation with all checks."""
        df = pd.DataFrame(
            {
                "player_id": ["0000000123", "0000000456"],
                "team_id": ["0000000001", "0000000002"],
                "age": [25, 30],
                "pts": [20, 25],
                "game_date": pd.to_datetime(["2024-01-15", "2024-02-20"]).date,
            }
        )

        result = validate_dataframe(
            df,
            required_columns={"player_id", "team_id"},
            range_rules={"age": (15, 50), "pts": (0, 100)},
        )

        assert result.passed is True

    def test_validation_with_issues(self):
        """Test validation that finds multiple issues."""
        df = pd.DataFrame(
            {
                "player_id": ["123"],  # Invalid ID format
                "age": [10],  # Below minimum
            }
        )

        result = validate_dataframe(
            df,
            required_columns={"player_id", "team_id"},  # Missing team_id
            range_rules={"age": (15, 50)},
        )

        assert result.passed is False
        assert len(result.errors) > 0


class TestNBARangeRules:
    """Test the NBA_RANGE_RULES constant."""

    def test_nba_range_rules_exist(self):
        """Test that NBA range rules are defined."""
        assert isinstance(NBA_RANGE_RULES, dict)
        assert "age" in NBA_RANGE_RULES
        assert "pts" in NBA_RANGE_RULES
        assert "fg_pct" in NBA_RANGE_RULES

    def test_nba_range_rules_valid(self):
        """Test that NBA range rules have valid tuples."""
        for col, (min_val, max_val) in NBA_RANGE_RULES.items():
            assert isinstance(min_val, (int, float))
            assert isinstance(max_val, (int, float))
            assert min_val < max_val
