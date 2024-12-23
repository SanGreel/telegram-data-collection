import pytest
from unittest.mock import AsyncMock

from telegram_data_downloader.utils import async_retry


class CustomException(Exception):
    pass


@pytest.mark.asyncio
async def test_async_retry_success_on_first_try():
    mock_func = AsyncMock(return_value="success")
    decorated_func = async_retry(CustomException)(mock_func)

    result = await decorated_func()
    assert result == "success"
    assert mock_func.await_count == 1


@pytest.mark.asyncio
async def test_async_retry_success_on_retry():
    mock_func = AsyncMock(side_effect=[CustomException("fail"), "success"])
    decorated_func = async_retry(CustomException, base_sleep_time=0.1, max_tries=3)(
        mock_func
    )

    result = await decorated_func()
    assert result == "success"
    assert mock_func.await_count == 2


@pytest.mark.asyncio
async def test_async_retry_failure_after_max_tries():
    mock_func = AsyncMock(side_effect=CustomException("fail"))
    decorated_func = async_retry(CustomException, base_sleep_time=0.1, max_tries=3)(
        mock_func
    )

    with pytest.raises(CustomException):
        await decorated_func()
    assert mock_func.await_count == 3


@pytest.mark.asyncio
async def test_async_retry_with_multiple_exceptions():
    mock_func = AsyncMock(
        side_effect=[CustomException("fail1"), CustomException("fail2"), "success"]
    )
    decorated_func = async_retry(CustomException, base_sleep_time=0.1, max_tries=5)(
        mock_func
    )

    result = await decorated_func()
    assert result == "success"
    assert mock_func.await_count == 3


@pytest.mark.asyncio
async def test_async_retry_with_unexpected_exception():
    mock_func = AsyncMock(side_effect=ValueError("unexpected"))
    decorated_func = async_retry(CustomException, base_sleep_time=0.1, max_tries=3)(
        mock_func
    )

    with pytest.raises(ValueError):
        await decorated_func()
    assert mock_func.await_count == 1  # Should not retry on unexpected exception
