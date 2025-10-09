"""
Tests for the TensorPool CLI newcluster commands.

This module tests the CLI's cluster management functionality including:
- Creating clusters (specifically 1xH100 instances)
- Listing clusters
- Destroying clusters

Note: These tests make real API calls to test functionality end-to-end.
"""

import pytest
import os
import tempfile
from typing import Tuple, Dict, Any

# Import the functions we're testing
from tensorpool.helpers import newcluster_create, newcluster_list, newcluster_destroy


class TestNewClusterCreate:
    """Test cases for the newcluster create command."""

    @pytest.fixture
    def temp_ssh_key_file(self) -> str:
        """Create a temporary SSH public key file for testing."""
        ssh_key_content = (
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7vbqajDhwN5b... user@example.com"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pub", delete=False) as f:
            f.write(ssh_key_content)
            return f.name

    def test_create_with_working_ssh_key(self, temp_ssh_key_file: str) -> None:
        """Test cluster creation with a valid SSH key file (requires API key in env)."""
        # This test requires TENSORPOOL_KEY to be set in environment
        if not os.environ.get("TENSORPOOL_KEY"):
            pytest.skip(
                "TENSORPOOL_KEY environment variable not set - skipping real API test"
            )

        success, message = newcluster_create(
            identity_file=temp_ssh_key_file,
            instance_type="1xH100",
            name="test-cluster",
            num_nodes=1,
        )

        # Clean up temp file
        os.unlink(temp_ssh_key_file)

        # The actual result depends on the API response
        # We just test that we get a proper response format
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert len(message) > 0

    def test_create_invalid_num_nodes(self) -> None:
        """Test cluster creation fails with invalid number of nodes."""
        # Set temporary API key to pass the validation
        original_key = os.environ.get("TENSORPOOL_KEY")
        os.environ["TENSORPOOL_KEY"] = "test_key_for_validation"

        try:
            success, message = newcluster_create(
                identity_file="~/.ssh/id_rsa.pub",
                instance_type="1xH100",
                name=None,
                num_nodes=0,
            )

            assert success is False
            assert "Number of nodes must be at least 1" in message
        finally:
            # Restore original key
            if original_key:
                os.environ["TENSORPOOL_KEY"] = original_key
            else:
                del os.environ["TENSORPOOL_KEY"]

    def test_create_ssh_key_not_found(self) -> None:
        """Test cluster creation fails when SSH key file doesn't exist."""
        # Set temporary API key to pass the first validation
        original_key = os.environ.get("TENSORPOOL_KEY")
        os.environ["TENSORPOOL_KEY"] = "test_key_for_validation"

        try:
            success, message = newcluster_create(
                identity_file="~/.ssh/nonexistent.pub",
                instance_type="1xH100",
                name=None,
                num_nodes=1,
            )

            assert success is False
            assert "SSH key file not found" in message
        finally:
            # Restore original key
            if original_key:
                os.environ["TENSORPOOL_KEY"] = original_key
            else:
                del os.environ["TENSORPOOL_KEY"]

    def test_create_with_invalid_ssh_key(self) -> None:
        """Test cluster creation fails with invalid SSH key content."""
        # Set temporary API key to pass the first validation
        original_key = os.environ.get("TENSORPOOL_KEY")
        os.environ["TENSORPOOL_KEY"] = "test_key_for_validation"

        # Create temp file with invalid SSH key content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pub", delete=False) as f:
            f.write("invalid ssh key content")
            temp_file = f.name

        try:
            success, message = newcluster_create(
                identity_file=temp_file, instance_type="1xH100", name=None, num_nodes=1
            )

            # Clean up temp file
            os.unlink(temp_file)

            # The API should reject invalid SSH key format
            assert success is False
            assert "invalid" in message.lower() or "error" in message.lower()
        finally:
            # Restore original key
            if original_key:
                os.environ["TENSORPOOL_KEY"] = original_key
            else:
                del os.environ["TENSORPOOL_KEY"]


class TestNewClusterList:
    """Test cases for the newcluster list command."""

    def test_list_clusters_real_api(self) -> None:
        """Test cluster listing with real API calls (requires API key in env)."""
        if not os.environ.get("TENSORPOOL_KEY"):
            pytest.skip(
                "TENSORPOOL_KEY environment variable not set - skipping real API test"
            )

        success, message = newcluster_list()

        # Actual results depend, just check proper response format
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert len(message) > 0


class TestNewClusterDestroy:
    """Test cases for the newcluster destroy command."""

    # def test_destroy_no_api_key(self) -> None:
    #     """Test cluster destruction fails when no API key is available."""
    #     # Temporarily remove API key from environment
    #     original_key = os.environ.get('TENSORPOOL_KEY')
    #     if original_key:
    #         del os.environ['TENSORPOOL_KEY']

    #     try:
    #         success, message = newcluster_destroy("cluster_123")

    #         assert success is False
    #         assert "TENSORPOOL_KEY not found" in message
    #     finally:
    #         # Restore original key if it existed
    #         if original_key:
    #             os.environ['TENSORPOOL_KEY'] = original_key
