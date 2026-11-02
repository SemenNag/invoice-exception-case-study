# case-001: acceptance notes

PDF layout: 1; number format: 1,234.56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(120 x 8.75, 2) = 1050.00; round(1050.00 x 0.20, 2) = 210.00.
- L02: round(80 x 6.40, 2) = 512.00; round(512.00 x 0.20, 2) = 102.40.
- L03: round(6 x 32.50, 2) = 195.00; round(195.00 x 0.20, 2) = 39.00.
- L04: round(12 x 7.35, 2) = 88.20; round(88.20 x 0.20, 2) = 17.64.

Calculated totals: 1845.20 + 369.04 = 2214.24 EUR.
Declared totals: 1845.20 + 369.04; total 2214.24 EUR.

## Intentional condition

None: 4 construction supply lines, exact SKU/reference, full receipt and matching prices/bank.

## Step results

### Step 1: new / clear

- All applicable checks pass, or no checks for a duplicate.
- L01 -> OL-001-01 (deterministic): ordered 120, received 120, previously invoiced 0; available = 120 - 0 = 120; remaining = 120 - 0 = 120.
- L02 -> OL-001-02 (deterministic): ordered 80, received 80, previously invoiced 0; available = 80 - 0 = 80; remaining = 80 - 0 = 80.
- L03 -> OL-001-03 (deterministic): ordered 6, received 6, previously invoiced 0; available = 6 - 0 = 6; remaining = 6 - 0 = 6.
- L04 -> OL-001-04 (deterministic): ordered 12, received 12, previously invoiced 0; available = 12 - 0 = 12; remaining = 12 - 0 = 12.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
