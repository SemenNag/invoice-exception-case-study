# case-008: acceptance notes

PDF layout: 2; number format: 1.234,56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(35 x 31.60, 2) = 1106.00; round(1106.00 x 0.20, 2) = 221.20.
- L02: round(20 x 14.20, 2) = 284.00; round(284.00 x 0.20, 2) = 56.80.
- L03: round(10 x 22.40, 2) = 224.00; round(224.00 x 0.20, 2) = 44.80.

Calculated totals: 1614.00 + 322.80 = 1936.80 EUR.
Declared totals: 1614.00 + 322.80; total 1936.80 EUR.

## Intentional condition

No financial violation: same business key and normalized facts as the counted original, different layout/number format/hash. Duplicate, without a new assessment.

## Step results

### Step 1: duplicate / no new assessment

- All applicable checks pass, or no checks for a duplicate.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
