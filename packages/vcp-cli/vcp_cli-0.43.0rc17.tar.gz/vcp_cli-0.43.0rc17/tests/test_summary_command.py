"""Tests for the data summary command."""

import re
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from vcp.commands.data.summary import summary_command
from vcp.datasets.api import CrossModalitySchemaFields, FacetBucket, SummaryResponse


@pytest.fixture
def mock_token_manager():
    """Mock TokenManager with valid tokens."""
    with patch("vcp.commands.data.summary.TOKEN_MANAGER") as mock:
        mock_tokens = MagicMock()
        mock_tokens.id_token = "mock_id_token"
        mock.load_tokens.return_value = mock_tokens
        yield mock


@pytest.fixture
def sample_summary_response():
    """Sample summary response from the API."""
    return SummaryResponse(
        field="assay",
        query="*",
        total_buckets=5,
        facets=[
            FacetBucket(value="10x 3' v3", count=1500),
            FacetBucket(value="10x 3' v2", count=1200),
            FacetBucket(value="Smart-seq2", count=800),
            FacetBucket(value="CEL-seq2", count=450),
            FacetBucket(value="Drop-seq", count=250),
        ],
    )


@pytest.fixture
def empty_summary_response():
    """Empty summary response from the API."""
    return SummaryResponse(
        field="tissue", query="nonexistent", total_buckets=0, facets=[]
    )


class TestValidFieldChoices:
    """Test that valid field choices work correctly."""

    @pytest.mark.parametrize(
        "field",
        [
            "assay",
            "assay_ontology_term_id",
            "tissue",
            "tissue_ontology_term_id",
            "organism",
            "organism_ontology_term_id",
            "disease",
            "disease_ontology_term_id",
            "tissue_type",
            "cell_type",
            "development_stage",
            "development_stage_ontology_term_id",
        ],
    )
    def test_valid_fields(self, field, mock_token_manager, sample_summary_response):
        """Test that all valid CrossModalitySchemaFields are accepted."""
        runner = CliRunner()

        # Update the response field to match the requested field
        sample_summary_response.field = field

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            mock_api.return_value = sample_summary_response

            result = runner.invoke(summary_command, [field])

            assert result.exit_code == 0
            assert "Summary: Dataset Counts by Field Value" in result.output
            assert field in result.output

            # Verify API was called with correct parameters
            mock_api.assert_called_once_with(
                id_token="mock_id_token", field=field, term="*"
            )

    def test_case_sensitive_field(self, mock_token_manager, sample_summary_response):
        """Test that field names are case-insensitive."""
        runner = CliRunner()

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            mock_api.return_value = sample_summary_response

            # Test with uppercase
            result = runner.invoke(summary_command, ["ASSAY"])
            assert result.exit_code == 0

            # Test with mixed case
            result = runner.invoke(summary_command, ["Tissue_Type"])
            assert result.exit_code == 0

    def test_with_search_term(self, mock_token_manager, sample_summary_response):
        """Test summary with a search query filter."""
        runner = CliRunner()

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            mock_api.return_value = sample_summary_response

            result = runner.invoke(summary_command, ["assay", "--query", "brain"])

            assert result.exit_code == 0
            mock_api.assert_called_once_with(
                id_token="mock_id_token", field="assay", term="brain"
            )


class TestInvalidFieldChoices:
    """Test that invalid field choices trigger correct error messages."""

    def test_invalid_field(self, mock_token_manager):
        """Test that invalid field names trigger the custom error message."""
        runner = CliRunner()

        result = runner.invoke(summary_command, ["invalid_field"])

        assert result.exit_code == 1
        assert (
            'Metadata FIELD "invalid_field" is not supported by summary command'
            in result.output
        )
        assert "Try: `vcp data summary --help` to see supported fields" in result.output

    def test_empty_field(self, mock_token_manager):
        """Test that empty field triggers error."""
        runner = CliRunner()

        result = runner.invoke(summary_command, [])

        assert result.exit_code == 2  # Click error for missing argument

    def test_multiple_invalid_fields(self, mock_token_manager):
        """Test behavior with multiple arguments (should only accept one)."""
        runner = CliRunner()

        result = runner.invoke(summary_command, ["assay", "tissue"])

        # Click should complain about unexpected argument
        assert result.exit_code == 2


class TestTableOutput:
    """Test the table output formatting."""

    def test_table_contains_facet_data(
        self, mock_token_manager, sample_summary_response
    ):
        """Test that the table properly displays facet data."""
        runner = CliRunner()

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            mock_api.return_value = sample_summary_response

            result = runner.invoke(summary_command, ["assay"])

            assert result.exit_code == 0

            # Check table title
            assert "Summary: Dataset Counts by Field Value" in result.output

            # Check column headers (implicitly through data presence)
            assert "assay" in result.output
            assert "Count" in result.output

            # Check facet values and counts
            assert "10x 3' v3" in result.output
            assert "1500" in result.output
            assert "10x 3' v2" in result.output
            assert "1200" in result.output
            assert "Smart-seq2" in result.output
            assert "800" in result.output

    def test_empty_facets_table(self, mock_token_manager, empty_summary_response):
        """Test table display when no facets are returned."""
        runner = CliRunner()

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            mock_api.return_value = empty_summary_response

            result = runner.invoke(
                summary_command, ["tissue", "--query", "nonexistent"]
            )

            assert result.exit_code == 0
            # Table should still be shown with headers but no data rows
            assert "Summary: Dataset Counts by Field Value" in result.output
            assert "tissue" in result.output


class TestPagination:
    """Test pagination handling."""

    def test_single_page_response(self, mock_token_manager):
        """Test handling of single-page response (no pagination needed)."""
        runner = CliRunner()

        response = SummaryResponse(
            field="organism",
            query="*",
            total_buckets=3,
            facets=[
                FacetBucket(value="Homo sapiens", count=5000),
                FacetBucket(value="Mus musculus", count=3000),
                FacetBucket(value="Rattus norvegicus", count=500),
            ],
        )

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            mock_api.return_value = response

            result = runner.invoke(summary_command, ["organism"])

            assert result.exit_code == 0
            # Verify all results are displayed
            assert "Homo sapiens" in result.output
            assert "5000" in result.output
            assert "Mus musculus" in result.output
            assert "3000" in result.output

            # API should be called once (no pagination)
            mock_api.assert_called_once()

    def test_large_facet_count(self, mock_token_manager):
        """Test handling when total_buckets indicates more results than returned."""
        runner = CliRunner()

        # Simulate a response where total_buckets > returned facets
        # (though the current implementation doesn't paginate)
        response = SummaryResponse(
            field="assay",
            query="*",
            total_buckets=100,  # More buckets exist
            facets=[
                FacetBucket(value=f"Assay_{i}", count=100 - i)
                for i in range(10)  # Only 10 returned
            ],
        )

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            mock_api.return_value = response

            result = runner.invoke(summary_command, ["assay"])

            assert result.exit_code == 0
            # Should display what was returned
            assert "Assay_0" in result.output
            assert "100" in result.output
            assert "Assay_9" in result.output
            assert "91" in result.output


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_no_tokens_present(self):
        """Test behavior when no authentication tokens are present."""
        runner = CliRunner()

        with patch("vcp.commands.data.summary.TOKEN_MANAGER") as mock:
            mock.load_tokens.return_value = None

            result = runner.invoke(summary_command, ["assay"])

            assert result.exit_code == 1  # Click commands return 0 even on error
            assert "Error: Not authenticated" in result.output
            assert "run 'vcp login'" in result.output

    def test_api_exception_handling(self, mock_token_manager):
        """Test handling of API exceptions."""
        runner = CliRunner()

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            mock_api.side_effect = Exception("API Error")

            result = runner.invoke(summary_command, ["assay"])

            # Should propagate the exception
            assert result.exit_code == 1
            assert result.exception

    def test_help_output(self):
        """Test that --help shows all supported fields."""
        runner = CliRunner()

        result = runner.invoke(summary_command, ["--help"])

        assert result.exit_code == 0
        assert (
            "Summarize counts of matched datasets against a specified FIELD"
            in result.output
        )
        assert "Examples:" in result.output
        assert "vcp data summary assay" in result.output

        # Flatten newline and whitespace to ignore formatting of output content
        m = re.search(r"\{([A-z\|\s]+)\}", result.output)
        assert m and len(m.groups()) == 1

        concatenated_output = re.sub(r"\n\s*", "", str(m.groups(0)[0]))

        # Check that field choices are shown
        for fieldname in CrossModalitySchemaFields.__pydantic_fields__:
            if fieldname not in concatenated_output:
                print(fieldname)
            assert fieldname in concatenated_output


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow(self, mock_token_manager):
        """Test a complete workflow with various fields and terms."""
        runner = CliRunner()

        responses = {
            "assay": SummaryResponse(
                field="assay",
                query="10x",
                total_buckets=2,
                facets=[
                    FacetBucket(value="10x 3' v3", count=1000),
                    FacetBucket(value="10x 3' v2", count=800),
                ],
            ),
            "tissue": SummaryResponse(
                field="tissue",
                query="brain",
                total_buckets=3,
                facets=[
                    FacetBucket(value="brain", count=500),
                    FacetBucket(value="brain cortex", count=300),
                    FacetBucket(value="brain stem", count=100),
                ],
            ),
        }

        with patch("vcp.commands.data.summary.summary_data_api") as mock_api:
            # Test assay with query
            mock_api.return_value = responses["assay"]
            result = runner.invoke(summary_command, ["assay", "--query", "10x"])
            assert result.exit_code == 0
            assert "10x 3' v3" in result.output
            assert "1000" in result.output

            # Test tissue with query
            mock_api.return_value = responses["tissue"]
            result = runner.invoke(summary_command, ["tissue", "--query", "brain"])
            assert result.exit_code == 0
            assert "brain cortex" in result.output
            assert "300" in result.output
