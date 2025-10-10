"""
Unit tests for dbbasic-sessions

Tests the core functionality of create_session, get_session, and destroy_session.
"""

import time
import os
import pytest
from dbbasic_sessions import create_session, get_session, destroy_session


class TestCreateSession:
    """Test create_session function"""

    def test_create_session_returns_token(self):
        """Should return a valid token string"""
        token = create_session('42')
        assert isinstance(token, str)
        assert len(token) > 50  # Base64 + signature
        assert '.' in token  # payload.signature format

    def test_create_session_with_string_user_id(self):
        """Should accept string user_id"""
        token = create_session('alice')
        assert token is not None
        user_id = get_session(token)
        assert user_id == 'alice'

    def test_create_session_with_int_user_id(self):
        """Should accept integer user_id and convert to string"""
        token = create_session(42)
        assert token is not None
        user_id = get_session(token)
        assert user_id == '42'

    def test_create_session_with_custom_ttl(self):
        """Should respect custom TTL"""
        token = create_session('42', ttl=1)
        user_id = get_session(token)
        assert user_id == '42'

        # Wait for expiration
        time.sleep(1.1)
        user_id = get_session(token)
        assert user_id is None

    def test_create_session_default_ttl(self):
        """Should create token with default 30-day TTL"""
        token = create_session('42')
        user_id = get_session(token)
        assert user_id == '42'

    def test_different_users_get_different_tokens(self):
        """Should generate different tokens for different users"""
        token1 = create_session('alice')
        token2 = create_session('bob')
        assert token1 != token2


class TestGetSession:
    """Test get_session function"""

    def test_get_session_valid_token(self):
        """Should return user_id for valid token"""
        token = create_session('42')
        user_id = get_session(token)
        assert user_id == '42'

    def test_get_session_expired_token(self):
        """Should return None for expired token"""
        token = create_session('42', ttl=-1)  # Already expired
        time.sleep(0.1)
        user_id = get_session(token)
        assert user_id is None

    def test_get_session_invalid_signature(self):
        """Should return None for tampered token"""
        token = create_session('42')
        payload, sig = token.split('.')

        # Tamper with signature
        tampered = f"{payload}.{'0' * 64}"
        user_id = get_session(tampered)
        assert user_id is None

    def test_get_session_invalid_token_format(self):
        """Should return None for malformed token"""
        user_id = get_session('not-a-valid-token')
        assert user_id is None

    def test_get_session_empty_token(self):
        """Should return None for empty token"""
        user_id = get_session('')
        assert user_id is None

    def test_get_session_none_token(self):
        """Should return None for None token"""
        user_id = get_session(None)
        assert user_id is None

    def test_get_session_token_with_no_dot(self):
        """Should return None for token without dot separator"""
        user_id = get_session('invaliddddddddddddddddddddddddddddddddddddddddtoken')
        assert user_id is None

    def test_get_session_token_with_invalid_base64(self):
        """Should return None for token with invalid base64 payload"""
        user_id = get_session('!!!invalid!!!.a3f8d9e2b1c4567890abcdef')
        assert user_id is None


class TestDestroySession:
    """Test destroy_session function"""

    def test_destroy_session_is_noop(self):
        """Should be a no-op (returns None)"""
        token = create_session('42')
        result = destroy_session(token)
        assert result is None

    def test_token_still_valid_after_destroy(self):
        """Token should still be valid after destroy (client must delete cookie)"""
        token = create_session('42')
        destroy_session(token)

        # Token still verifies (server-side is stateless)
        user_id = get_session(token)
        assert user_id == '42'


class TestConcurrentSessions:
    """Test handling multiple concurrent sessions"""

    def test_multiple_sessions_independent(self):
        """Should handle multiple sessions independently"""
        tokens = [create_session(str(i)) for i in range(100)]

        # All should verify correctly
        for i, token in enumerate(tokens):
            user_id = get_session(token)
            assert user_id == str(i)

    def test_session_isolation(self):
        """Sessions should not interfere with each other"""
        token1 = create_session('alice')
        token2 = create_session('bob')

        assert get_session(token1) == 'alice'
        assert get_session(token2) == 'bob'

        # Destroying one doesn't affect the other
        destroy_session(token1)
        assert get_session(token2) == 'bob'


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_session_with_zero_ttl(self):
        """Should handle zero TTL (expires immediately)"""
        token = create_session('42', ttl=0)
        time.sleep(0.01)
        user_id = get_session(token)
        assert user_id is None

    def test_session_with_very_long_ttl(self):
        """Should handle very long TTL"""
        token = create_session('42', ttl=31536000)  # 1 year
        user_id = get_session(token)
        assert user_id == '42'

    def test_session_with_special_characters(self):
        """Should handle user_id with special characters"""
        special_ids = ['user@example.com', 'user-123', 'user_456', 'user.789']

        for user_id in special_ids:
            token = create_session(user_id)
            retrieved_id = get_session(token)
            assert retrieved_id == user_id

    def test_session_with_unicode_user_id(self):
        """Should handle unicode user_id"""
        token = create_session('用户42')
        user_id = get_session(token)
        assert user_id == '用户42'
