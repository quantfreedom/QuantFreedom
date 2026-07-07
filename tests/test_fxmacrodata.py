import io
import json
import sys
import types
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest import mock

import numpy as np
import pytest


def load_fxmacrodata_module():
    root = Path(__file__).resolve().parents[1]
    previous_modules = {
        name: sys.modules.get(name)
        for name in (
            "quantfreedom",
            "quantfreedom.core",
            "quantfreedom.core.enums",
            "quantfreedom.helpers",
            "quantfreedom.helpers.fxmacrodata",
        )
    }

    try:
        sys.modules["quantfreedom"] = types.ModuleType("quantfreedom")
        sys.modules["quantfreedom.core"] = types.ModuleType("quantfreedom.core")
        sys.modules["quantfreedom.helpers"] = types.ModuleType("quantfreedom.helpers")

        enums_spec = spec_from_file_location(
            "quantfreedom.core.enums",
            root / "quantfreedom" / "core" / "enums.py",
        )
        enums_module = module_from_spec(enums_spec)
        sys.modules["quantfreedom.core.enums"] = enums_module
        enums_spec.loader.exec_module(enums_module)

        fx_spec = spec_from_file_location(
            "quantfreedom.helpers.fxmacrodata",
            root / "quantfreedom" / "helpers" / "fxmacrodata.py",
        )
        fx_module = module_from_spec(fx_spec)
        sys.modules["quantfreedom.helpers.fxmacrodata"] = fx_module
        fx_spec.loader.exec_module(fx_module)
        return fx_module
    finally:
        for name, module in previous_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def test_fxmacrodata_rows_to_footprint_candles_sorts_and_maps_ohlc():
    module = load_fxmacrodata_module()
    candles = module.fxmacrodata_rows_to_footprint_candles(
        [
            {"date": "2024-01-03", "value": "1.0920"},
            {"date": "2024-01-01", "rate": 1.1038},
            {"date": "2024-01-02", "close": 1.0943},
        ],
        duration_seconds=86_400,
    )

    expected_rates = np.array([1.1038, 1.0943, 1.0920])
    np.testing.assert_array_equal(
        candles.candle_open_timestamps,
        np.array([1704067200000, 1704153600000, 1704240000000], dtype=np.int64),
    )
    np.testing.assert_allclose(candles.candle_open_prices, expected_rates)
    np.testing.assert_allclose(candles.candle_high_prices, expected_rates)
    np.testing.assert_allclose(candles.candle_low_prices, expected_rates)
    np.testing.assert_allclose(candles.candle_close_prices, expected_rates)
    np.testing.assert_array_equal(candles.candle_asset_volumes, np.zeros(3))
    np.testing.assert_array_equal(candles.candle_usdt_volumes, np.zeros(3))
    np.testing.assert_array_equal(candles.candle_durations_seconds, np.full(3, 86_400))


def test_fxmacrodata_rows_to_footprint_candles_rejects_invalid_payloads():
    module = load_fxmacrodata_module()
    with pytest.raises(ValueError, match="dated rate rows"):
        module.fxmacrodata_rows_to_footprint_candles([{"date": "2024-01-01"}])

    with pytest.raises(ValueError, match="duration_seconds"):
        module.fxmacrodata_rows_to_footprint_candles(
            [{"date": "2024-01-01", "value": 1.1038}],
            duration_seconds=0,
        )


def test_fetch_fxmacrodata_candles_builds_current_api_request():
    module = load_fxmacrodata_module()
    payload = {"data": [{"date": "2024-01-01", "value": 1.1038}]}
    captured = {}

    class FakeResponse(io.StringIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self.close()

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["api_key"] = request.get_header("X-api-key")
        captured["timeout"] = timeout
        return FakeResponse(json.dumps(payload))

    with mock.patch.object(module, "urlopen", side_effect=fake_urlopen):
        candles = module.fetch_fxmacrodata_candles(
            "EURUSD",
            "2024-01-01",
            "2024-01-31",
            api_key="test-key",
            timeout=12,
        )

    assert captured == {
        "url": (
            "https://fxmacrodata.com/api/v1/forex/EUR/USD"
            "?start_date=2024-01-01&end_date=2024-01-31"
        ),
        "api_key": "test-key",
        "timeout": 12,
    }
    assert candles.candle_close_prices[0] == 1.1038
