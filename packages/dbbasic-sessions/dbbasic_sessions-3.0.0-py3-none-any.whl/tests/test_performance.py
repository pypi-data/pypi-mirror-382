"""
Performance tests for dbbasic-sessions

Tests that the implementation meets performance requirements:
- Create session: < 0.1ms per operation
- Verify session: < 0.1ms per operation
- Handles 10,000+ operations within reasonable time
"""

import time
import pytest
from dbbasic_sessions import create_session, get_session


class TestPerformance:
    """Test performance characteristics"""

    def test_create_session_performance(self):
        """Should create 10K sessions in < 1 second"""
        start = time.time()
        tokens = [create_session(str(i)) for i in range(10000)]
        elapsed = time.time() - start

        print(f"\nCreated 10,000 sessions in {elapsed:.3f}s")
        print(f"Average: {elapsed/10000*1000:.3f}ms per session")

        assert len(tokens) == 10000
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s for 10K sessions"

    def test_get_session_performance(self):
        """Should verify 10K sessions in < 1 second"""
        # Create tokens first
        tokens = [create_session(str(i)) for i in range(10000)]

        # Measure verification
        start = time.time()
        for token in tokens:
            get_session(token)
        elapsed = time.time() - start

        print(f"\nVerified 10,000 sessions in {elapsed:.3f}s")
        print(f"Average: {elapsed/10000*1000:.3f}ms per verification")

        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s for 10K verifications"

    def test_single_operation_performance(self):
        """Should perform single operations very quickly"""
        # Warm up
        for _ in range(100):
            token = create_session('42')
            get_session(token)

        # Measure create
        start = time.perf_counter()
        token = create_session('42')
        create_time = time.perf_counter() - start

        # Measure verify
        start = time.perf_counter()
        get_session(token)
        verify_time = time.perf_counter() - start

        print(f"\nSingle operation times:")
        print(f"Create: {create_time*1000:.3f}ms")
        print(f"Verify: {verify_time*1000:.3f}ms")

        # Should be very fast (< 1ms each)
        assert create_time < 0.001, f"Create too slow: {create_time*1000:.3f}ms"
        assert verify_time < 0.001, f"Verify too slow: {verify_time*1000:.3f}ms"

    def test_concurrent_session_performance(self):
        """Should handle many concurrent sessions efficiently"""
        num_sessions = 1000

        start = time.time()
        tokens = {str(i): create_session(str(i)) for i in range(num_sessions)}
        create_time = time.time() - start

        start = time.time()
        for user_id, token in tokens.items():
            verified_id = get_session(token)
            assert verified_id == user_id
        verify_time = time.time() - start

        print(f"\nConcurrent {num_sessions} sessions:")
        print(f"Create all: {create_time:.3f}s")
        print(f"Verify all: {verify_time:.3f}s")
        print(f"Total: {create_time + verify_time:.3f}s")

        assert create_time < 0.2, f"Create too slow: {create_time:.3f}s"
        assert verify_time < 0.2, f"Verify too slow: {verify_time:.3f}s"

    def test_memory_efficiency(self):
        """Should use minimal memory (no server storage)"""
        import sys

        # Create many sessions
        tokens = [create_session(str(i)) for i in range(10000)]

        # Tokens are just strings, no server-side storage
        # Memory usage should be minimal (just the token strings in the list)
        token_memory = sum(sys.getsizeof(token) for token in tokens)

        print(f"\nMemory for 10K tokens: {token_memory / 1024:.2f} KB")
        print(f"Average per token: {token_memory / 10000:.0f} bytes")

        # Should be reasonable (< 2MB for 10K tokens)
        # Note: sys.getsizeof includes Python object overhead
        assert token_memory < 2 * 1024 * 1024, f"Memory usage too high: {token_memory / 1024:.2f} KB"

    def test_scaling_characteristics(self):
        """Should scale linearly (O(n))"""
        sizes = [100, 500, 1000, 5000, 10000]
        times = []

        for size in sizes:
            start = time.time()
            tokens = [create_session(str(i)) for i in range(size)]
            for token in tokens:
                get_session(token)
            elapsed = time.time() - start
            times.append(elapsed)

            print(f"\n{size:5d} sessions: {elapsed:.3f}s ({elapsed/size*1000:.3f}ms avg)")

        # Time should scale roughly linearly
        # Check that 10x size doesn't take more than 15x time
        # (allowing some overhead)
        ratio_100_to_1000 = times[2] / times[0]
        ratio_1000_to_10000 = times[4] / times[2]

        print(f"\nScaling ratios:")
        print(f"100 -> 1000 (10x): {ratio_100_to_1000:.2f}x time")
        print(f"1000 -> 10000 (10x): {ratio_1000_to_10000:.2f}x time")

        assert ratio_100_to_1000 < 15, "Scaling worse than linear (100->1000)"
        assert ratio_1000_to_10000 < 15, "Scaling worse than linear (1000->10000)"

    def test_invalid_token_performance(self):
        """Should handle invalid tokens quickly (fail fast)"""
        invalid_tokens = [
            'invalid-token',
            'not.a.real.token',
            '',
            'a' * 1000,  # Very long invalid token
        ]

        start = time.time()
        for _ in range(1000):
            for token in invalid_tokens:
                get_session(token)
        elapsed = time.time() - start

        print(f"\nVerified 4000 invalid tokens in {elapsed:.3f}s")
        print(f"Average: {elapsed/4000*1000:.3f}ms per check")

        # Should fail fast
        assert elapsed < 0.5, f"Invalid token checks too slow: {elapsed:.3f}s"
