"""Tests for the size utility functions."""

import pytest

from vcp.datasets.api import (
    CroissantLiteModel,
    DataItemSimplified,
    DatasetRecord,
    DatasetSizeModel,
    LocationModel,
)
from vcp.utils.size import (
    calculate_dataset_size_from_search_item,
    calculate_search_results_total_size,
    calculate_total_dataset_size,
    format_size_bytes,
    get_file_count_from_dataset,
    get_file_count_from_search_results,
    parse_content_size,
)


class TestFormatSizeBytes:
    """Test the format_size_bytes function."""

    @pytest.mark.parametrize(
        "size_bytes,expected",
        [
            (0, "0.0 B"),
            (512, "512.0 B"),
            (1536, "1.5 KB"),  # 1.5 * 1024
            (2097152, "2.0 MB"),  # 2 * 1024^2
            (1879065057, "1.8 GB"),  # ~1.8 * 1024^3
            (1099511627776, "1.0 TB"),  # 1024^4
            (-100, "Unknown"),
        ],
    )
    def test_format_various_sizes(self, size_bytes, expected):
        assert format_size_bytes(size_bytes) == expected


class TestParseContentSize:
    """Test the parse_content_size function."""

    @pytest.mark.parametrize(
        "input_value,expected",
        [
            # Edge cases
            (None, 0),
            ("", 0),
            ("invalid", 0),
            ("1.5 XB", 0),
            # Integer input
            (1024, 1024),
            # Plain number strings
            ("1024", 1024),
            ("1,879,065,057", 1879065057),
            # Units (test one case per unit type to verify logic)
            ("1024 B", 1024),
            ("1.5 KB", 1536),  # 1.5 * 1024
            ("2 MB", 2097152),  # 2 * 1024^2
            ("1.8 GB", int(1.8 * 1024 * 1024 * 1024)),
            # Case insensitive and spacing variations
            ("1.5KB", 1536),
            ("1.5 kb", 1536),
            # Binary units
            ("1 MiB", 1048576),  # 1024^2
        ],
    )
    def test_parse_various_formats(self, input_value, expected):
        assert parse_content_size(input_value) == expected


class TestDatasetSizeCalculation:
    """Test dataset size calculation functions."""

    def test_calculate_dataset_size_with_none_content_size(self):
        """Test the bug fix for None contentSize values."""
        item = DataItemSimplified(
            internal_id="test-id",
            name="Test Dataset",
            locations=[
                DatasetSizeModel(url="http://example.com/file1", contentSize=1024),
                DatasetSizeModel(url="http://example.com/file2", contentSize=None),
                DatasetSizeModel(url="http://example.com/file3", contentSize=2048),
            ],
        )

        total_size = calculate_dataset_size_from_search_item(item)
        assert total_size == 3072  # 1024 + 0 + 2048 (None is skipped)

    def test_calculate_dataset_size_mixed_location_types(self):
        """Test with mixed location types (DatasetSizeModel, LocationModel, string)."""
        item = DataItemSimplified(
            internal_id="test-id",
            name="Test Dataset",
            locations=[
                DatasetSizeModel(url="http://example.com/file1.h5ad", contentSize=1024),
                LocationModel(scheme="s3", path="bucket/file2.h5ad"),  # No size info
                "http://example.com/file3.html",  # Plain string, no size info
                DatasetSizeModel(url="http://example.com/file4.h5ad", contentSize=2048),
            ],
        )

        total_size = calculate_dataset_size_from_search_item(item)
        assert (
            total_size == 3072
        )  # Only DatasetSizeModel objects with contentSize count

    def test_calculate_search_results_total_size_with_none_values(self):
        """Test total size calculation across multiple datasets with None contentSize."""
        items = [
            DataItemSimplified(
                internal_id="dataset-1",
                name="Dataset 1",
                locations=[
                    DatasetSizeModel(url="http://example.com/file1", contentSize=1024),
                    DatasetSizeModel(url="http://example.com/file2", contentSize=None),
                ],
            ),
            DataItemSimplified(
                internal_id="dataset-2",
                name="Dataset 2",
                locations=[
                    LocationModel(scheme="http", path="example.com/file3"),  # No size
                    DatasetSizeModel(url="http://example.com/file4", contentSize=2048),
                ],
            ),
        ]

        total_size = calculate_search_results_total_size(items)
        assert total_size == 3072  # 1024 + 0 + 0 + 2048

    def test_calculate_total_dataset_size_from_md_distribution(self):
        """Test size calculation from md.distribution (primary source)."""
        record = DatasetRecord(
            internal_id="test-id",
            label="Test Dataset",
            type="dataset",
            external_id="ext-123",
            md=CroissantLiteModel(
                distribution=[
                    {
                        "@type": "cr:FileObject",
                        "@id": "file1",
                        "name": "data.h5ad",
                        "contentUrl": "http://example.com/data.h5ad",
                        "contentSize": "1024",  # String format
                        "encodingFormat": "application/x-hdf5",
                    },
                    {
                        "@type": "cr:FileObject",
                        "@id": "file2",
                        "name": "metadata.csv",
                        "contentUrl": "http://example.com/metadata.csv",
                        "contentSize": "2.5 KB",  # With units
                        "encodingFormat": "text/csv",
                    },
                ]
            ),
        )

        total_size = calculate_total_dataset_size(record)
        assert total_size == 1024 + 2560  # 1024 + (2.5 * 1024)

    def test_calculate_total_dataset_size_fallback_to_record_distribution(self):
        """Test fallback to record.distribution when md is empty."""
        # Note: This would need FileObject imports and proper setup
        # For now, test the case where both md and record.distribution are empty
        record = DatasetRecord(
            internal_id="test-id",
            label="Test Dataset",
            type="dataset",
            external_id="ext-123",
            md=None,
        )

        total_size = calculate_total_dataset_size(record)
        assert total_size == 0


class TestFileCountCalculation:
    """Test file count calculation functions."""

    def test_get_file_count_from_dataset_md_distribution(self):
        """Test file count from md.distribution."""
        record = DatasetRecord(
            internal_id="test-id",
            label="Test Dataset",
            type="dataset",
            external_id="ext-123",
            md=CroissantLiteModel(
                distribution=[
                    {"@id": "file1", "name": "data.h5ad"},
                    {"@id": "file2", "name": "metadata.csv"},
                    {"@id": "file3", "name": "readme.txt"},
                ]
            ),
        )

        file_count = get_file_count_from_dataset(record)
        assert file_count == 3

    def test_get_file_count_from_dataset_locations_fallback(self):
        """Test fallback to locations when no distribution."""
        record = DatasetRecord(
            internal_id="test-id",
            label="Test Dataset",
            type="dataset",
            external_id="ext-123",
            locations=[
                "http://example.com/file1.h5ad",
                "http://example.com/file2.csv",
            ],
        )

        file_count = get_file_count_from_dataset(record)
        assert file_count == 2

    def test_get_file_count_from_search_results_mixed_types(self):
        """Test file count from search results with mixed location types."""
        items = [
            DataItemSimplified(
                internal_id="dataset-1",
                name="Dataset 1",
                locations=[
                    DatasetSizeModel(url="http://example.com/file1", contentSize=1024),
                    LocationModel(scheme="s3", path="bucket/file2"),  # Not counted
                ],
            ),
            DataItemSimplified(
                internal_id="dataset-2",
                name="Dataset 2",
                locations=[
                    "http://example.com/file3",  # String, not counted
                    DatasetSizeModel(url="http://example.com/file4", contentSize=2048),
                    DatasetSizeModel(url="http://example.com/file5", contentSize=None),
                ],
            ),
        ]

        file_count = get_file_count_from_search_results(items)
        assert file_count == 3  # Only DatasetSizeModel objects count as files


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_datasets(self):
        """Test functions with empty input."""
        empty_item = DataItemSimplified(internal_id="empty", name="Empty", locations=[])

        assert calculate_dataset_size_from_search_item(empty_item) == 0
        assert calculate_search_results_total_size([empty_item]) == 0
        assert get_file_count_from_search_results([empty_item]) == 0

    def test_all_none_content_sizes(self):
        """Test datasets where all files have None contentSize."""
        item = DataItemSimplified(
            internal_id="test-id",
            name="No Sizes Dataset",
            locations=[
                DatasetSizeModel(url="http://example.com/file1", contentSize=None),
                DatasetSizeModel(url="http://example.com/file2", contentSize=None),
            ],
        )

        assert calculate_dataset_size_from_search_item(item) == 0
        assert get_file_count_from_search_results([item]) == 2  # Files still count
