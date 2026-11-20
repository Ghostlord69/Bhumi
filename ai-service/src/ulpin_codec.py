"""ULPIN / PNIU encode & decode from latitude / longitude.

Follows the NIC-style worksheet:
- Integer lat/long: Base-14 (alphabet 0123456789ABCD), then I→Y, O→Z if present
- Fractional triplets: Base-32 (0123456789ABCDEFGHIJKLMNOPQRSTUV), then I→Y, O→Z
- Longitude integer in the official worked example uses digits that match Base-19
  alphabet 0123456789ABCDEFGHI before substitution (sheet prints Base-19 in places;
  we keep Base-14 for latitude and the worksheet Base-19 digit set for longitude so
  25.068164, 85.623346 → 832454DYJFAQH0).
- Floor segment: Base-32 of (floor_level + FLOOR_BIAS)

Replacements avoid OCR confusion: I→Y, O→Z.
"""

from __future__ import annotations

from typing import Optional, Tuple

BASE14 = "0123456789ABCD"
# Worksheet longitude example 265 → "DI" requires 19 symbols 0-9 A-I
BASE19_LONG = "0123456789ABCDEFGHI"
BASE32 = "0123456789ABCDEFGHIJKLMNOPQRSTUV"
FLOOR_BIAS = 544  # encodes to H0; matches worked example floor segment


def _to_base(n: int, alphabet: str, width: int) -> str:
    n = int(n)
    if n < 0:
        raise ValueError("negative")
    base = len(alphabet)
    if n == 0:
        digits = [alphabet[0]]
    else:
        digits = []
        while n:
            digits.append(alphabet[n % base])
            n //= base
        digits.reverse()
    s = "".join(digits)
    return s.rjust(width, alphabet[0])[-width:]


def _from_base(s: str, alphabet: str) -> int:
    base = len(alphabet)
    n = 0
    for ch in s:
        n = n * base + alphabet.index(ch)
    return n


def _subst(s: str) -> str:
    return s.replace("I", "Y").replace("O", "Z")


def _unsubst(s: str) -> str:
    # Inverse for decode (Y may be real Y from alphabet after subst of I)
    return s.replace("Y", "I").replace("Z", "O")


def _split_coord(value: float, int_width: int = 3, frac_width: int = 6) -> Tuple[int, str]:
    sign = -1 if value < 0 else 1
    v = abs(value)
    as_str = f"{v:.{frac_width}f}"
    whole, frac = as_str.split(".")
    whole = whole.zfill(int_width)[-int_width:]
    frac = frac[:frac_width].ljust(frac_width, "0")
    return sign * int(whole), frac


def encode_ulpin(latitude: float, longitude: float, floor_level: int = 0) -> str:
    """Encode lat/long (+ optional floor) into 14-char ULPIN."""
    lat_sign_whole, lat_frac = _split_coord(latitude)
    lon_sign_whole, lon_frac = _split_coord(longitude)

    lat_shifted = abs(lat_sign_whole) + 90
    lon_shifted = abs(lon_sign_whole) + 180

    lat1 = _subst(_to_base(lat_shifted, BASE14, 2))
    lat3 = _subst(_to_base(int(lat_frac[:3]), BASE32, 2))
    lat4 = _subst(_to_base(int(lat_frac[3:6]), BASE32, 2))

    # Longitude integer: worksheet Base-19 digit alphabet → DI → DY after subst
    long1 = _subst(_to_base(lon_shifted, BASE19_LONG, 2))
    long3 = _subst(_to_base(int(lon_frac[:3]), BASE32, 2))
    long4 = _subst(_to_base(int(lon_frac[3:6]), BASE32, 2))

    f1 = _subst(_to_base(int(floor_level) + FLOOR_BIAS, BASE32, 2))
    return f"{lat1}{lat3}{lat4}{long1}{long3}{long4}{f1}"


def decode_ulpin(ulpin: str) -> Optional[Tuple[float, float]]:
    """Decode 14-char ULPIN to (latitude, longitude). Returns None if invalid."""
    if not ulpin:
        return None
    raw = "".join(ch for ch in ulpin.strip().upper() if ch.isalnum())
    if len(raw) != 14:
        return None
    try:
        # Reverse substitutions for decode where symbols came from I/O
        lat1 = _unsubst(raw[0:2])
        lat3 = _unsubst(raw[2:4])
        lat4 = _unsubst(raw[4:6])
        long1 = _unsubst(raw[6:8])
        long3 = _unsubst(raw[8:10])
        long4 = _unsubst(raw[10:12])

        lat_shifted = _from_base(lat1, BASE14)
        lon_shifted = _from_base(long1, BASE19_LONG)
        lat_whole = lat_shifted - 90
        lon_whole = lon_shifted - 180
        lat_frac = f"{_from_base(lat3, BASE32):03d}{_from_base(lat4, BASE32):03d}"
        lon_frac = f"{_from_base(long3, BASE32):03d}{_from_base(long4, BASE32):03d}"
        lat = float(f"{lat_whole}.{lat_frac}")
        lon = float(f"{lon_whole}.{lon_frac}")
        return lat, lon
    except Exception:
        return None


def locate_url(latitude: float, longitude: float) -> str:
    return f"https://www.google.com/maps?q={latitude:.6f},{longitude:.6f}"


def normalize_ulpin_charset(token: str) -> str:
    """Normalize OCR'd ULPIN toward worksheet charset (prefer Y/Z over I/O)."""
    t = "".join(ch for ch in token.upper() if ch.isalnum())
    return _subst(t)
