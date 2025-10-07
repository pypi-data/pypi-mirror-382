#
#   Copyright (c) 2018-2020 eGauge Systems LLC
# 	1644 Conestoga St, Suite 2
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
import re

import tablib
from django.core.exceptions import ValidationError

from epic.models import Part, format_part_number

LINE_ITEM_COLUMNS = ["qty", "part", "amount"]
DELTA_COLUMNS = ["qty", "part"]

ALTERNATE_NAMES = {
    "qty": ["quantity", "count"],
    "part": ["pn", "ep"],
    "amount": ["cost", "price"],
}


def clean_part(part, row_num, part_row):
    """Verify that "part" is a valid (existing) part number.  May be
    specified as an number or as a string starting with the letters
    "EP".  Case is ignored.  For example: "5", "ep5", "EP0005" would
    all refer to part number 5.  Returns the part specified by
    "pn_str" or raises ValidationError in case of error.

    """
    if isinstance(part, str):
        m = re.match(r"ep(\d+)$", part, re.IGNORECASE)
        if m:
            part = int(m.group(1))
        else:
            try:
                part = int(part)
            except ValueError as e:
                raise ValidationError(
                    '"%s" is not a valid part number.' % part
                ) from e
    qs = Part.objects.filter(id=part)
    if not qs.exists():
        raise ValidationError(
            "Part %s does not exist." % format_part_number(part)
        )

    if part in part_row:
        raise ValidationError(
            "Part %s listed multiple times (rows %d and %d)."
            % (format_part_number(part), part_row[part], row_num)
        )

    part_row[part] = row_num
    return qs[0]


def clean_qty(qty, row_num, part_row):
    # pylint: disable=unused-argument
    """Verify that "qty" is a valid quantity, which must be a non-negative
    number or a decimal integer string.  Returns the number or raises
    ValidationError in case of error.

    """
    if isinstance(qty, str):
        try:
            qty = int(qty)
        except ValueError as e:
            raise ValidationError('"%s" is not a valid quantity.' % qty) from e
    if qty < 0:
        raise ValidationError(
            "Quantity %d is invalid (must be non-negative)." % qty
        )
    return qty


def clean_amount(amount, row_num, part_row):
    # pylint: disable=unused-argument
    """Verify that "amount" is a valid currency amount, which must be a
    non-negative number or decimal number string.  Returns the number
    or raises ValidationError in case of error.

    """
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError as e:
            raise ValidationError(
                '"%s" is not a valid amount.' % amount
            ) from e
    if amount < 0.0:
        raise ValidationError(
            "Amount %f is invalid (must be non-negative)." % amount
        )
    return amount


CLEANER = {"part": clean_part, "qty": clean_qty, "amount": clean_amount}


def clean_spreadsheet(spreadsheet, required_columns, add_error):
    """Given uploaded file "spreadsheet", verify that it has the columns
    specified by "required_columns" and return a list containing one
    entry for each data row in the spreadsheet.  Each list entry
    consists of dictionary with a name/value pair for each of the
    required columns.  Extraneous columns are ignored.  Errors that
    abort any further parsing of the spreadsheet are reported by
    raising ValidationError.  Other errors are reported by calls to
    "add_error", which must be a function expecting a ValidationError
    argument.

    """
    contents = spreadsheet.read()
    try:
        # try loading utf-8 decoded contents for CSV files:
        txt = contents.decode("utf-8")
        ds = tablib.Dataset().load(txt)
    except Exception:
        try:
            # try loading binary contents for Excel files:
            ds = tablib.Dataset().load(contents, read_only=False)
        except Exception as e:
            raise ValidationError(
                "failed to load spreadsheet; neither an CSV nor Excel file?"
            ) from e

    have_errors = False

    col_idx = {}  # maps required column to the index in the spreadsheet
    col_name = {}  # maps required column to the name in the spreadsheet
    for idx, name in enumerate(ds.headers):
        if name is None:
            continue
        col = name.lower()
        for required in required_columns:
            if col == required or col in ALTERNATE_NAMES[required]:
                if required in col_idx:
                    add_error(
                        'Multiple columns for "%s" found '
                        '("%s" and "%s")' % (required, col_name[required], col)
                    )
                    have_errors = True
                col_idx[required] = idx
                col_name[required] = col
    for required in required_columns:
        if required not in col_idx:
            add_error(
                ValidationError(
                    'Column "%s" missing.  It may also be called one of: %s.'
                    % (required, ", ".join(ALTERNATE_NAMES[required]))
                )
            )
            have_errors = True

    if have_errors:
        return []
    if not ds:
        raise ValidationError("At least one row of data required.")

    rows = []
    part_row = {}
    row_num = 2  # 2 because row 1 is the header row
    for row in ds:
        clean = {}
        row_empty = True
        for required in required_columns:
            raw_val = row[col_idx[required]]
            if raw_val is not None:
                row_empty = False
                break
        if row_empty:
            continue

        for required in required_columns:
            raw_val = row[col_idx[required]]
            if raw_val is None:
                add_error(
                    'Row %d, column "%s" has no value.'
                    % (row_num, col_name[required])
                )
                continue
            try:
                val = CLEANER[required](raw_val, row_num, part_row)
            except ValidationError as e:
                add_error(e)
            else:
                clean[required] = val

        if (
            "amount" in clean
            and "qty" in clean
            and col_name["amount"] == "price"
        ):
            # convert from per-piece price to total amount:
            clean["amount"] = clean["amount"] * clean["qty"]

        rows.append(clean)
        row_num += 1
    return rows
