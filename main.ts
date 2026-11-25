// THE DAILY WORLD — front page for Wednesday 25 November 2026.
// The image is drawn by draw.py (PIL) and shipped as entry.png in this repo;
// this program copies it to /output/entry.png with gate guards.
import { copyFileSync, existsSync, readFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const OUT = join(OUT_DIR, "entry.png");

if (!existsSync(SRC)) {
  console.error("entry.png missing from repository");
  process.exit(1);
}
const buf = readFileSync(SRC);
// PNG signature: 89 50 4E 47 0D 0A 1A 0A
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!buf.subarray(0, 8).equals(PNG_SIG)) {
  console.error("entry.png is not a PNG");
  process.exit(1);
}
if (buf.length > 1048576) {
  console.error(`entry.png is ${buf.length} bytes, over the 1 MiB gate`);
  process.exit(1);
}
// IHDR: width/height are big-endian uint32 at bytes 16..24.
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  console.error(`entry.png is ${width}x${height}, gate needs 1024x1024`);
  process.exit(1);
}
// CRC-32 (PNG chunk checksums) — table-driven, no dependency.
const CRC_TABLE = (() => {
  const table = new Int32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c;
  }
  return table;
})();
function crc32(b: Buffer): number {
  let c = 0xffffffff;
  for (let i = 0; i < b.length; i++) c = CRC_TABLE[(c ^ b[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
// Walk every PNG chunk, verify its CRC, require IHDR first and IEND last,
// and that the chunks consume the buffer exactly — a truncated or corrupt
// file (right signature, right IHDR, missing data) must fail here.
let off = 8;
let first = true;
let sawIend = false;
while (off < buf.length) {
  if (off + 12 > buf.length) {
    console.error("PNG truncated inside a chunk header");
    process.exit(1);
  }
  const len = buf.readUInt32BE(off);
  const type = buf.toString("ascii", off + 4, off + 8);
  if (off + 12 + len > buf.length) {
    console.error(`PNG truncated inside chunk ${type}`);
    process.exit(1);
  }
  const stored = buf.readUInt32BE(off + 8 + len);
  const computed = crc32(buf.subarray(off + 4, off + 8 + len));
  if (stored !== computed) {
    console.error(`PNG chunk ${type} has a bad CRC`);
    process.exit(1);
  }
  if (first && type !== "IHDR") {
    console.error("PNG does not start with IHDR");
    process.exit(1);
  }
  first = false;
  if (type === "IEND") {
    sawIend = true;
    off += 12 + len;
    break;
  }
  off += 12 + len;
}
if (!sawIend || off !== buf.length) {
  console.error("PNG is missing IEND or has trailing bytes");
  process.exit(1);
}
copyFileSync(SRC, OUT);
// Read-back check: the file on disk must be byte-identical to the source,
// so a partial or failed copy can never pass as an entry.
const written = readFileSync(OUT);
if (!written.equals(buf)) {
  console.error("read-back check failed: /output/entry.png differs from entry.png");
  process.exit(1);
}
const outSize = statSync(OUT).size;
if (outSize !== buf.length) {
  console.error(`read-back size mismatch: ${outSize} vs ${buf.length}`);
  process.exit(1);
}
console.log(`wrote ${OUT} (${buf.length} bytes, 1024x1024, read-back verified)`);
