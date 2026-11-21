/*
 * XXTEA (Corrected Block TEA) helper for WzryUID.
 * Self-contained CommonJS module. Data and key are passed via stdin/argv as base64/utf8.
 * Usage: node xxtea_helper.js <e|d> <key-utf8>   (base64 data on stdin, base64 result on stdout)
 * Algorithm mirrors GloryOfKings-Plugin/utils/xxtea.js (standard XXTEA with embedded length).
 */
'use strict';

const DELTA = 0x9E3779B9;
const WORD_BYTES = 4;
const KEY_WORDS = 4;

function bytesToWords(buffer, withLength) {
  const words = new Array(Math.ceil(buffer.length / WORD_BYTES));
  for (let i = 0; i < words.length; i++) {
    const at = i * WORD_BYTES;
    words[i] = ((buffer[at] || 0) |
      ((buffer[at + 1] || 0) << 8) |
      ((buffer[at + 2] || 0) << 16) |
      ((buffer[at + 3] || 0) << 24)) >>> 0;
  }
  if (withLength) words.push(buffer.length);
  return words;
}

function wordsToBytes(words, withLength) {
  let size = words.length * WORD_BYTES;
  if (withLength) {
    const declared = words[words.length - 1];
    if (declared < 0 || declared > size - WORD_BYTES) return Buffer.alloc(0);
    size = declared;
  }
  const out = Buffer.alloc(size);
  for (let i = 0; i < size; i++) {
    out[i] = (words[i >>> 2] >>> ((i & 3) * 8)) & 0xFF;
  }
  return out;
}

function toKeyWords(key) {
  const words = bytesToWords(key, false);
  while (words.length < KEY_WORDS) words.push(0);
  return words.slice(0, KEY_WORDS);
}

function mix(sum, y, z, p, e, keyWords) {
  const a = ((z >>> 5) ^ (y << 2)) + ((y >>> 3) ^ (z << 4));
  const b = (sum ^ y) + (keyWords[(p & 3) ^ e] ^ z);
  return (a ^ b) >>> 0;
}

function encrypt(data, key) {
  const input = Buffer.isBuffer(data) ? data : Buffer.from(data);
  const keyBuffer = Buffer.isBuffer(key) ? key : Buffer.from(key);
  if (!input.length) return Buffer.alloc(0);
  const words = bytesToWords(input, true);
  const keyWords = toKeyWords(keyBuffer);
  const rounds = Math.floor(6 + 52 / words.length);
  const last = words.length - 1;
  let sum = 0;
  let z = words[last];
  for (let round = 0; round < rounds; round++) {
    sum = (sum + DELTA) >>> 0;
    const e = (sum >>> 2) & 3;
    for (let p = 0; p < last; p++) {
      const y = words[p + 1];
      words[p] = (words[p] + mix(sum, y, z, p, e, keyWords)) >>> 0;
      z = words[p];
    }
    const y0 = words[0];
    words[last] = (words[last] + mix(sum, y0, z, last, e, keyWords)) >>> 0;
    z = words[last];
  }
  return wordsToBytes(words, false);
}

function decrypt(data, key) {
  const input = Buffer.isBuffer(data) ? data : Buffer.from(data);
  const keyBuffer = Buffer.isBuffer(key) ? key : Buffer.from(key);
  if (!input.length) return Buffer.alloc(0);
  const words = bytesToWords(input, false);
  const keyWords = toKeyWords(keyBuffer);
  const last = words.length - 1;
  const rounds = Math.floor(6 + 52 / words.length);
  let sum = (rounds * DELTA) >>> 0;
  let y = words[0];
  while (sum !== 0) {
    const e = (sum >>> 2) & 3;
    for (let p = last; p > 0; p--) {
      const z = words[p - 1];
      words[p] = (words[p] - mix(sum, y, z, p, e, keyWords)) >>> 0;
      y = words[p];
    }
    const zLast = words[last];
    words[0] = (words[0] - mix(sum, y, zLast, 0, e, keyWords)) >>> 0;
    y = words[0];
    sum = (sum - DELTA) >>> 0;
  }
  return wordsToBytes(words, true);
}

const op = process.argv[2];
const key = process.argv[3];
const chunks = [];
process.stdin.on('data', (c) => chunks.push(c));
process.stdin.on('end', () => {
  const data = Buffer.from(Buffer.concat(chunks).toString('utf8').trim(), 'base64');
  const result = op === 'e' ? encrypt(data, key) : decrypt(data, key);
  process.stdout.write(result.toString('base64'));
});
