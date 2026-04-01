# PRODIGY_CS_02 - Pixel Manipulation for Image Encryption

Educational tool for the Prodigy InfoTech Cyber Security **Task-02**: encrypt and decrypt images by manipulating pixels (XOR, modular addition/subtraction, and a reversible red/blue channel swap).

## What this project does

- **Encrypt** an image file to a **PNG** using a chosen mode and (where required) a text **key**.
- **Decrypt** with the **same mode and key** to recover the original pixels (lossless when using PNG end-to-end).

Images are processed internally as **RGBA**. The alpha channel is **not** altered by XOR/add (only RGB channels are transformed).

## Requirements

- Python **3.10+**
- Install dependencies:

```bash
pip install -r requirements.txt
```

## How to run

From this folder, after installing dependencies:

**XOR (default)** â€” reversible with the same key:

```bash
python image_crypto.py encrypt photo.jpg scrambled.png -k "your-secret-key" -m xor
python image_crypto.py decrypt scrambled.png restored.png -k "your-secret-key" -m xor
```

**Add / subtract (mod 256)** â€” encryption adds a key-derived byte per channel; decryption subtracts:

```bash
python image_crypto.py encrypt photo.png out.png -k "mykey" -m add
python image_crypto.py decrypt out.png back.png -k "mykey" -m add
```

**Swap red and blue** â€” no secret material; encrypt and decrypt both apply the same swap (so one round-trip restores the image). You can omit `-k` for this mode:

```bash
python image_crypto.py encrypt photo.png swapped.png -m swap_rb
python image_crypto.py decrypt swapped.png original.png -m swap_rb
```

Help:

```bash
python image_crypto.py --help
python image_crypto.py encrypt --help
```

## Repository layout

| File | Purpose |
|------|---------|
| `image_crypto.py` | Pixel operations + command-line interface |
| `README.md` | Quick start and usage |
| `requirements.txt` | Dependency list |

## Ethics and scope

This is a **learning demo**, not a substitute for real image protection. The XOR/add stream is **not** cryptographically strong for serious threats. Use only on images you own or are allowed to process.

## Author

**Mario Makhlouta** â€” intern at Prodigy InfoTech (April 2026). Project: **PRODIGY_CS_02**.
