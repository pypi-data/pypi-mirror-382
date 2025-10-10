"""Tests for the enhanced describe command."""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests
from click.testing import CliRunner

from vcp.commands.data.describe import describe_command
from vcp.datasets.api import DatasetRecord, PropertyValue, create_data_item_from_dataset


@pytest.fixture
def sample_dataset_response():
    """Sample dataset response from the API."""
    return {
        "internal_id": "688bc7xxxxxxxxxxxxxxxxx",
        "label": "Liver",
        "version": "6.0.0",
        "type": "h5ad",
        "owner": "",
        "org": "CZI",
        "external_id": "35e73102-xxxx-xxxx-xxxx-86bb587102bf",
        "version_of": [],
        "transformation_of": [],
        "locations": [
            {
                "scheme": "cellxgene",
                "path": "https://datasets.cellxgene.cziscience.com/35e73102-xxxx-xxxx-xxxx-86bb587102bf.h5ad",
            }
        ],
        "scopes": ["public"],
        "tags": ["namespace:cellxgene"],
        "md": {
            "@context": {
                "@language": "en",
                "@vocab": "https://schema.org/",
            },
            "@type": "sc:Dataset",
            "conformsTo": "http://mlcommons.org/croissant/1.0",
            "name": "Liver",
            "description": "",
            "version": "6.0.0",
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "creator": {"@type": "Organization", "name": "CZI"},
            "citation": "https://doi.org/10.1016/j.cell.2023.11.026",
            "citeAs": "Publication: https://doi.org/10.1016/j.cell.2023.11.026 Dataset Version: https://datasets.cellxgene.cziscience.com/35e73102-xxxx-xxxx-xxxx-86bb587102bf.h5ad curated and distributed by CZ CELLxGENE Discover in Collection: https://cellxgene.cziscience.com/collections/854c0855-23ad-4362-8b77-6b1639e7a9fc",
            "keywords": ["transcriptomics", "h5ad", "cellxgene"],
            "variableMeasured": [
                {
                    "@type": "PropertyValue",
                    "name": "assay",
                    "value": ["10x 3' v3", "10x 3' v2", "CEL-seq2"],
                },
                {
                    "@type": "PropertyValue",
                    "name": "assay_ontology_term_id",
                    "value": ["EFO:0009899", "EFO:0010010", "EFO:0009922"],
                },
                {
                    "@type": "PropertyValue",
                    "name": "development_stage",
                    "value": ["adult stage", "45-year-old stage", "66-year-old stage"],
                },
                {
                    "@type": "PropertyValue",
                    "name": "development_stage_ontology_term_id",
                    "value": ["HsapDv:0000128", "HsapDv:0000143", "HsapDv:0000138"],
                },
                {"@type": "PropertyValue", "name": "disease", "value": ["normal"]},
                {
                    "@type": "PropertyValue",
                    "name": "disease_ontology_term_id",
                    "value": ["PATO:0000461"],
                },
                {
                    "@type": "PropertyValue",
                    "name": "organism",
                    "value": ["Homo sapiens"],
                },
                {
                    "@type": "PropertyValue",
                    "name": "organism_ontology_term_id",
                    "value": ["NCBITaxon:9606"],
                },
                {
                    "@type": "PropertyValue",
                    "name": "tissue",
                    "value": ["caudate lobe of liver", "liver"],
                },
                {
                    "@type": "PropertyValue",
                    "name": "tissue_ontology_term_id",
                    "value": ["UBERON:0002107", "UBERON:0001117"],
                },
                {"@type": "PropertyValue", "name": "tissue_type", "value": ["tissue"]},
                {
                    "@type": "PropertyValue",
                    "name": "cell_count",
                    "value": 259678,
                    "description": "Number of cells in the dataset",
                },
            ],
            "distribution": [
                {
                    "@type": "cr:FileObject",
                    "@id": "h5ad-file",
                    "name": "h5ad-file",
                    "description": "Data file accessible via h5ad",
                    "contentUrl": "https://datasets.cellxgene.cziscience.com/35e73102-xxxx-xxxx-xxxx-86bb587102bf.h5ad",
                    "contentSize": "1879065057 B",
                    "encodingFormat": "application/x-h5ad",
                    "sha256": "sha256",
                }
            ],
        },
    }


@pytest.fixture
def sample_dataset_response_bibtex_doi(sample_dataset_response):
    """Sample dataset response with DOI in bibtex format."""
    response = sample_dataset_response.copy()
    response["md"]["citeAs"] = (
        '@article{example2024, title="Example Article", doi="10.1109/TMI.2024.3398401"}'
    )
    return response


@pytest.fixture
def sample_dataset_response_no_org(sample_dataset_response):
    """Sample dataset response without Organization type creator."""
    response = sample_dataset_response.copy()
    response["md"]["creator"] = {"@type": "Person", "name": "John Doe"}
    return response


@pytest.fixture
def mock_token_manager():
    """Mock TokenManager with valid tokens."""
    with patch("vcp.commands.data.describe.TOKEN_MANAGER") as mock:
        mock_tokens = MagicMock()
        mock_tokens.id_token = "mock_id_token"
        mock.load_tokens.return_value = mock_tokens
        yield mock


@pytest.fixture
def sample_nested_propertyValue():
    return {
        "@type": "PropertyValue",
        "name": "runs",
        "description": "Tomographic acquisition runs",
        "additionalProperty": [
            {
                "@type": "PropertyValue",
                "name": "pda2020-11-04-11",
                "description": "Tomographic acquisition run pda2020-11-04-11",
                "propertyID": "RN-1591",
                "additionalProperty": [
                    {
                        "@type": "PropertyValue",
                        "name": "data_types",
                        "value": ["frames", "tiltseries", "tomograms"],
                    }
                ],
            }
        ],
    }


def test_describe_command_tabular_output(sample_dataset_response, mock_token_manager):
    """Test that describe command produces tabular output with all required fields."""
    runner = CliRunner()

    with patch("vcp.commands.data.describe.get_dataset_api") as mock_get:
        # Create DatasetRecord from sample response
        record = DatasetRecord.model_validate(sample_dataset_response)
        mock_get.return_value = record

        result = runner.invoke(describe_command, ["688bc7xxxxxxxxxxxxxxxxx"])

        # Check command succeeded
        assert result.exit_code == 0

        # Check for table titles
        assert "Basic Information" in result.output
        assert "Biological Metadata" in result.output
        assert "Distribution / Assets" in result.output

        # Check Basic Information fields
        assert "Dataset Name" in result.output
        assert "Domain" in result.output
        assert "Liver" in result.output
        assert "Version" in result.output
        assert "6.0.0" in result.output
        assert "Dataset License Terms" in result.output
        assert "https://creativecommons.org/licenses/by/4.0/" in result.output
        assert "Dataset Owner" in result.output
        assert "CZI" in result.output
        assert "DOI" in result.output
        assert "10.1016/j.cell.2023.11.026" in result.output

        # Check Biological Metadata fields
        assert "Assay Ontology Term ID" in result.output
        assert "EFO:0009899" in result.output
        assert "Assay" in result.output
        assert "10x 3' v3" in result.output
        assert "Organism" in result.output
        assert "Homo sapiens" in result.output
        assert "Tissue" in result.output
        assert "liver" in result.output
        assert "Disease" in result.output
        assert "normal" in result.output

        # Check Distribution/Assets
        assert "application/x-h5ad" in result.output
        assert (
            "1.8 GB" in result.output
        )  # Size is now formatted to human readable format
        # URL might be truncated, so check for partial match
        assert (
            "https://datasets.cellxgene" in result.output
            or "cellxgene" in result.output
        )


def test_describe_command_raw_output(sample_dataset_response, mock_token_manager):
    """Test that --raw flag returns raw JSON."""
    runner = CliRunner()

    with patch("vcp.commands.data.describe.get_dataset_api_raw") as mock_get:
        mock_get.return_value = sample_dataset_response

        result = runner.invoke(describe_command, ["688bc7xxxxxxxxxxxxxxxxx", "--raw"])

        assert result.exit_code == 0
        # Output should be valid JSON
        output_json = json.loads(result.output.strip())
        assert output_json["internal_id"] == "688bc7xxxxxxxxxxxxxxxxx"


def test_describe_command_full_output(sample_dataset_response, mock_token_manager):
    """Test that --full flag returns complete JSON."""
    runner = CliRunner()

    with patch("vcp.commands.data.describe.get_dataset_api") as mock_get:
        record = DatasetRecord.model_validate(sample_dataset_response)
        mock_get.return_value = record

        result = runner.invoke(describe_command, ["688bc7xxxxxxxxxxxxxxxxx", "--full"])

        assert result.exit_code == 0
        # Output should be valid JSON with model field names
        output_json = json.loads(result.output)
        assert output_json["internal_id"] == "688bc7xxxxxxxxxxxxxxxxx"
        assert "md" in output_json  # Check md field exists
        # Check that md contains variableMeasured with alias
        if output_json["md"]:
            assert "variableMeasured" in output_json["md"]


def test_describe_command_no_tokens():
    """Test that command fails gracefully when no tokens are present."""
    runner = CliRunner()

    with patch("vcp.commands.data.describe.TOKEN_MANAGER") as mock:
        mock.load_tokens.return_value = None

        result = runner.invoke(describe_command, ["688bc7xxxxxxxxxxxxxxxxx"])

        assert result.exit_code == 1  # Click commands return 0 even on error
        assert "Error: Not authenticated" in result.output
        assert "run 'vcp login'" in result.output


def test_doi_extraction_from_bibtex(
    sample_dataset_response_bibtex_doi, mock_token_manager
):
    """Test that DOI is correctly extracted from bibtex citation."""
    runner = CliRunner()

    with patch("vcp.commands.data.describe.get_dataset_api") as mock_get:
        record = DatasetRecord.model_validate(sample_dataset_response_bibtex_doi)
        mock_get.return_value = record

        result = runner.invoke(describe_command, ["688bc7xxxxxxxxxxxxxxxxx"])

        assert result.exit_code == 0
        assert "10.1109/TMI.2024.3398401" in result.output


def test_organization_extraction(sample_dataset_response_no_org, mock_token_manager):
    """Test that only Organization type creators are shown as Dataset Owner."""
    runner = CliRunner()

    with patch("vcp.commands.data.describe.get_dataset_api") as mock_get:
        record = DatasetRecord.model_validate(sample_dataset_response_no_org)
        mock_get.return_value = record

        result = runner.invoke(describe_command, ["688bc7xxxxxxxxxxxxxxxxx"])

        assert result.exit_code == 0
        # Should fall back to org field since creator is not Organization
        assert "CZI" in result.output
        # Person name should not appear as owner
        assert "John Doe" not in result.output


def test_data_item_conversion(sample_dataset_response):
    """Test that DatasetRecord correctly converts to DataItem using factory function."""
    record = DatasetRecord.model_validate(sample_dataset_response)
    data_item = create_data_item_from_dataset(record)

    # Check biological metadata fields are extracted
    assert data_item.assay == ["10x 3' v3", "10x 3' v2", "CEL-seq2"]
    assert data_item.assay_ontology_term_id == [
        "EFO:0009899",
        "EFO:0010010",
        "EFO:0009922",
    ]
    assert data_item.organism == ["Homo sapiens"]
    assert data_item.organism_ontology_term_id == ["NCBITaxon:9606"]
    assert data_item.tissue == ["caudate lobe of liver", "liver"]
    assert data_item.tissue_ontology_term_id == ["UBERON:0002107", "UBERON:0001117"]
    assert data_item.disease == ["normal"]
    assert data_item.disease_ontology_term_id == ["PATO:0000461"]
    assert data_item.tissue_type == ["tissue"]

    # Check basic fields
    assert data_item.internal_id == "688bc7xxxxxxxxxxxxxxxxx"
    assert data_item.name == "Liver"


def test_missing_metadata_fields(mock_token_manager):
    """Test that missing metadata fields are handled gracefully."""
    runner = CliRunner()

    test_id = "123456789012345678901234567890"  # Valid format dataset ID
    minimal_response = {
        "internal_id": test_id,
        "label": "Test Dataset",
        "type": "h5ad",
        "external_id": "ext123",
        "locations": [],
        "tags": [],
        "scopes": [],
        "version_of": [],
        "transformation_of": [],
        "md": {
            "@context": {"@language": "en", "@vocab": "https://schema.org/"},
            "@type": "sc:Dataset",
            "name": "Test Dataset",
            # Missing description, creator, license, citation, variableMeasured, distribution
        },
    }

    with patch("vcp.commands.data.describe.get_dataset_api") as mock_get:
        record = DatasetRecord.model_validate(minimal_response)
        mock_get.return_value = record

        result = runner.invoke(describe_command, [test_id])

        assert result.exit_code == 0
        # Check that missing fields show placeholder
        assert "—" in result.output
        assert "Test Dataset" in result.output


def test_nested_property_value_handling(sample_nested_propertyValue):
    r = PropertyValue.model_validate(sample_nested_propertyValue)
    assert isinstance(r, PropertyValue)
    assert r.additionalProperty is not None and isinstance(r.additionalProperty, list)
    assert isinstance(r.additionalProperty[0], PropertyValue)


def test_describe_command_invalid_dataset_id_short():
    """Test that short invalid dataset ID shows validation error."""
    runner = CliRunner()

    # Test with a clearly invalid short ID
    result = runner.invoke(describe_command, ["test"])

    assert result.exit_code == 1  # Command doesn't fail, just shows error
    assert "Error: Invalid dataset ID:" in result.output
    assert (
        "Dataset IDs should be \nlong alphanumeric strings (20+ characters)"
        in result.output
    )
    # assert "vcp data search" in result.output
    assert "vcp data describe --help" in result.output


def test_describe_command_invalid_dataset_id_symbols():
    """Test that dataset ID with invalid characters shows validation error."""
    runner = CliRunner()

    # Test with invalid characters
    result = runner.invoke(describe_command, ["invalid@dataset#id$with%symbols"])

    assert result.exit_code == 1
    assert "Error: Invalid dataset ID:" in result.output
    assert (
        "Dataset IDs should be long alphanumeric strings (20+ characters)"
        in result.output
    )
    assert "vcp data describe --help" in result.output


def test_describe_command_valid_format_but_not_found(mock_token_manager):
    """Test that valid format but non-existent dataset ID shows 404 error."""
    runner = CliRunner()

    with patch("vcp.commands.data.describe.get_dataset_api") as mock_get:
        # Mock a 404 HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = requests.exceptions.HTTPError(response=mock_response)
        http_error.response = mock_response
        mock_get.side_effect = http_error

        result = runner.invoke(describe_command, ["688bc7fe111f194a9ff123nonexistent"])

        assert result.exit_code == 1
        assert "Dataset '688bc7fe111f194a9ff123nonexistent' not found" in result.output
        assert "Please check that the dataset ID is correct." in result.output


def test_describe_command_http_error_other_than_404(mock_token_manager):
    """Test that non-404 HTTP errors are re-raised."""
    runner = CliRunner()

    with patch("vcp.commands.data.describe.get_dataset_api") as mock_get:
        # Mock a 503 HTTPError (service unavailable)
        mock_response = MagicMock()
        mock_response.status_code = 503
        http_error = requests.exceptions.HTTPError(
            "503 Service Unavailable", response=mock_response
        )
        http_error.response = mock_response
        mock_get.side_effect = http_error

        result = runner.invoke(
            describe_command,
            ["688bc7fe111f194a9ff123validformat"],
            catch_exceptions=False,
        )
        assert result.exit_code == 1
        assert "Error: Server error occurred" in result.output
        assert "Please try again later." in result.output
