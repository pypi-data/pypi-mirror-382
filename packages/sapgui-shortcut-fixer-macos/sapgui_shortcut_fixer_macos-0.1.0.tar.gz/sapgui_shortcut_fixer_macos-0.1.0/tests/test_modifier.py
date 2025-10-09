"""
Unit tests for SAP file modifier
"""

import pytest
from sap_file_modifier.modifier import (
    find_and_modify_sap_files,
    is_recently_modified,
    modify_sap_file,
)


@pytest.fixture
def temp_sap_file(tmp_path):
    """Create a temporary SAP file for testing"""
    sap_content = """[System]
Name=DEV
Client=100
GuiParm=/M//H/sapserver.example.com/S/3200/M/sapapp.example.com/S/3600/G/PUBLIC
[User]
Name=TESTUSER
Language=EN
[Function]
Command=SMEN
Type=Transaction
"""
    file_path = tmp_path / "test.sap"
    file_path.write_text(sap_content)
    return file_path


@pytest.fixture
def temp_sap_file_no_m(tmp_path):
    """Create a SAP file without /M/ to remove"""
    sap_content = """[System]
Name=TEST
GuiParm=/H/example.com/S/3200
[User]
Name=USER
"""
    file_path = tmp_path / "test_no_m.sap"
    file_path.write_text(sap_content)
    return file_path


@pytest.fixture
def temp_sap_file_multiple_m(tmp_path):
    """Create a SAP file with multiple /M/ occurrences"""
    sap_content = """[System]
GuiParm=/M//M//H/example.com/S/3200
"""
    file_path = tmp_path / "test_multiple.sap"
    file_path.write_text(sap_content)
    return file_path


class TestModifySapFile:
    """Tests for modify_sap_file function"""

    def test_modify_removes_first_m(self, temp_sap_file):
        """Test that /M/ is removed from GuiParm line"""
        assert modify_sap_file(temp_sap_file)

        content = temp_sap_file.read_text()
        assert "GuiParm=/H/sapserver.example.com" in content
        assert "GuiParm=/M//" not in content

    def test_modify_with_backup(self, temp_sap_file):
        """Test that backup is created when requested"""
        assert modify_sap_file(temp_sap_file, backup=True)

        backup_path = temp_sap_file.with_suffix(".sap.bak")
        assert backup_path.exists()

        # Original content should be in backup
        backup_content = backup_path.read_text()
        assert "GuiParm=/M//" in backup_content

    def test_no_modification_needed(self, temp_sap_file_no_m):
        """Test file without /M/ returns False"""
        assert not modify_sap_file(temp_sap_file_no_m)

        content = temp_sap_file_no_m.read_text()
        assert "GuiParm=/H/example.com" in content

    def test_only_first_m_removed(self, temp_sap_file_multiple_m):
        """Test that only first /M/ is removed"""
        assert modify_sap_file(temp_sap_file_multiple_m)

        content = temp_sap_file_multiple_m.read_text()
        # After removing first /M/, should have /M//H/
        assert "GuiParm=/M//H/example.com" in content
        # Should not have /M//M//
        assert "GuiParm=/M//M//" not in content

    def test_nonexistent_file(self, tmp_path):
        """Test handling of nonexistent file"""
        fake_path = tmp_path / "nonexistent.sap"
        assert not modify_sap_file(fake_path)

    def test_non_sap_file(self, tmp_path):
        """Test handling of non-.sap file"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("GuiParm=/M//H/test")
        assert not modify_sap_file(txt_file)


class TestIsRecentlyModified:
    """Tests for is_recently_modified function"""

    def test_newly_created_file(self, temp_sap_file):
        """Test that newly created file is considered recent"""
        assert is_recently_modified(temp_sap_file, seconds=10)

    def test_old_file(self, tmp_path):
        """Test that we can check if file is not recent"""
        # We can't easily test old files without mocking time,
        # but we can test with very short time window
        old_file = tmp_path / "old.sap"
        old_file.write_text("test")

        # Wait a tiny bit and check with 0 second window
        import time

        time.sleep(0.001)
        assert not is_recently_modified(old_file, seconds=0)

    def test_nonexistent_file(self, tmp_path):
        """Test handling of nonexistent file"""
        fake_path = tmp_path / "nonexistent.sap"
        assert not is_recently_modified(fake_path)


class TestFindAndModifySapFiles:
    """Tests for find_and_modify_sap_files function"""

    def test_modify_multiple_files(self, tmp_path):
        """Test modifying multiple SAP files"""
        # Create multiple SAP files
        for i in range(3):
            file_path = tmp_path / f"test{i}.sap"
            file_path.write_text(f"[System]\nGuiParm=/M//H/server{i}.com")

        count = find_and_modify_sap_files(tmp_path, recent_only=False)
        assert count == 3

        # Verify all were modified
        for i in range(3):
            file_path = tmp_path / f"test{i}.sap"
            content = file_path.read_text()
            assert "GuiParm=/H/" in content

    def test_recent_only_filter(self, tmp_path):
        """Test that recent_only filter works"""
        # Create a file
        file_path = tmp_path / "test.sap"
        file_path.write_text("[System]\nGuiParm=/M//H/test.com")

        # With recent_only=True, should find it
        count = find_and_modify_sap_files(tmp_path, recent_only=True)
        assert count == 1

    def test_with_backup(self, tmp_path):
        """Test that backup option works for all files"""
        # Create SAP file
        file_path = tmp_path / "test.sap"
        file_path.write_text("[System]\nGuiParm=/M//H/test.com")

        count = find_and_modify_sap_files(tmp_path, recent_only=False, backup=True)
        assert count == 1

        # Check backup exists
        backup_path = file_path.with_suffix(".sap.bak")
        assert backup_path.exists()

    def test_nonexistent_directory(self, tmp_path):
        """Test handling of nonexistent directory"""
        fake_dir = tmp_path / "nonexistent"
        count = find_and_modify_sap_files(fake_dir)
        assert count == 0

    def test_no_sap_files(self, tmp_path):
        """Test directory with no SAP files"""
        # Create some non-SAP files
        (tmp_path / "test.txt").write_text("test")
        (tmp_path / "test.py").write_text("test")

        count = find_and_modify_sap_files(tmp_path)
        assert count == 0


class TestIntegration:
    """Integration tests"""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: create, modify, verify"""
        # Create original file
        original_content = """[System]
Name=DEV
Client=100
GuiParm=/M//H/sapserver.example.com/S/3200/M/sapapp.example.com/S/3600/G/PUBLIC
[User]
Name=TESTUSER
Language=EN
"""
        file_path = tmp_path / "connection.sap"
        file_path.write_text(original_content)

        # Modify with backup
        success = modify_sap_file(file_path, backup=True)
        assert success

        # Verify modification
        modified_content = file_path.read_text()
        assert (
            "GuiParm=/H/sapserver.example.com/S/3200/M/sapapp.example.com/S/3600/G/PUBLIC"
            in modified_content
        )

        # Verify backup has original
        backup_path = file_path.with_suffix(".sap.bak")
        backup_content = backup_path.read_text()
        assert "GuiParm=/M//H/sapserver.example.com" in backup_content

        # Verify other content unchanged
        assert "Name=DEV" in modified_content
        assert "Client=100" in modified_content
        assert "Name=TESTUSER" in modified_content
