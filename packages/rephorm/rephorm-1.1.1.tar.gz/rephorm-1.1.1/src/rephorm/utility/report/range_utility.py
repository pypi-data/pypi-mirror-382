import warnings

def _get_max_span(obj, span, comparison):

    if not hasattr(comparison, "frequency"):
        return span

    obj_frequency = (
        getattr(obj.settings.span, "frequency", None)
        or getattr(obj.settings, "frequency", None)
    )

    if comparison.frequency is not None and obj_frequency is not None:
        if comparison.frequency != obj_frequency:
            warnings.warn("Multiple frequencies are not allowed.")
            return span

    if span is None:
        span = comparison
        return span

    start = min(span.start, comparison.start)
    end = max(span.end, comparison.end)

    return start >> end

# Method for Table and Chart
def get_span(obj):
    span = None

    def resolve_span_recursive(node, current_span):
        if hasattr(node, "settings") and hasattr(node.settings, "span") and hasattr(node, "data") and hasattr(node.data, "span"):

            comparison = node.settings.span.resolve(node.data.span)
            current_span = _get_max_span(obj, current_span, comparison)

        if hasattr(node, "CHILDREN"):
            for child in node.CHILDREN:
                current_span = resolve_span_recursive(child, current_span)

        return current_span

    span = resolve_span_recursive(obj, span)

    # if hasattr(obj, "settings") and hasattr(obj.settings, "span"):
    if ".start" in str(obj.settings.span.start):
        obj.settings.span = span.start >> obj.settings.span.end

    if ".end" in str(obj.settings.span.end):
        obj.settings.span = obj.settings.span.start >> span.end

    if obj.settings.span.start > obj.settings.span.end:
        raise Exception(
            f"Invalid highlight range for {obj.__class__.__name__}: Start date ({obj.settings.span.start}) is after the end date ({obj.settings.span.end}). "
            f"Please provide a highlight range where start precedes the end. "
            f"Current range: {obj.settings.span.start} >> {obj.settings.span.end}"
        )

    return obj.settings.span

# Method for Table and Chart
def get_highlight(obj):

    if obj.settings.highlight is None:
        return # Just exit the function

    span = get_span(obj)

    if span is None:
        raise Exception(f"{obj.__class__.__name__} span is missing.")

    start = obj.settings.highlight.start

    if ".start" in str(start):
        start = span.start

    if start not in span:
        # We just warn user. But this start not in span is not a problem, because we return min/max
        # It is just for user to know of issue
        warnings.warn(f"{obj.__class__.__name__} highlight start is outside the selected span.", UserWarning)

    end = obj.settings.highlight.end

    if ".end" in str(end):
        end = span.end

    if start > end:
        raise Exception(
            f"Invalid highlight range for {obj.__class__.__name__}: Start date ({start}) is after the end date ({end}). "
            f"Please provide a highlight range where start precedes the end. "
            f"Current range: {start} >> {end}"
        )

    return max(start, span.start), min(end, span.end)