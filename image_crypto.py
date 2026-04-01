"""
Image encryption via pixel manipulation (XOR, modular add/subtract, channel swap).

Prodigy InfoTech — PRODIGY_CS_02 — educational use only.
"""

from __future__ import annotations

import argparse
import hashlib
from enum import Enum
from pathlib import Path

import numpy as np
from PIL import Image


class Mode(str, Enum):
    XOR = "xor"
    ADD = "add"
    SWAP_RB = "swap_rb"


def _load_rgba(path: Path) -> tuple[np.ndarray, str]:
    img = Image.open(path).convert("RGBA")
    arr = np.asarray(img, dtype=np.uint8)
    return arr, "RGBA"


def _save_rgba(arr: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr, mode="RGBA").save(path, format="PNG")


def _keystream_rgb(shape_hwc: tuple[int, int, int], key: str) -> np.ndarray:
    """Deterministic pseudo-random bytes for RGB (H, W, 3) from key."""
    h, w, c = shape_hwc
    if c != 3:
        raise ValueError("keystream expects RGB slice shape (*, *, 3)")
    need = h * w * 3
    out = bytearray()
    counter = 0
    k = key.encode("utf-8")
    while len(out) < need:
        out.extend(hashlib.sha256(k + b":" + str(counter).encode()).digest())
        counter += 1
    stream = np.frombuffer(bytes(out[:need]), dtype=np.uint8).reshape(h, w, 3)
    return stream


def _rgb_and_alpha(arr: np.ndarray) -> tuple[np.ndarray, np.ndarray | None]:
    if arr.shape[2] == 4:
        return arr[:, :, :3], arr[:, :, 3:4]
    if arr.shape[2] == 3:
        return arr, None
    raise ValueError("Expected RGBA image array")


def _merge_rgb_alpha(rgb: np.ndarray, alpha: np.ndarray | None, base: np.ndarray) -> np.ndarray:
    if alpha is None:
        out = base.copy()
        out[:, :, :3] = rgb
        return out
    out = base.copy()
    out[:, :, :3] = rgb
    out[:, :, 3:4] = alpha
    return out


def encrypt_xor(arr: np.ndarray, key: str) -> np.ndarray:
    rgb, alpha = _rgb_and_alpha(arr)
    ks = _keystream_rgb(rgb.shape, key)
    new_rgb = rgb ^ ks
    return _merge_rgb_alpha(new_rgb, alpha, arr)


def decrypt_xor(arr: np.ndarray, key: str) -> np.ndarray:
    return encrypt_xor(arr, key)


def encrypt_add(arr: np.ndarray, key: str) -> np.ndarray:
    rgb, alpha = _rgb_and_alpha(arr)
    ks = _keystream_rgb(rgb.shape, key)
    new_rgb = (rgb.astype(np.int16) + ks.astype(np.int16)) % 256
    return _merge_rgb_alpha(new_rgb.astype(np.uint8), alpha, arr)


def decrypt_add(arr: np.ndarray, key: str) -> np.ndarray:
    rgb, alpha = _rgb_and_alpha(arr)
    ks = _keystream_rgb(rgb.shape, key)
    new_rgb = (rgb.astype(np.int16) - ks.astype(np.int16)) % 256
    return _merge_rgb_alpha(new_rgb.astype(np.uint8), alpha, arr)


def encrypt_swap_rb(arr: np.ndarray, _key: str) -> np.ndarray:
    del _key  # swap is fixed; key kept for CLI consistency with task brief
    rgb, alpha = _rgb_and_alpha(arr)
    out_rgb = rgb.copy()
    out_rgb[:, :, 0], out_rgb[:, :, 2] = rgb[:, :, 2].copy(), rgb[:, :, 0].copy()
    return _merge_rgb_alpha(out_rgb, alpha, arr)


def decrypt_swap_rb(arr: np.ndarray, key: str) -> np.ndarray:
    return encrypt_swap_rb(arr, key)


def run(mode: Mode, key: str, input_path: Path, output_path: Path) -> None:
    arr, _ = _load_rgba(input_path)
    if mode is Mode.XOR:
        out = encrypt_xor(arr, key)
    elif mode is Mode.ADD:
        out = encrypt_add(arr, key)
    else:
        out = encrypt_swap_rb(arr, key)
    _save_rgba(out, output_path)


def run_decrypt(mode: Mode, key: str, input_path: Path, output_path: Path) -> None:
    arr, _ = _load_rgba(input_path)
    if mode is Mode.XOR:
        out = decrypt_xor(arr, key)
    elif mode is Mode.ADD:
        out = decrypt_add(arr, key)
    else:
        out = decrypt_swap_rb(arr, key)
    _save_rgba(out, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Encrypt/decrypt images using pixel manipulation (PRODIGY_CS_02)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("input", type=Path, help="Input image path")
    common.add_argument("output", type=Path, help="Output PNG path")
    common.add_argument(
        "-k",
        "--key",
        type=str,
        default="",
        help="Secret string (used for xor/add; ignored for swap_rb except must be non-empty for add/xor)",
    )
    common.add_argument(
        "-m",
        "--mode",
        choices=[m.value for m in Mode],
        default=Mode.XOR.value,
        help="xor: XOR with key stream | add: (pixel+key) mod 256 | swap_rb: swap red/blue channels",
    )

    sub.add_parser("encrypt", parents=[common], help="Encrypt image")
    sub.add_parser("decrypt", parents=[common], help="Decrypt image")

    args = parser.parse_args()
    mode = Mode(args.mode)
    if mode in (Mode.XOR, Mode.ADD) and not args.key:
        parser.error("--key is required for modes xor and add")

    if args.command == "encrypt":
        run(mode, args.key, args.input, args.output)
    else:
        run_decrypt(mode, args.key, args.input, args.output)


if __name__ == "__main__":
    main()
