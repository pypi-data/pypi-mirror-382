import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator

import pytest
import redis.asyncio as redis_asyncio
from pytest_mock import MockerFixture

from arate_limit import (
    AtomicInt,
    LeakyBucketRateLimiter,
    RedisSlidingWindowApiRateLimiter,
    RedisSlidingWindowRateLimiter,
    TokenBucketRateLimiter,
)


@pytest.fixture(scope="function")
async def redis_client() -> AsyncGenerator[redis_asyncio.Redis]:
    async with redis_asyncio.Redis(host="localhost", port=6379) as client:
        yield client


async def test_atomic_int_init() -> None:
    value_default = AtomicInt()
    assert await value_default.get_value() == 0

    value = AtomicInt(10)
    assert await value.get_value() == 10


async def test_atomic_int() -> None:
    value = AtomicInt()
    assert await value.inc() == 1
    assert await value.dec() == 0
    assert await value.inc(10) == 10
    assert await value.dec(5) == 5
    assert await value.get_value() == 5
    await value.set_value(12)
    assert await value.get_value() == 12
    assert await value.compare_and_swap(12, 10)
    assert not await value.compare_and_swap(12, 10)


async def test_leaky_bucket_rate_limiter_init() -> None:
    rate_limiter = LeakyBucketRateLimiter(15, time_window=2.0, slack=10)

    assert rate_limiter._max_slack == 1333333330
    assert rate_limiter._per_request == 133333333
    assert await rate_limiter._state.get_value() == 0


async def test_leaky_bucket_rate_limiter(mocker: MockerFixture) -> None:
    call_counter = mocker.AsyncMock()
    rate_limiter = LeakyBucketRateLimiter(20)

    async def _call() -> None:
        await rate_limiter.wait()
        await call_counter()

    start = datetime.now()
    await asyncio.gather(*(_call() for _ in range(100)))
    end = datetime.now()

    assert (end - start).total_seconds() == pytest.approx(5.0, 0.2)
    assert call_counter.await_count == 100


def test_token_bucket_rate_limiter_init() -> None:
    rate_limiter = TokenBucketRateLimiter(100, time_window=2.0, burst=10)
    assert rate_limiter._limit == pytest.approx(50.0, 0.1)
    assert rate_limiter._burst == 10
    assert rate_limiter._tokens == pytest.approx(10, 0.1)


async def test_token_bucket_rate_limiter(mocker: MockerFixture) -> None:
    call_counter = mocker.AsyncMock()
    rate_limiter = TokenBucketRateLimiter(20, burst=20)

    async def _call() -> None:
        await rate_limiter.wait()
        await call_counter()

    start = datetime.now()
    await asyncio.gather(*(_call() for _ in range(100)))
    end = datetime.now()

    assert (end - start).total_seconds() == pytest.approx(5.0, 0.2)
    assert call_counter.await_count == 100


async def test_redis_sliding_window_rate_limiter_init(redis_client: redis_asyncio.Redis) -> None:
    rate_limiter = RedisSlidingWindowRateLimiter(redis=redis_client, event_count=100, time_window=10.1, slack=100)

    assert rate_limiter._event_count == 100
    assert rate_limiter._time_window == 10
    assert rate_limiter._max_slack == 100
    assert rate_limiter._key_prefix == "rate_limiter:"


async def test_redis_sliding_window_rate_limiter(mocker: MockerFixture, redis_client: redis_asyncio.Redis) -> None:
    call_counter = mocker.AsyncMock()
    rate_limiter = RedisSlidingWindowRateLimiter(
        redis=redis_client, event_count=20, slack=0, key_prefix=str(uuid.uuid4())
    )

    async def _call() -> None:
        await rate_limiter.wait()
        await call_counter()

    start = datetime.now()
    await asyncio.gather(*(_call() for _ in range(100)))
    end = datetime.now()

    assert (end - start).total_seconds() == pytest.approx(5.0, 0.5)
    assert call_counter.await_count == 100


async def test_redis_sliding_window_api_rate_limiter(redis_client: redis_asyncio.Redis) -> None:
    event_count = 10
    user_id = str(uuid.uuid4())
    api_rate_limiter = RedisSlidingWindowApiRateLimiter(
        redis=redis_client, event_count=event_count, time_window=10.0, key_prefix=str(uuid.uuid4())
    )

    for _ in range(event_count):
        within_limit, time_remaining = await api_rate_limiter.check(user_id)
        assert within_limit
        assert isinstance(time_remaining, int)
        assert time_remaining == 0

    await asyncio.sleep(2.2)

    within_limit, time_remaining = await api_rate_limiter.check(user_id)
    assert not within_limit
    assert isinstance(time_remaining, int)
    assert 0 < time_remaining < 10
