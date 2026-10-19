// Wrap Why engine: fixed-width two's complement integers on BigInt arithmetic.
var BITS_ERR = "width must be 8, 16, 32 or 64 bits";
var KIND_ERR = "kind must be signed or unsigned";
var VAL_ERR = "value must be a whole number of at most 40 digits";

function _bits(t) {
  t = typeof t === "string" ? t.trim() : "";
  if (t !== "8" && t !== "16" && t !== "32" && t !== "64") throw new Error(BITS_ERR);
  return BigInt(t);
}
function _kind(t) {
  t = typeof t === "string" ? t.trim() : "";
  if (t !== "signed" && t !== "unsigned") throw new Error(KIND_ERR);
  return t;
}
function _val(t) {
  t = typeof t === "string" ? t.trim() : "";
  if (!/^-?[0-9]{1,40}$/.test(t)) throw new Error(VAL_ERR);
  return BigInt(t);
}
function _lo(b, k) { return k === "signed" ? -(1n << (b - 1n)) : 0n; }
function _hi(b, k) { return k === "signed" ? (1n << (b - 1n)) - 1n : (1n << b) - 1n; }
function _hex(v, b) {
  var m = v & ((1n << b) - 1n);
  var s = m.toString(16).toUpperCase();
  while (s.length < Number(b) / 4) s = "0" + s;
  return "0x" + s;
}
function _wrap(v, b, k) {
  var m = 1n << b;
  var r = ((v % m) + m) % m;
  if (k === "signed" && r >= (m >> 1n)) r -= m;
  return r;
}
function _name(b, k) { return b + "-bit " + k; }

// The range truth: what a width and kind can hold.
function rangeTruth(bits, kind) {
  var b = _bits(bits), k = _kind(kind);
  var lo = _lo(b, k), hi = _hi(b, k), count = 1n << b;
  var s = "The " + _name(b, k) + " integer holds " + lo + " to " + hi + ", " + count + " values in all. ";
  if (k === "signed") s += "The top bit is the sign bit, so " + _hex(lo, b) + " is " + lo + " and " + _hex(-1n, b) + " is -1.";
  else s += "Adding 1 to " + hi + " wraps to 0, and taking 1 from 0 wraps to " + hi + ".";
  return s;
}

// The wrap truth: a whole number forced into a width by keeping only its low bits.
function wrapTruth(value, bits, kind) {
  var v = _val(value), b = _bits(bits), k = _kind(kind);
  var lo = _lo(b, k), hi = _hi(b, k);
  var range = "(" + lo + " to " + hi + ")";
  if (v >= lo && v <= hi) return v + " fits in " + _name(b, k) + " " + range + ", so it is stored unchanged as " + _hex(v, b) + ".";
  var r = _wrap(v, b, k), m = 1n << b, q = (v - r) / m;
  var how = q > 0n ? v + " minus " + (q === 1n ? "" : q + " x ") + m : v + " plus " + (q === -1n ? "" : (-q) + " x ") + m;
  return v + " does not fit in " + _name(b, k) + " " + range + ". Keeping the low " + b + " bits gives " + _hex(v, b) + ", which reads as " + r + " (" + how + ").";
}

// The cast truth: the same number moved from one width and kind to another.
function castTruth(value, fromBits, fromKind, toBits, toKind) {
  var v = _val(value), fb = _bits(fromBits), fk = _kind(fromKind), tb = _bits(toBits), tk = _kind(toKind);
  var lo = _lo(fb, fk), hi = _hi(fb, fk);
  if (v < lo || v > hi) throw new Error(v + " does not fit in " + _name(fb, fk) + " (" + lo + " to " + hi + ")");
  var r = _wrap(v, tb, tk);
  var why;
  if (tb > fb) why = v < 0n && fk === "signed" ? "the sign bit is copied into the new top bits" : "the new top bits are zeros";
  else if (tb < fb) why = "only the low " + tb + " bits are kept";
  else why = fk === tk ? "the bits are the same" : "the same bits are read with the other sign rule";
  return v + " as " + _name(fb, fk) + " is " + _hex(v, fb) + ". As " + _name(tb, tk) + " it is " + r + " (" + _hex(r, tb) + "), because " + why + ". " +
    (r === v ? "The value is unchanged." : "The value changes from " + v + " to " + r + ".");
}
