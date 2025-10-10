"""
Prepare shared (base-level) trace update settings for Plotly plots.

This function returns general trace configuration that applies uniformly
across all traces — where no fine-grained (per-trace) control is needed
between multivariate and single-series cases.

"""
def update_base_traces(settings):
    yaxis = getattr(settings, "yaxis", "left")
    if settings.series_type == "line":
         update_traces = {
            "mode": settings.markers_mode,
            "marker": {
                "symbol": settings.marker_symbol,
                "size": settings.styles["chart"]["series"]["marker_size"],
                "line.width": settings.styles["chart"]["series"]["marker_width"],
                "line.color": settings.styles["chart"]["series"]["marker_color"],
                "color": settings.styles["chart"]["series"]["marker_color"],
            },
            "marker.color": settings.styles["chart"]["series"]["marker_color"],
            "yaxis": "y2" if yaxis == "right" else "y1"
            }
    elif "bar" in settings.series_type.lower():
         update_traces = {
            "type": "bar",
            "marker": {
                "line.color": settings.styles["chart"]["series"]["bar_edge_color"],
                "line.width": settings.styles["chart"]["series"]["bar_edge_width"],
            },
              "yaxis": "y2" if yaxis == "right" else "y1"
        }
    else: update_traces = {}

    return update_traces

def apply_per_trace_styles(
    fig,
    line_colors=None,
    line_widths=None,
    line_styles=None,
    bar_colors=None,
    num_variants=None,
):
    """
    Apply per-trace styling to a Plotly figure.

    Supports passing a single value or a list for each style type.
    """

    if not fig.data:
        return

    traces = fig.data[-num_variants:]

    for idx, trace in enumerate(traces):

        if trace.type == 'scatter':

            color = get_value(line_colors, idx)
            if color:
                trace.line.color = color

            width = get_value(line_widths, idx)
            if width:
                trace.line.width = width

            dash = get_value(line_styles, idx)
            if dash:
                trace.line.dash = dash

        elif trace.type == 'bar':
            color = get_value(bar_colors, idx)
            if color:
                trace.marker.color = color


def get_value(value, i):
    """
    Function to retrieve the appropriate style value for the n-th trace.
    Mainly used for apply_per_trace_styles()

    :param value: Either a single value or a list of values.
    :param i: trace index
    :return: value (str)
    """
    if isinstance(value, list):
        # If a list, return value based on trace index, and cycle
        return value[i % len(value)]
    else: return value  # bcs single value can also be passed
