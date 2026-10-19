# Wrap Why

Fixed-width integer wraparound. Add 1 to 127 in an 8-bit signed integer and two's complement hands back -128.

## What it computes

- **The range truth** - what an 8, 16, 32 or 64-bit signed or unsigned integer can hold, and which bit patterns are the extremes.
- **The wrap truth** - a whole number forced into a width by keeping only its low bits, with the hex pattern and the exact amount subtracted or added.
- **The cast truth** - the same number moved between widths and kinds, and why it did or did not change (sign extension, truncation, or a different sign rule).

Values are whole numbers of up to 40 digits. Widths are 8, 16, 32 and 64.

## Boundary

Arithmetic only, on two's complement integers. It does not know your language or compiler: some treat signed overflow as undefined, some use arbitrary-size or floating-point numbers. Every value is the owner's own entry.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic (BigInt remainders).
- `oracle.py` - the Python mirror (explicit bit strings, text sign extension and truncation) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (68 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/wrapwhy/
Repo: https://github.com/iLanis-agent/wrapwhy
