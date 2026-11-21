// A working passport-spread entry (Node 22, standard library only): its image
// is the entry.png beside this file, and the program copies it to
// /output/entry.png. The image is an invented passport spread for the
// Republic of Velmora, drawn by draw.py in this repository.
// The gate takes a whole PNG or JPEG of at most 1 MiB and 1024 by 1024
// pixels, and the judge sees exactly the bytes copied. The program runs
// twice in grading, and both runs must write the same bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const src = new URL('./entry.png', import.meta.url);
const size = statSync(src).size;
if (size > 1048576) {
  throw new Error(`entry.png is ${size} bytes, over the 1 MiB gate`);
}
copyFileSync(src, join(outDir, 'entry.png'));
