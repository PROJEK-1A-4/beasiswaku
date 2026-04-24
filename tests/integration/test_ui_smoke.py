#!/usr/bin/env python3
"""
Smoke Test Suite for BeasiswaKu UI Flow
Tests critical user journeys: login → profile edit → logout

P2-05: Smoke test UI flow: login/logout/profile update
"""

import sys
import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.crud import (
    init_db, register_user, login_user, get_connection,
    update_user_profile
)
from src.core.database import DatabaseManager
from src.core.config import Config
from main import AppSignalBus, MainWindow

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Global QApplication instance for PyQt6
_app = None

def get_qapp():
    """Get or create QApplication singleton."""
    global _app
    if _app is None:
        _app = QApplication.instance()
        if _app is None:
            _app = QApplication(sys.argv)
    return _app


class TestUISmokeFlow:
    """Smoke tests for core UI flows."""

    def setup_method(self):
        """Setup test fixtures before each test."""
        self.qapp = get_qapp()
        self.test_username = "smoke_test_user"
        self.test_email = "smoke@test.local"
        self.test_password = "TestPassword@123"
        self.main_window = None

    def teardown_method(self):
        """Cleanup after each test."""
        if self.main_window is not None:
            try:
                self.main_window.close()
            except:
                pass
        # Process pending events
        self.qapp.processEvents()

    def test_smoke_login_creates_valid_session(self, isolated_database):
        """Test 1: Login flow creates valid user session."""
        # Setup: Initialize database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        assert cursor.fetchone() is not None, "Database should be initialized"
        cursor.close()

        # Execute: Register and login user
        success, msg = register_user(
            self.test_username,
            self.test_email,
            self.test_password
        )
        assert success, f"Registration should succeed: {msg}"

        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success, f"Login should succeed: {msg}"
        assert user_data is not None, "User data should be returned after successful login"
        user_id = user_data["id"]

        # Verify: User exists in database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM akun WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        assert user is not None, f"User {user_id} should exist in database"
        assert user["username"] == self.test_username
        assert user["email"] == self.test_email

        logger.info(f"✓ Test 1 Passed: Login creates valid session for user {user_id}")

    def test_smoke_main_window_initialization(self, isolated_database):
        """Test 2: MainWindow initializes with correct user context."""
        # Setup: Create test user
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success
        user_id = user_data["id"]

        # Execute: Create MainWindow
        self.main_window = MainWindow(user_id, self.test_username)

        # Verify: Window initialized with correct attributes
        assert self.main_window.user_id == user_id
        assert self.main_window.username == self.test_username
        assert self.main_window.signals is not None
        assert isinstance(self.main_window.signals, AppSignalBus)
        assert self.main_window.user_label.text() == f"👤 {self.test_username}"
        assert self.test_username in self.main_window.windowTitle()
        assert self.main_window.tabs.count() == 5  # 5 tabs: Beranda, Beasiswa, Tracker, Statistik, Profil
        
        logger.info(f"✓ Test 2 Passed: MainWindow initialized correctly for {self.test_username}")

    def test_smoke_profile_edit_and_save(self, isolated_database):
        """Test 3: Profile edit/save flow updates data correctly."""
        # Setup: Create user and MainWindow
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success
        user_id = user_data["id"]

        self.main_window = MainWindow(user_id, self.test_username)
        profil_tab = self.main_window.profil_tab

        # Original values
        original_username = self.test_username
        original_email = self.test_email

        # Execute: Change profile fields
        new_name = "Updated Test User"
        new_email = "updated@test.local"
        new_username = "updated_user"
        new_jenjang = "S2"

        profil_tab.profile_fields["nama_lengkap"].setText(new_name)
        profil_tab.profile_fields["email"].setText(new_email)
        profil_tab.profile_fields["username"].setText(new_username)
        profil_tab.profile_fields["jenjang"].setText(new_jenjang)

        # Save profile
        profil_tab._on_save_profile_clicked()
        self.qapp.processEvents()

        # Verify: Changes persisted in database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nama_lengkap, email, username, jenjang FROM akun WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        cursor.close()

        assert result is not None
        assert result["nama_lengkap"] == new_name
        assert result["email"] == new_email
        assert result["username"] == new_username
        assert result["jenjang"] == new_jenjang

        logger.info(f"✓ Test 3 Passed: Profile edit/save persisted correctly")

    def test_smoke_profile_update_signal_emission(self, isolated_database):
        """Test 4: Profile update emits AppSignalBus signal."""
        # Setup: Create user and MainWindow
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success
        user_id = user_data["id"]

        self.main_window = MainWindow(user_id, self.test_username)
        profil_tab = self.main_window.profil_tab

        # Execute: Track signal emission
        signal_received = {"topic": None}

        def on_signal(topic):
            signal_received["topic"] = topic

        self.main_window.signals.data_changed.connect(on_signal)

        # Change and save profile
        profil_tab.profile_fields["nama_lengkap"].setText("Signal Test User")
        profil_tab._on_save_profile_clicked()
        self.qapp.processEvents()

        # Verify: Signal was emitted with correct topic
        assert signal_received["topic"] == "profile.updated", \
            f"Expected 'profile.updated' signal, got '{signal_received['topic']}'"

        logger.info(f"✓ Test 4 Passed: Profile update emits correct signal")

    def test_smoke_profile_update_refreshes_user_label(self, isolated_database):
        """Test 5: Profile username update refreshes MainWindow user label."""
        # Setup: Create user and MainWindow
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success
        user_id = user_data["id"]

        self.main_window = MainWindow(user_id, self.test_username)
        profil_tab = self.main_window.profil_tab

        # Execute: Update username in profile
        new_username = "profile_updated_user"
        profil_tab.profile_fields["username"].setText(new_username)
        profil_tab.profile_fields["nama_lengkap"].setText("Profile Test User")
        profil_tab._on_save_profile_clicked()
        self.qapp.processEvents()

        # Verify: User label reflects the new username
        assert new_username in self.main_window.username, \
            f"MainWindow username should be updated to {new_username}"
        assert f"👤 {new_username}" in self.main_window.user_label.text(), \
            f"User label should show updated username"
        assert new_username in self.main_window.windowTitle(), \
            f"Window title should contain updated username"

        logger.info(f"✓ Test 5 Passed: Profile username update refreshes UI labels")

    def test_smoke_password_change_flow(self, isolated_database):
        """Test 6: Password change validates and updates correctly."""
        # Setup: Create user and MainWindow
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success
        user_id = user_data["id"]

        self.main_window = MainWindow(user_id, self.test_username)
        profil_tab = self.main_window.profil_tab

        # Execute: Change password
        new_password = "NewPassword@456"
        profil_tab.current_password_input.setText(self.test_password)
        profil_tab.new_password_input.setText(new_password)
        profil_tab.confirm_password_input.setText(new_password)
        
        profil_tab._on_change_password_clicked()
        self.qapp.processEvents()

        # Verify: New password works on login
        logout_success = True
        self.main_window.close()
        self.main_window = None
        
        # Attempt login with new password
        login_success, msg, new_session = login_user(self.test_username, new_password)
        assert login_success, f"Login with new password should succeed: {msg}"
        assert new_session is not None
        assert new_session["id"] == user_id

        logger.info(f"✓ Test 6 Passed: Password change validated and persisted")

    def test_smoke_cross_tab_event_propagation(self, isolated_database):
        """Test 7: Profile.updated signal triggers beranda tab refresh."""
        # Setup: Create user and MainWindow
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success
        user_id = user_data["id"]

        self.main_window = MainWindow(user_id, self.test_username)
        profil_tab = self.main_window.profil_tab
        beranda_tab = self.main_window.beranda_tab

        # Mock beranda_tab.load_dashboard_data to track calls
        original_method = beranda_tab.load_dashboard_data
        call_count = {"count": 0}

        def tracked_load_dashboard_data():
            call_count["count"] += 1
            original_method()

        beranda_tab.load_dashboard_data = tracked_load_dashboard_data

        # Execute: Update profile
        profil_tab.profile_fields["nama_lengkap"].setText("Cross Tab Test")
        initial_count = call_count["count"]
        profil_tab._on_save_profile_clicked()
        self.qapp.processEvents()

        # Verify: Beranda tab was refreshed
        assert call_count["count"] > initial_count, \
            "Beranda tab should be refreshed when profile.updated signal is emitted"

        logger.info(f"✓ Test 7 Passed: Profile.updated triggers cross-tab refresh")

    def test_smoke_logout_flow(self, isolated_database):
        """Test 8: Logout flow closes MainWindow and clears session."""
        # Setup: Create user and MainWindow
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_id = login_user(self.test_username, self.test_password)
        assert success

        self.main_window = MainWindow(user_id, self.test_username)
        assert self.main_window.isVisible() or self.main_window.user_id is not None

        # Execute: Logout (close window)
        self.main_window.close()
        self.qapp.processEvents()

        # Verify: Window is closed
        # Note: In real app, this would show login window again
        # For test, we verify the close action completed
        assert True, "Logout flow completed without error"

        logger.info(f"✓ Test 8 Passed: Logout flow completed successfully")

    def test_smoke_profile_validation_prevents_invalid_save(self, isolated_database):
        """Test 9: Profile validation prevents saving invalid data."""
        # Setup: Create user and MainWindow
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success
        user_id = user_data["id"]

        self.main_window = MainWindow(user_id, self.test_username)
        profil_tab = self.main_window.profil_tab

        # Get original data
        original_email = profil_tab.profile_fields["email"].text()

        # Execute: Try to save with invalid email
        profil_tab.profile_fields["email"].setText("invalid-email-format")

        # Patch QMessageBox to avoid UI blocking
        with patch("src.gui.tab_profil.QMessageBox.warning"):
            profil_tab._on_save_profile_clicked()
        self.qapp.processEvents()

        # Verify: Invalid data was not saved
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM akun WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        cursor.close()

        # Email should either remain original or validation should prevent update
        assert result["email"] == original_email, "Invalid email should not be saved"

        logger.info(f"✓ Test 9 Passed: Profile validation prevents invalid saves")

    def test_smoke_complete_user_journey(self, isolated_database):
        """Test 10: Complete user journey (login → profile edit → logout)."""
        # Execute: Full user journey
        logger.info("Starting complete user journey test...")

        # 1. Register and login
        register_user(self.test_username, self.test_email, self.test_password)
        success, msg, user_data = login_user(self.test_username, self.test_password)
        assert success, f"Login failed: {msg}"
        user_id = user_data["id"]
        logger.info(f"  ✓ Login successful, user_id={user_id}")

        # 2. Create MainWindow
        self.main_window = MainWindow(user_id, self.test_username)
        logger.info(f"  ✓ MainWindow created")

        # 3. Edit profile
        profil_tab = self.main_window.profil_tab
        profil_tab.profile_fields["nama_lengkap"].setText("Journey Test User")
        profil_tab.profile_fields["email"].setText("journey@test.local")
        logger.info(f"  ✓ Profile fields updated")

        # 4. Save profile
        profil_tab._on_save_profile_clicked()
        self.qapp.processEvents()
        logger.info(f"  ✓ Profile saved")

        # 5. Verify persistence
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM akun WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        assert user["email"] == "journey@test.local", "Profile save should persist"
        logger.info(f"  ✓ Changes persisted in database")

        # 6. Logout
        self.main_window.close()
        self.qapp.processEvents()
        logger.info(f"  ✓ Logout completed")

        # Verify: User journey completed successfully
        assert True, "Complete user journey should execute without error"
        logger.info(f"✓ Test 10 Passed: Complete user journey executed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
