import irispie as ir
import re

from rephorm.utility.report.range_utility import get_highlight, get_span


def get_table_highlight(table):

    start, end = get_highlight(table)
    span = get_span(table)
    skip_cols = 1
    if table.settings.show_units:
        skip_cols += 1

    length = len(span.start >> end)

    cols = range(list(span).index(start) + skip_cols, length + skip_cols)
    cols = list(cols)

    return cols

def prepare_row(
        series: ir.Series = None,
        span: ir.Span = None,
        title: str = "",
        unit: str = "",
        show_units: bool = None,
        decimal_precision: int = None,
        compare_style: str = None,
        footnote_references = None,
):
    if series is None:
        series_data = ir.Series()
        decimal_precision = 0

    else:
        series_data = series

    if isinstance(series_data, ir.Series):
        series_data = series_data[span].flatten().tolist()
    #if isinstance(series_data, TableSeries):
    else:
        series_data = series_data.data[span].flatten().tolist()


    if span is None:
        raise Exception("Span is missing.")

    options = {
        "diff": ("[", "]"),
        "pct": ("(", ")"),
    }

    left, right = options.get(
        compare_style,
        ("", ""),
    )

    # descriptions = [f"{spacer}{title}{footnote_references.get(i, ' ')}" for i in range(len(series_data))]

    descriptions = [f"{title}"]

    if show_units:
        descriptions = descriptions + [unit]


    pattern = r"\bnan\b|\[nan\]|\(nan\)"

    row = descriptions + [re.sub(pattern, "", f"{left}{x:.{decimal_precision}f}{right}") for x in series_data]

    return row