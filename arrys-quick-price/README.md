# Arry's Quick Price

A one-page roofing price calculator with margin suggestions. It's a working demo of a cleaned-up version of Arry's Roofing **Price Estimator** workbook (`Price_Estimator.ARS_1.xls`).

> **Demo only.** Rates are the 2018 sample values from the workbook. Don't quote customers from it until current material, labor and overhead numbers are loaded.

## What it does

- **Inputs:** roof type (shingle, metal, tile, TPO), measured squares, pitch, tear-off layers, waste %, profit margin
- **Live price:** customer price, price per square, breakeven, and the net margin kept after card fees and commission
- **Margin suggestions:** Floor / Target / Stretch presets, plus a margin ladder showing the price at each margin
- **Check a number:** enter a customer budget or competitor bid to see the margin it leaves
- **System comparison:** the same roof priced in all four systems
- **Editable assumptions:** overhead factor, tax, fees, commission, margin floor, and per-system rates
- **Validation:** out-of-range inputs are flagged, and pricing pauses until they're fixed

## Pricing formula

```
materials  = material $/sq × squares × (1 + sales tax) × (1 + waste)
labor      = (labor $/sq + pitch add) × squares
job costs  = fixed job costs + dump $/sq × squares × layers + warranty
overhead   = overhead factor × (materials + labor + job costs)
breakeven  = materials + labor + job costs + overhead
price      = breakeven ÷ (1 − margin) ÷ (1 − card fee) ÷ (1 − commission)
```

### Changes from the workbook

| Workbook | This tool |
|---|---|
| Overhead formula referenced an empty cell (`I134`), so permits, dump and warranty got no overhead | Overhead applies to all direct costs |
| Shingle, Tile and TPO sheets pulled the overhead factor from three external files | One overhead factor for every system |
| 5% waste applied to every material line, boots and nails included | Waste applies to the roof covering only |
| No minimum margin | A margin floor flags quotes that need manager approval |

Two assumptions are new to the demo and aren't in the workbook: pitch labor adds (+$15 / +$30 / +$50 per square) and dump fees that multiply by tear-off layers.

## Run it

It's a single static file with no build step and no dependencies (Google Fonts is optional; system fonts are the fallback).

- **Locally:** open `index.html` in a browser
- **GitHub Pages:** push this repo, then go to **Settings → Pages → Deploy from a branch**, choose `main` and `/ (root)`

## Tests

`tests/stress_test.py` drives the page in headless Chromium. It clicks every control, enters bad inputs, checks phone widths, and confirms the hero price, the ladder and the build-up always agree.

```bash
pip install playwright
playwright install chromium
python tests/stress_test.py
```

## Next steps

1. Load current (2026) material and labor rates
2. Recalculate the overhead factor from this year's budget
3. Move rates into a separate `rates.json` so they can be updated without touching the page
