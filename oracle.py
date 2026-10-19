#!/usr/bin/env python3
# Wrap Why oracle - mirrors engine.js but works on explicit bit strings (sign extension and truncation done as text).
import json, re

BITS_ERR = "width must be 8, 16, 32 or 64 bits"
KIND_ERR = "kind must be signed or unsigned"
VAL_ERR = "value must be a whole number of at most 40 digits"

def bits_of(t):
    t = t.strip() if isinstance(t, str) else ""
    if t not in ("8", "16", "32", "64"): raise ValueError(BITS_ERR)
    return int(t)

def kind_of(t):
    t = t.strip() if isinstance(t, str) else ""
    if t not in ("signed", "unsigned"): raise ValueError(KIND_ERR)
    return t

def val_of(t):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"-?[0-9]{1,40}", t): raise ValueError(VAL_ERR)
    return int(t)

def lo(b, k): return -(2 ** (b - 1)) if k == "signed" else 0
def hi(b, k): return 2 ** (b - 1) - 1 if k == "signed" else 2 ** b - 1

def pattern(v, b):
    # two's complement bit string of v, any size, low b bits
    n = v if v >= 0 else (1 << (abs(v).bit_length() + b)) + v
    return format(n, "b").zfill(b)[-b:]

def hexs(v, b): return "0x" + format(int(pattern(v, b), 2), "X").zfill(b // 4)

def read(bits, k):
    n = int(bits, 2)
    return n - (1 << len(bits)) if k == "signed" and bits[0] == "1" else n

def name(b, k): return f"{b}-bit {k}"

def range_truth(b, k):
    b = bits_of(b); k = kind_of(k)
    s = f"The {name(b, k)} integer holds {lo(b, k)} to {hi(b, k)}, {2 ** b} values in all. "
    if k == "signed":
        s += f"The top bit is the sign bit, so {hexs(lo(b, k), b)} is {lo(b, k)} and {hexs(-1, b)} is -1."
    else:
        s += f"Adding 1 to {hi(b, k)} wraps to 0, and taking 1 from 0 wraps to {hi(b, k)}."
    return s

def wrap_truth(v, b, k):
    v = val_of(v); b = bits_of(b); k = kind_of(k)
    rng = f"({lo(b, k)} to {hi(b, k)})"
    if lo(b, k) <= v <= hi(b, k):
        return f"{v} fits in {name(b, k)} {rng}, so it is stored unchanged as {hexs(v, b)}."
    r = read(pattern(v, b), k)
    m = 2 ** b
    q = (v - r) // m
    if q > 0:
        how = f"{v} minus " + ("" if q == 1 else f"{q} x ") + str(m)
    else:
        how = f"{v} plus " + ("" if q == -1 else f"{-q} x ") + str(m)
    return f"{v} does not fit in {name(b, k)} {rng}. Keeping the low {b} bits gives {hexs(v, b)}, which reads as {r} ({how})."

def cast_truth(v, fb, fk, tb, tk):
    v = val_of(v); fb = bits_of(fb); fk = kind_of(fk); tb = bits_of(tb); tk = kind_of(tk)
    if not lo(fb, fk) <= v <= hi(fb, fk):
        raise ValueError(f"{v} does not fit in {name(fb, fk)} ({lo(fb, fk)} to {hi(fb, fk)})")
    src = pattern(v, fb)
    if tb > fb:
        fill = src[0] if fk == "signed" else "0"
        dst = fill * (tb - fb) + src
        why = "the sign bit is copied into the new top bits" if (fk == "signed" and src[0] == "1") else "the new top bits are zeros"
    elif tb < fb:
        dst = src[-tb:]
        why = f"only the low {tb} bits are kept"
    else:
        dst = src
        why = "the bits are the same" if fk == tk else "the same bits are read with the other sign rule"
    r = read(dst, tk)
    tail = "The value is unchanged." if r == v else f"The value changes from {v} to {r}."
    return f"{v} as {name(fb, fk)} is {hexs(v, fb)}. As {name(tb, tk)} it is {r} ({hexs(r, tb)}), because {why}. {tail}"

FNS = {"rangeTruth": range_truth, "wrapTruth": wrap_truth, "castTruth": cast_truth}
CASES = []
for b in ("8", "16", "32", "64"):
    for k in ("signed", "unsigned"):
        CASES.append(("rangeTruth", [b, k]))
CASES += [("rangeTruth", [" 8 ", " signed "]), ("rangeTruth", ["12", "signed"]), ("rangeTruth", ["8", "both"]), ("rangeTruth", ["", ""])]
CASES += [
    ("wrapTruth", ["128", "8", "signed"]), ("wrapTruth", ["127", "8", "signed"]), ("wrapTruth", ["-128", "8", "signed"]), ("wrapTruth", ["-129", "8", "signed"]),
    ("wrapTruth", ["256", "8", "unsigned"]), ("wrapTruth", ["255", "8", "unsigned"]), ("wrapTruth", ["-1", "8", "unsigned"]), ("wrapTruth", ["0", "8", "unsigned"]),
    ("wrapTruth", ["2147483648", "32", "signed"]), ("wrapTruth", ["4294967296", "32", "unsigned"]), ("wrapTruth", ["600", "8", "unsigned"]), ("wrapTruth", ["-600", "8", "signed"]),
    ("wrapTruth", ["32768", "16", "signed"]), ("wrapTruth", ["65536", "16", "unsigned"]), ("wrapTruth", ["9223372036854775808", "64", "signed"]), ("wrapTruth", ["18446744073709551616", "64", "unsigned"]),
    ("wrapTruth", ["-9223372036854775809", "64", "signed"]), ("wrapTruth", ["1000000", "16", "signed"]), ("wrapTruth", ["-1", "64", "unsigned"]), ("wrapTruth", ["300", "8", "signed"]),
    ("wrapTruth", ["99999999999999999999999999999999999999", "64", "unsigned"]), ("wrapTruth", ["-99999999999999999999999999999999999999", "32", "signed"]),
    ("wrapTruth", ["1.5", "8", "signed"]), ("wrapTruth", ["abc", "8", "signed"]), ("wrapTruth", ["", "8", "signed"]), ("wrapTruth", ["12345678901234567890123456789012345678901", "8", "signed"]),
    ("wrapTruth", ["5", "7", "signed"]), ("wrapTruth", ["5", "8", "other"]),
    ("castTruth", ["-1", "8", "signed", "32", "unsigned"]), ("castTruth", ["255", "8", "unsigned", "8", "signed"]), ("castTruth", ["-1", "8", "signed", "32", "signed"]), ("castTruth", ["200", "8", "unsigned", "32", "signed"]),
    ("castTruth", ["300", "16", "signed", "8", "unsigned"]), ("castTruth", ["70000", "32", "signed", "16", "signed"]), ("castTruth", ["5", "8", "signed", "8", "signed"]), ("castTruth", ["5", "8", "signed", "8", "unsigned"]),
    ("castTruth", ["-5", "8", "signed", "8", "unsigned"]), ("castTruth", ["0", "64", "unsigned", "8", "signed"]), ("castTruth", ["-2147483648", "32", "signed", "64", "unsigned"]), ("castTruth", ["4294967295", "32", "unsigned", "32", "signed"]),
    ("castTruth", ["4294967295", "32", "unsigned", "64", "signed"]), ("castTruth", ["18446744073709551615", "64", "unsigned", "64", "signed"]), ("castTruth", ["-1", "64", "signed", "8", "unsigned"]), ("castTruth", ["65535", "16", "unsigned", "8", "signed"]),
    ("castTruth", ["-32768", "16", "signed", "8", "signed"]), ("castTruth", ["128", "16", "signed", "8", "signed"]), ("castTruth", ["127", "8", "signed", "16", "unsigned"]), ("castTruth", ["-129", "16", "signed", "8", "signed"]),
    ("castTruth", ["128", "8", "signed", "16", "signed"]), ("castTruth", ["256", "8", "unsigned", "16", "signed"]), ("castTruth", ["-1", "8", "unsigned", "16", "signed"]), ("castTruth", ["1", "x", "signed", "8", "signed"]),
    ("castTruth", ["1", "8", "signed", "9", "signed"]), ("castTruth", ["1", "8", "wide", "8", "signed"]), ("castTruth", ["1", "8", "signed", "8", "wide"]), ("castTruth", ["z", "8", "signed", "8", "signed"]),
]

out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
