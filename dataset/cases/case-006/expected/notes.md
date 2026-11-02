# case-006: acceptance notes

PDF layout: 1; number format: 1.234,56.
All companies and account values are synthetic. Checks are computed from core-v1 by the reviewer-side generator, not assigned by case number.

## Decimal arithmetic

- L01: round(30 x 18.50, 2) = 555.00; round(555.00 x 0.20, 2) = 111.00.
- L02: round(4 x 44.90, 2) = 179.60; round(179.60 x 0.20, 2) = 35.92.

Calculated totals: 734.60 + 146.92 = 881.52 EUR.
Declared totals: 734.60 + 146.92; total 881.52 EUR.

## Intentional condition

Supplier registration differs from the referenced PO supplier despite a similar name. The document IBAN belongs to the document supplier, so BANK_ACCOUNT passes.

## Step results

### Step 1: new / blocked

- SUPPLIER_IDENTITY/DOC-006: fail, severity=blocked, depends_on=None.
- L01 -> OL-006-01 (deterministic): ordered 30, received 30, previously invoiced 0; available = 30 - 0 = 30; remaining = 30 - 0 = 30.
- L02 -> OL-006-02 (deterministic): ordered 4, received 4, previously invoiced 0; available = 4 - 0 = 4; remaining = 4 - 0 = 4.

## Manual acceptance

- Inspect the rendered PDF against extraction; read table, identifiers, bank, date and total.
- Confirm text-layer excerpts, including original fixtures, with validate_dataset.py and generator audit.
- Verify the only exceptional checks are listed above; all other applicable checks pass.
- No expected outcomes, semantic case labels or reference calculations are printed in runtime PDFs or context.
