import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vcp.datasets.api import DataItemSimplified, SearchResponse
from vcp.datasets.download import download_from_candidates_db
from vcp.datasets.download_db import DownloadCandidate, DownloadDatabase


@pytest.fixture
def temp_downloads_dir():
    """Create a temporary directory for downloads testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def download_db(temp_downloads_dir):
    """Create a DownloadDatabase instance with temporary directory."""
    return DownloadDatabase(downloads_dir=temp_downloads_dir)


@pytest.fixture
def sample_search_response():
    """Create a sample search response for testing."""
    return SearchResponse(
        data=[
            Mock(
                internal_id="dataset1",
                name="Test Dataset 1",
                namespace="test_namespace",
                locations=["s3://bucket/path1.h5ad", "s3://bucket/path2.h5ad"],
            ),
            Mock(
                internal_id="dataset2",
                name="Test Dataset 2",
                namespace="test_namespace",
                locations=["https://example.com/file.h5ad"],
            ),
        ],
        cursor="next_page_cursor",
        credentials={"access_key": "test", "secret_key": "test"},
    )


class TestDownloadDatabase:
    """Test DownloadDatabase functionality."""

    def test_downloads_directory_creation(self, temp_downloads_dir):
        """Test that downloads directory is created."""
        db = DownloadDatabase(downloads_dir=temp_downloads_dir)
        assert Path(temp_downloads_dir).exists()
        assert db.downloads_dir == Path(temp_downloads_dir)

    def test_db_path_generation(self, download_db):
        """Test database path generation with expiration date."""
        search_term = "test search"
        expiration_date = datetime(2024, 12, 25)

        db_path = download_db._get_db_path(search_term, expiration_date)

        assert "testsearch" in str(db_path)
        assert "20241225" in str(db_path)
        assert db_path.suffix == ".db"

    def test_db_path_safe_filename(self, download_db):
        """Test that special characters are handled in filenames."""
        search_term = "test/search:with*special|chars"
        expiration_date = datetime(2024, 12, 25)

        db_path = download_db._get_db_path(search_term, expiration_date)

        # Should only contain safe characters
        filename = db_path.name
        assert "/" not in filename
        assert ":" not in filename
        assert "*" not in filename
        assert "|" not in filename

    def test_create_candidates_db(self, download_db):
        """Test database creation with proper schema."""
        search_term = "test"

        db_path, conn = download_db.create_candidates_db(search_term, "test query")

        # Check that database file was created
        assert db_path.exists()

        # Check that tables exist
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='download_candidates'
        """)
        assert cursor.fetchone() is not None

        # Check that indexes exist
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_%'
        """)
        indexes = cursor.fetchall()
        assert len(indexes) >= 2  # Should have at least 2 indexes

        conn.close()

    def test_insert_and_retrieve_candidates(self, download_db):
        """Test inserting and retrieving candidates."""
        search_term = "test"
        candidates = [
            DownloadCandidate(
                dataset_id="dataset1",
                dataset_name="Test Dataset 1",
                namespace="test_ns",
                location="s3://bucket/file1.h5ad",
            ),
            DownloadCandidate(
                dataset_id="dataset2",
                dataset_name="Test Dataset 2",
                namespace="test_ns",
                location="https://example.com/file2.h5ad",
            ),
        ]

        db_path, conn = download_db.create_candidates_db(search_term, "test query")
        download_db.insert_candidates(conn, candidates)
        conn.close()

        # Retrieve candidates
        retrieved = download_db.get_pending_candidates(db_path)

        assert len(retrieved) == 2
        assert retrieved[0].dataset_id == "dataset1"
        assert retrieved[0].dataset_name == "Test Dataset 1"
        assert retrieved[0].downloaded is False
        assert retrieved[1].dataset_id == "dataset2"

    def test_mark_downloaded(self, download_db):
        """Test marking candidates as downloaded."""
        search_term = "test"
        candidates = [
            DownloadCandidate(
                dataset_id="dataset1",
                dataset_name="Test Dataset 1",
                namespace="test_ns",
                location="s3://bucket/file1.h5ad",
            )
        ]

        db_path, conn = download_db.create_candidates_db(search_term, "test query")
        download_db.insert_candidates(conn, candidates)
        conn.close()

        # Mark as downloaded
        download_db.mark_downloaded(db_path, "dataset1", "s3://bucket/file1.h5ad")

        # Verify it's no longer pending
        pending = download_db.get_pending_candidates(db_path)
        assert len(pending) == 0

    @patch("vcp.datasets.download_db.search_data_api")
    def test_collect_candidates_from_search(self, mock_search_api, download_db):
        """Test collecting candidates from search API with pagination."""
        # Mock multiple pages of search results
        page1_response = SearchResponse(
            data=[
                DataItemSimplified(
                    internal_id="dataset1",
                    name="Dataset 1",
                    tags=["namespace:ns1"],
                    locations=["s3://bucket/file1.h5ad"],
                )
            ],
            cursor="cursor1",
            limit=1,  # Set limit to match data length so it doesn't exit early
            credentials={"access_key": "test"},
        )

        page2_response = SearchResponse(
            data=[
                DataItemSimplified(
                    internal_id="dataset2",
                    name="Dataset 2",
                    tags=["namespace:ns2"],
                    locations=["s3://bucket/file2.h5ad"],
                )
            ],
            cursor=None,  # Last page
            limit=1,  # Set limit to match data length
            credentials={"access_key": "test"},
        )

        mock_search_api.side_effect = [page1_response, page2_response]

        with patch("builtins.print"):  # Suppress print output
            db_path = download_db.collect_candidates_from_search(
                query="test query", id_token="fake_token", limit=100
            )

        # Verify database was created and candidates inserted
        assert db_path.exists()
        candidates = download_db.get_pending_candidates(db_path)
        assert len(candidates) == 2
        assert candidates[0].dataset_id == "dataset1"
        assert candidates[1].dataset_id == "dataset2"

        # Verify search API was called correctly
        assert mock_search_api.call_count == 2
        mock_search_api.assert_any_call(
            "fake_token", "test query", 100, None, exact=False
        )
        mock_search_api.assert_any_call(
            "fake_token", "test query", 100, "cursor1", exact=False
        )

    def test_collect_candidates_handles_multiple_locations(self, download_db):
        """Test that datasets with multiple locations create multiple candidates."""
        with patch("vcp.datasets.download_db.search_data_api") as mock_search_api:
            mock_search_api.return_value = SearchResponse(
                data=[
                    DataItemSimplified(
                        internal_id="dataset1",
                        name="Multi-location Dataset",
                        tags=["namespace:test_ns"],
                        locations=[
                            "s3://bucket/file1.h5ad",
                            "s3://bucket/file2.h5ad",
                            "https://example.com/file3.h5ad",
                        ],
                    )
                ],
                cursor=None,
                limit=100,
                credentials={"access_key": "test"},
            )

            with patch("builtins.print"):
                db_path = download_db.collect_candidates_from_search(
                    query="test query", id_token="fake_token"
                )

            candidates = download_db.get_pending_candidates(db_path)
            assert len(candidates) == 3  # One candidate per location
            assert all(c.dataset_id == "dataset1" for c in candidates)
            assert candidates[0].location == "s3://bucket/file1.h5ad"
            assert candidates[1].location == "s3://bucket/file2.h5ad"
            assert candidates[2].location == "https://example.com/file3.h5ad"

    @patch("vcp.datasets.download_db.search_data_api")
    def test_collect_candidates_rollback_on_error(self, mock_search_api, download_db):
        """Test that database is cleaned up if collection fails."""
        # Mock search to raise an error on second call
        page1_response = SearchResponse(
            data=[
                DataItemSimplified(
                    internal_id="dataset1",
                    name="Dataset 1",
                    tags=["namespace:ns1"],
                    locations=["s3://bucket/file1.h5ad"],
                )
            ],
            cursor="cursor1",
            limit=1,
            credentials={"access_key": "test"},
        )

        mock_search_api.side_effect = [page1_response, Exception("Network error")]

        with pytest.raises(Exception, match="Network error"):
            with patch("builtins.print"):
                download_db.collect_candidates_from_search(
                    query="test query",
                    id_token="fake_token",
                    limit=100,
                )

        # Verify no database files were left behind
        db_files = list(download_db.downloads_dir.glob("*.db"))
        assert len(db_files) == 0

    @patch("vcp.datasets.download_db.search_data_api")
    def test_collect_candidates_atomic_transaction(self, mock_search_api, download_db):
        """Test that all candidates are committed atomically."""
        page1_response = SearchResponse(
            data=[
                DataItemSimplified(
                    internal_id="dataset1",
                    name="Dataset 1",
                    tags=["namespace:ns1"],
                    locations=["s3://bucket/file1.h5ad"],
                )
            ],
            cursor=None,  # Single page
            limit=1,
            credentials={"access_key": "test"},
        )

        mock_search_api.return_value = page1_response

        with patch("builtins.print"):
            db_path = download_db.collect_candidates_from_search(
                query="test query", id_token="fake_token"
            )

        # Verify database exists and has data only after successful completion
        assert db_path.exists()
        candidates = download_db.get_pending_candidates(db_path)
        assert len(candidates) == 1
        assert candidates[0].dataset_id == "dataset1"


class TestResumefunctionality:
    """Test resume functionality with query matching and expiration."""

    def test_find_existing_candidates_db_match(self, download_db):
        """Test finding existing database with matching query."""
        query = "domain:microscopy"

        # Create a database with the query
        db_path, conn = download_db.create_candidates_db("microscopy", query)
        conn.close()

        # Should find the matching database
        found_db = download_db.find_existing_candidates_db(query)
        assert found_db == db_path

    def test_find_existing_candidates_db_no_match(self, download_db):
        """Test that non-matching queries return None."""
        query1 = "domain:microscopy"
        query2 = "domain:transcriptomics"

        # Create database with query1
        _, conn = download_db.create_candidates_db("microscopy", query1)
        conn.close()

        # Should not find database when searching with query2
        found_db = download_db.find_existing_candidates_db(query2)
        assert found_db is None

    def test_find_existing_candidates_db_expired(self, download_db):
        """Test that expired databases are not returned."""
        query = "domain:microscopy"

        # Create database with past expiration date
        past_date = datetime.now() - timedelta(hours=1)
        db_path = download_db._get_db_path("microscopy", past_date)

        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE query_metadata (
                id INTEGER PRIMARY KEY,
                query TEXT NOT NULL,
                search_term TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        conn.execute(
            """
            INSERT INTO query_metadata (query, search_term, expires_at)
            VALUES (?, ?, ?)
        """,
            (query, "microscopy", past_date),
        )
        conn.commit()
        conn.close()

        # Should not find expired database
        found_db = download_db.find_existing_candidates_db(query)
        assert found_db is None

    def test_get_database_stats(self, download_db):
        """Test getting database statistics."""
        candidates = [
            DownloadCandidate(
                dataset_id="dataset1",
                dataset_name="Dataset 1",
                namespace="test_ns",
                location="s3://bucket/file1.h5ad",
            ),
            DownloadCandidate(
                dataset_id="dataset2",
                dataset_name="Dataset 2",
                namespace="test_ns",
                location="s3://bucket/file2.h5ad",
                downloaded=True,
            ),
        ]

        db_path, conn = download_db.create_candidates_db("test", "test query")
        download_db.insert_candidates(conn, candidates)
        conn.close()

        total, pending = download_db.get_database_stats(db_path)
        assert total == 2
        assert pending == 1  # Only one not downloaded

    def test_cleanup_expired_databases(self, download_db):
        """Test cleanup of expired databases."""
        # Create expired database
        past_date = datetime.now() - timedelta(hours=1)
        expired_db_path = download_db._get_db_path("expired", past_date)

        conn = sqlite3.connect(str(expired_db_path))
        conn.execute("""
            CREATE TABLE query_metadata (
                id INTEGER PRIMARY KEY,
                query TEXT NOT NULL,
                search_term TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        conn.execute(
            """
            INSERT INTO query_metadata (query, search_term, expires_at)
            VALUES (?, ?, ?)
        """,
            ("old query", "expired", past_date),
        )
        conn.commit()
        conn.close()

        # Create valid database
        future_date = datetime.now() + timedelta(hours=1)
        valid_db_path = download_db._get_db_path("valid", future_date)
        conn = sqlite3.connect(str(valid_db_path))
        conn.execute("""
            CREATE TABLE query_metadata (
                id INTEGER PRIMARY KEY,
                query TEXT NOT NULL,
                search_term TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        conn.execute(
            """
            INSERT INTO query_metadata (query, search_term, expires_at)
            VALUES (?, ?, ?)
        """,
            ("current query", "valid", future_date),
        )
        conn.commit()
        conn.close()

        # Run cleanup
        removed_count = download_db.cleanup_expired_databases()

        # Should have removed 1 database
        assert removed_count == 1
        assert not expired_db_path.exists()
        assert valid_db_path.exists()


class TestBatchedDownload:
    """Test batched download functionality."""

    @patch("vcp.datasets.download.get_credentials_for_datasets")
    @patch("vcp.datasets.download.download_locations")
    def test_batched_credential_download(
        self, mock_download_locations, mock_get_credentials, download_db
    ):
        """Test that downloads use batched credential requests."""
        # Create database with candidates
        candidates = [
            DownloadCandidate(
                dataset_id="dataset1",
                dataset_name="Dataset 1",
                namespace="test_ns",
                location="s3://bucket/file1.h5ad",
            ),
            DownloadCandidate(
                dataset_id="dataset2",
                dataset_name="Dataset 2",
                namespace="test_ns",
                location="s3://bucket/file2.h5ad",
            ),
        ]

        db_path, conn = download_db.create_candidates_db("test", "test query")
        download_db.insert_candidates(conn, candidates)
        conn.close()

        # Mock credentials API - now returns nested structure
        mock_get_credentials.return_value = {
            "credentials": {
                "access_key_id": "test_access_key",
                "secret_access_key": "test_secret_key",
                "session_token": "test_session_token",
            }
        }

        with patch("builtins.print"):  # Suppress console output
            download_from_candidates_db(
                db_path=str(db_path), id_token="fake_token", outdir="/tmp/test"
            )

        # Verify credentials were requested individually for each dataset
        assert mock_get_credentials.call_count == 2
        mock_get_credentials.assert_any_call("fake_token", ["dataset1"])
        mock_get_credentials.assert_any_call("fake_token", ["dataset2"])

        # Verify download_locations was called for each dataset
        assert mock_download_locations.call_count == 2

    @patch("vcp.datasets.download.get_credentials_for_datasets")
    @patch("vcp.datasets.download.download_locations")
    def test_individual_download_many_datasets(
        self, mock_download_locations, mock_get_credentials, download_db
    ):
        """Test that many datasets are downloaded with individual credential requests."""
        # Create 3 candidates to test individual credential fetching
        candidates = []
        for i in range(3):
            candidates.append(
                DownloadCandidate(
                    dataset_id=f"dataset{i}",
                    dataset_name=f"Dataset {i}",
                    namespace="test_ns",
                    location=f"s3://bucket/file{i}.h5ad",
                )
            )

        db_path, conn = download_db.create_candidates_db("test", "test query")
        download_db.insert_candidates(conn, candidates)
        conn.close()

        # Mock credentials API - returns nested structure
        mock_get_credentials.return_value = {
            "credentials": {
                "access_key_id": "test_access_key",
                "secret_access_key": "test_secret_key",
                "session_token": "test_session_token",
            }
        }

        with patch("builtins.print"):
            download_from_candidates_db(
                db_path=str(db_path), id_token="fake_token", outdir="/tmp/test"
            )

        # Verify credentials API was called individually for each dataset
        assert mock_get_credentials.call_count == 3

        # Verify each call was for a single dataset
        for i in range(3):
            mock_get_credentials.assert_any_call("fake_token", [f"dataset{i}"])

    @patch("vcp.datasets.download.get_credentials_for_datasets")
    @patch("vcp.datasets.download.download_locations")
    def test_individual_failure_continues_with_next_dataset(
        self, mock_download_locations, mock_get_credentials, download_db
    ):
        """Test that failure for one dataset doesn't stop processing of other datasets."""
        # Create 3 candidates for testing individual failures
        candidates = []
        for i in range(3):
            candidates.append(
                DownloadCandidate(
                    dataset_id=f"dataset{i}",
                    dataset_name=f"Dataset {i}",
                    namespace="test_ns",
                    location=f"s3://bucket/file{i}.h5ad",
                )
            )

        db_path, conn = download_db.create_candidates_db("test", "test query")
        download_db.insert_candidates(conn, candidates)
        conn.close()

        # Mock credentials API - first call fails, others succeed
        mock_get_credentials.side_effect = [
            Exception("Network error"),
            {
                "credentials": {
                    "access_key_id": "test_access_key",
                    "secret_access_key": "test_secret_key",
                    "session_token": "test_session_token",
                }
            },
            {
                "credentials": {
                    "access_key_id": "test_access_key",
                    "secret_access_key": "test_secret_key",
                    "session_token": "test_session_token",
                }
            },
        ]

        with patch("builtins.print"):
            download_from_candidates_db(
                db_path=str(db_path), id_token="fake_token", outdir="/tmp/test"
            )

        # Verify all datasets were attempted
        assert mock_get_credentials.call_count == 3

        # Verify downloads were only attempted for the successful datasets
        assert mock_download_locations.call_count == 2  # Only successful datasets


class TestDownloadCandidate:
    """Test DownloadCandidate model."""

    def test_download_candidate_creation(self):
        """Test basic candidate creation."""
        candidate = DownloadCandidate(
            dataset_id="test_id",
            dataset_name="Test Dataset",
            namespace="test_ns",
            location="s3://bucket/file.h5ad",
        )

        assert candidate.dataset_id == "test_id"
        assert candidate.dataset_name == "Test Dataset"
        assert candidate.namespace == "test_ns"
        assert candidate.location == "s3://bucket/file.h5ad"
        assert candidate.downloaded is False

    def test_download_candidate_optional_namespace(self):
        """Test candidate creation with optional namespace."""
        candidate = DownloadCandidate(
            dataset_id="test_id",
            dataset_name="Test Dataset",
            namespace=None,
            location="s3://bucket/file.h5ad",
        )

        assert candidate.namespace is None
        assert candidate.downloaded is False
