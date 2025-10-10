"""
dbbasic-sessions: Stateless session management using signed cookies

Philosophy: "Compute, don't store. Verify, don't persist."

Example:
    from dbbasic_sessions import create_session, get_session, destroy_session

    # Create session
    token = create_session(user_id=42)

    # Verify session
    user_id = get_session(token)

    # Logout
    destroy_session(token)
"""

import hmac
import hashlib
import json
import base64
import os
import time

__version__ = "3.0.0"
__all__ = ["create_session", "get_session", "destroy_session"]

SECRET = os.getenv('SECRET_KEY', 'CHANGE-ME-IN-PRODUCTION')


def create_session(user_id, ttl=2592000):
    """Create signed session token

    Args:
        user_id: User identifier (str or int)
        ttl: Time-to-live in seconds (default: 30 days = 2592000)

    Returns:
        str: Signed session token in format "payload.signature"

    Example:
        >>> token = create_session(user_id=42)
        >>> token = create_session(user_id="alice", ttl=3600)  # 1 hour
    """
    data = {'user_id': str(user_id), 'expires': int(time.time()) + ttl}
    payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    signature = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def get_session(token):
    """Verify and extract user_id from token

    Args:
        token: Session token from cookie

    Returns:
        str: User ID if valid, None if invalid/expired

    Example:
        >>> user_id = get_session(request.cookies.get('session'))
        >>> if user_id:
        ...     user = User.get(user_id)
    """
    if not token:
        return None

    try:
        payload, signature = token.split('.')
        expected_sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()

        # Timing-safe comparison
        if not hmac.compare_digest(signature, expected_sig):
            return None

        data = json.loads(base64.urlsafe_b64decode(payload))

        # Check expiration
        if data['expires'] <= time.time():
            return None

        return data['user_id']
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def destroy_session(token):
    """Logout (no-op server-side, client deletes cookie)

    Args:
        token: Session token (unused)

    Returns:
        None

    Note:
        Token expires naturally. Client must delete cookie.
        No server-side action needed in stateless design.

    Example:
        >>> destroy_session(token)  # No-op
        >>> response.delete_cookie('session')
    """
    pass
