import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ulpin_codec import decode_ulpin, encode_ulpin  # noqa: E402
from extract import normalize_khasra, normalize_khata  # noqa: E402


def test_encode_example():
    assert encode_ulpin(25.068164, 85.623346) == "832454DYJFAQH0"


def test_decode_roundtrip():
    lat, lon = decode_ulpin("832454DYJFAQH0")
    assert abs(lat - 25.068164) < 1e-6
    assert abs(lon - 85.623346) < 1e-6


def test_khasra_subdivisions():
    assert normalize_khasra("Khasra 127/1/1") == "127/1/1"
    assert normalize_khata("45/2") == "45/2"
