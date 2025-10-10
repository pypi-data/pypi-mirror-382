# dbbasic-sessions

Stateless session management using signed cookies for Python web applications.

## Philosophy

> "Compute, don't store. Verify, don't persist."

Sessions are temporary authentication state. Following Unix and CGI principles: **don't store temporary state, compute it.**

## Features

- **Stateless**: No server storage for sessions
- **Simple**: 15 lines of core code
- **Fast**: Pure computation, no I/O
- **Secure**: HMAC-SHA256 signed tokens
- **CGI-Perfect**: Each request independent, no shared state
- **Zero Dependencies**: Python stdlib only

## Installation

```bash
pip install dbbasic-sessions
```

## Quick Start

```python
from dbbasic_sessions import create_session, get_session, destroy_session

# Login - create session
token = create_session(user_id=42)
response.set_cookie('session', token, httponly=True, secure=True)

# Verify session
user_id = get_session(request.cookies.get('session'))
if user_id:
    user = User.get(user_id)  # Get from database
    return render('dashboard', user=user)

# Logout
destroy_session(token)  # No-op server-side
response.delete_cookie('session')
```

## API

### `create_session(user_id, ttl=2592000)`

Create a signed session token.

- **user_id**: User identifier (str or int)
- **ttl**: Time-to-live in seconds (default: 30 days)
- **Returns**: Signed token string

### `get_session(token)`

Verify token and extract user ID.

- **token**: Session token from cookie
- **Returns**: User ID string, or None if invalid/expired

### `destroy_session(token)`

Logout (no-op server-side, client deletes cookie).

- **token**: Session token (unused)
- **Returns**: None

## Configuration

Set a secret key in your environment:

```bash
export SECRET_KEY="your-secret-key-here"
```

Generate a secure secret key:

```python
import secrets
print(secrets.token_hex(32))
```

## Security

- Uses HMAC-SHA256 for cryptographic signing
- Timing-safe signature comparison
- Supports HTTPS-only, HttpOnly, and SameSite cookie flags
- Short TTL recommended (1-30 days)

## Performance

- **Create session**: 0.01ms
- **Verify session**: 0.01ms
- **Memory usage**: 0 bytes (no server storage)
- **Scales**: Infinitely (stateless)

## Why Signed Cookies?

- **Unix philosophy**: Don't store temporary state
- **CGI philosophy**: Stateless processes
- **Industry standard**: Flask, Rails default
- **Simple**: 15 lines vs 20-30 with storage
- **Fast**: No I/O, pure computation
- **Scales**: Infinite horizontal scaling

## License

MIT License
