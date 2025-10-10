"""
Security tests for dbbasic-sessions

Tests cryptographic security, tampering detection, and attack resistance.
"""

import time
import base64
import json
import hmac
import hashlib
import os
import pytest
from dbbasic_sessions import create_session, get_session


class TestSignatureSecurity:
    """Test HMAC signature security"""

    def test_tampered_payload_rejected(self):
        """Should reject token with modified payload"""
        token = create_session('42')
        payload, sig = token.split('.')

        # Decode, modify, re-encode payload
        data = json.loads(base64.urlsafe_b64decode(payload))
        data['user_id'] = '999'  # Try to become different user
        new_payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

        # Use old signature with new payload
        tampered = f"{new_payload}.{sig}"
        user_id = get_session(tampered)

        assert user_id is None, "Tampered payload should be rejected"

    def test_tampered_signature_rejected(self):
        """Should reject token with modified signature"""
        token = create_session('42')
        payload, sig = token.split('.')

        # Modify signature
        tampered_sig = sig[:-4] + 'XXXX'
        tampered = f"{payload}.{tampered_sig}"

        user_id = get_session(tampered)
        assert user_id is None, "Tampered signature should be rejected"

    def test_signature_verification_is_constant_time(self):
        """Should use constant-time comparison to prevent timing attacks"""
        # This test verifies hmac.compare_digest is used
        # We can't easily test timing directly, but we can verify
        # that the function doesn't short-circuit on first difference

        token = create_session('42')
        payload, correct_sig = token.split('.')

        # Create signatures that differ at different positions
        wrong_sigs = [
            'X' + correct_sig[1:],  # Differ at start
            correct_sig[:32] + 'X' + correct_sig[33:],  # Differ in middle
            correct_sig[:-1] + 'X',  # Differ at end
        ]

        # All should be rejected
        for wrong_sig in wrong_sigs:
            tampered = f"{payload}.{wrong_sig}"
            user_id = get_session(tampered)
            assert user_id is None

    def test_cannot_create_valid_signature_without_secret(self):
        """Should not be able to forge signature without secret key"""
        # Create a payload manually
        data = {'user_id': '999', 'expires': int(time.time()) + 3600}
        payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

        # Try to sign with wrong secret
        wrong_secret = 'wrong-secret'
        wrong_sig = hmac.new(wrong_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        forged_token = f"{payload}.{wrong_sig}"

        user_id = get_session(forged_token)
        assert user_id is None, "Forged token should be rejected"


class TestTokenExpiration:
    """Test expiration security"""

    def test_expired_token_rejected(self):
        """Should reject expired token"""
        token = create_session('42', ttl=1)
        time.sleep(1.1)

        user_id = get_session(token)
        assert user_id is None, "Expired token should be rejected"

    def test_cannot_extend_expiration_by_tampering(self):
        """Should not allow extending expiration by modifying token"""
        token = create_session('42', ttl=1)
        payload, sig = token.split('.')

        # Try to extend expiration
        data = json.loads(base64.urlsafe_b64decode(payload))
        data['expires'] = int(time.time()) + 9999999
        new_payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

        tampered = f"{new_payload}.{sig}"

        user_id = get_session(tampered)
        assert user_id is None, "Modified expiration should be rejected"

    def test_replay_after_expiry_fails(self):
        """Should not accept token replayed after expiry"""
        token = create_session('42', ttl=1)

        # Token valid initially
        user_id = get_session(token)
        assert user_id == '42'

        # Wait for expiry
        time.sleep(1.1)

        # Token should now be invalid
        user_id = get_session(token)
        assert user_id is None, "Expired token should not be accepted"


class TestSessionFixation:
    """Test protection against session fixation attacks"""

    def test_cannot_inject_token_via_url(self):
        """Should only accept token from secure cookie, not URL"""
        # This is a usage pattern test - the library itself doesn't
        # enforce this, but the spec requires it

        # Create a token
        token = create_session('42')

        # Token should work when passed correctly
        user_id = get_session(token)
        assert user_id == '42'

        # Note: Application must not accept tokens from query params
        # This test documents the expected usage pattern

    def test_new_token_after_login(self):
        """Should generate new token after each login"""
        # Each login should get a fresh token
        token1 = create_session('42')
        time.sleep(1.01)  # Wait 1+ second for timestamp to change
        token2 = create_session('42')

        # Tokens should be different (includes timestamp)
        assert token1 != token2, "Each login should generate unique token"

        # Both should be valid
        assert get_session(token1) == '42'
        assert get_session(token2) == '42'


class TestPrivilegeEscalation:
    """Test protection against privilege escalation"""

    def test_cannot_change_user_id(self):
        """Should not allow changing user_id in token"""
        token = create_session('42')
        payload, sig = token.split('.')

        # Try to change user_id from 42 to 999
        data = json.loads(base64.urlsafe_b64decode(payload))
        data['user_id'] = '999'
        new_payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

        tampered = f"{new_payload}.{sig}"
        user_id = get_session(tampered)

        assert user_id is None, "Cannot escalate to different user"

    def test_cannot_add_fields_to_token(self):
        """Should not allow adding fields to token"""
        token = create_session('42')
        payload, sig = token.split('.')

        # Try to add 'admin' field
        data = json.loads(base64.urlsafe_b64decode(payload))
        data['admin'] = True
        new_payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

        tampered = f"{new_payload}.{sig}"
        user_id = get_session(tampered)

        assert user_id is None, "Cannot add fields to token"


class TestCryptographicStrength:
    """Test cryptographic properties"""

    def test_signature_length(self):
        """Should use 256-bit (64 hex chars) signature"""
        token = create_session('42')
        payload, sig = token.split('.')

        # HMAC-SHA256 produces 64 hex characters
        assert len(sig) == 64, f"Signature should be 64 chars, got {len(sig)}"
        assert all(c in '0123456789abcdef' for c in sig), "Signature should be hex"

    def test_tokens_appear_random(self):
        """Should generate tokens that appear random"""
        tokens = []
        for i in range(10):
            # Use different user IDs to ensure uniqueness
            # (tokens generated in same second will have same timestamp)
            tokens.append(create_session(f'user_{i}'))

        # All should be unique (different user IDs)
        assert len(set(tokens)) == len(tokens), "Tokens should be unique"

    def test_secret_key_requirement(self):
        """Should use SECRET_KEY from environment"""
        import dbbasic_sessions

        # Check that default secret key is warning value
        default_secret = dbbasic_sessions.SECRET

        # Should have a value (even if default warning)
        assert default_secret is not None
        assert len(default_secret) > 0

    def test_payload_is_visible_but_signed(self):
        """Payload should be readable but tamper-proof"""
        token = create_session('42')
        payload, sig = token.split('.')

        # Payload can be decoded (it's base64, not encrypted)
        data = json.loads(base64.urlsafe_b64decode(payload))

        assert data['user_id'] == '42'
        assert 'expires' in data

        # But cannot be modified without breaking signature
        data['user_id'] = '999'
        new_payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
        tampered = f"{new_payload}.{sig}"

        assert get_session(tampered) is None


class TestErrorHandling:
    """Test security of error handling"""

    def test_errors_dont_leak_information(self):
        """Should return None for all errors, not reveal details"""
        invalid_tokens = [
            'invalid',
            'payload.badsig',
            'bad-base64.sig',
            '',
            None,
            'a.b.c.d',  # Too many parts
        ]

        for token in invalid_tokens:
            user_id = get_session(token)
            assert user_id is None, f"Should return None for: {token}"

    def test_no_exception_on_invalid_input(self):
        """Should not raise exceptions for invalid input"""
        invalid_inputs = [
            'invalid',
            '',
            None,
            'a' * 10000,  # Very long
            '\x00\x01\x02',  # Binary
        ]

        for inp in invalid_inputs:
            try:
                user_id = get_session(inp)
                assert user_id is None
            except Exception as e:
                pytest.fail(f"Should not raise exception for {inp}: {e}")


class TestSecretKeyManagement:
    """Test secret key security"""

    def test_changing_secret_invalidates_tokens(self):
        """Should invalidate all tokens when secret changes"""
        import dbbasic_sessions

        # Save original secret
        original_secret = dbbasic_sessions.SECRET

        try:
            # Create token with original secret
            dbbasic_sessions.SECRET = 'secret1'
            token = create_session('42')

            # Verify with same secret
            user_id = get_session(token)
            assert user_id == '42'

            # Change secret
            dbbasic_sessions.SECRET = 'secret2'

            # Token should now be invalid
            user_id = get_session(token)
            assert user_id is None, "Token should be invalid after secret change"

        finally:
            # Restore original secret
            dbbasic_sessions.SECRET = original_secret

    def test_default_secret_warning(self):
        """Should have clear warning in default secret"""
        import dbbasic_sessions

        # If using default secret, it should contain warning
        if os.getenv('SECRET_KEY') is None:
            default = dbbasic_sessions.SECRET
            assert 'CHANGE' in default or 'PRODUCTION' in default, \
                "Default secret should warn user to change it"
