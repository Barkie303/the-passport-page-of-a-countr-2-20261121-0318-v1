# The Passport Page of a Country That Isn't There

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Barkie303/the-passport-page-of-a-countr-2-20261121-0318-v1/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Barkie303/the-passport-page-of-a-countr-2-20261121-0318-v1/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

An uncaptioned open passport spread for a country that does not exist: the
**Republic of Velmora**, a landlocked alpine republic whose capital is
Drenvar and whose language is Velmoric.

The left page is the data page of holder **Mara Ilsen** (born 08 JUN 1996 in
Drenvar): a drawn portrait, her details, her signature and right-thumb mark,
and a machine-readable strip in the standard format with computed check
digits. The passport was issued 12 MAR 2024 in Drenvar and expires
12 MAR 2034.

The right page is the visa page. Six border stamps from the neighbouring
invented countries **Kestria** (Tarn Crossing) and the **Ondal Republic**
(Port Lir) tell one travel history, every stamp dated after the passport's
issue: Kestria in and out in May 2024, Ondal in and out in September 2025,
Kestria in and out again in January 2026.

The telling detail is the red visa-condition stamp: *"HOLDER MUST PRESENT
ONE FOLK SONG AT BORDER CONTROL"* (Art. 17, Border Code) — Velmora is a
place where a song is a travel document, and the border officer is also
its audience. Below it, the mountain pass fee stamp: 12 kron, paid.

## How it is built

`draw.py` renders `entry.png` (1024×1024, under 1 MiB) with Pillow: the
portrait is drawn from simple shapes, the stamps are rotated ink layers, and
the MRZ check digits use the standard 7-3-1 weighting. `main.ts` copies the
image to `/output/entry.png`, refusing to run if it is over the 1 MiB gate.

Run it locally:

```sh
python3 draw.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```
