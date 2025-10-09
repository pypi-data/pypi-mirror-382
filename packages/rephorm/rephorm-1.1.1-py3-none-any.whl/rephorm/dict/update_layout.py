from rephorm.dict.legend_positions import legend_positions
from rephorm.utility.report.resolve_color import resolve_color

def update_layout(title, settings, figure, y_range = None):

    # Todo: extract this, but basically this is how to get title style in plotly for chart or for label too (I guess same way for label)
    font_style = settings.styles["chart"]["title"]["font_style"]
    if font_style == "B":
        formatted_title = f"<b>{title}</b>"
    elif font_style == "I":
        formatted_title = f"<i>{title}</i>"
    elif font_style == "BI":
        formatted_title = f"<b><i>{title}</i></b>"
    else:
        formatted_title = title

    layout = {
                "title": {
                    "text": formatted_title,
                    "yref": "container",  # stop overlaps with plot area
                    "yanchor": "top", # align to top
                    "x": 0.5,
                    "automargin": True,  # adjust margins
                    "pad": {"b": 5},  # Fine control
                    "font_size": settings.styles["chart"]["title"]["font_size"],
                    "font_family": settings.styles["chart"]["title"]["font_family"],
                    "font_color": resolve_color(settings.styles["chart"]["title"]["font_color"]),
                },
                "plot_bgcolor": resolve_color(settings.styles["chart"]["bg_color"]),
                # paper_bgcolor is kinda useless for us now,
                # because of PDF image choice it will not support transparent bg
                # https://github.com/plotly/Kaleido/issues/91
                "paper_bgcolor": 'hsla(0, 100%, 50%, 0)',
                "margin": {"l": 0,
                           "r": 0,
                           "t": 5,
                           "b": 0
                           },
                "xaxis": {
                    # TODO: Later on introduce this parameter, to set number of ticks manually.
                    # "nticks": settings.styles["chart"]["x_axis"]["ticks"]["nticks"],
                    "showgrid": settings.show_grid if settings.show_grid else True,
                    "gridcolor": resolve_color(settings.styles["chart"]["grid_color"]),
                    "mirror": settings.axis_border,
                    "linecolor": resolve_color(settings.styles["chart"]["chart_border_color"]),
                    "showline": True,
                    "ticks": "inside",
                    "tickcolor": "black",
                    "linewidth": 1,
                    "tickwidth": 1,
                    "griddash": "dot",
                    "gridwidth": 1,
                    "tickfont": {"size": settings.styles["chart"]["x_axis"]["ticks"]["font_size"],
                                 "family": settings.styles["chart"]["x_axis"]["ticks"]["font_family"],
                                 "color": settings.styles["chart"]["y_axis"]["ticks"]["font_color"]},
                    "title": {
                        "text": settings.xaxis_title,
                        "font": {
                            "size": settings.styles["chart"]["x_axis"]["label"]["font_size"],
                            "family": settings.styles["chart"]["x_axis"]["label"]["font_family"]}},
                },
                "yaxis": {
                    "zeroline": settings.zeroline if hasattr(settings, 'zeroline') else True,
                    "showgrid": settings.show_grid if hasattr(settings, 'show_grid') else True,
                    "gridcolor": resolve_color(settings.styles["chart"]["grid_color"]),
                    "mirror": settings.axis_border,
                    "linecolor": resolve_color(settings.styles["chart"]["chart_border_color"]),
                    "showline": True,
                    "ticks": "inside",
                    "tickcolor": "black",
                    "linewidth": 1,
                    "tickwidth": 1,
                    "griddash": "dot",
                    "gridwidth": 1,
                    "range": y_range,
                    "tickfont": {"size": settings.styles["chart"]["y_axis"]["ticks"]["font_size"],
                                 "family": settings.styles["chart"]["y_axis"]["ticks"]["font_family"],
                                 "color": settings.styles["chart"]["y_axis"]["ticks"]["font_color"]},
                    "title": {
                        "text": settings.yaxis_title,
                        "font": {
                            "size": settings.styles["chart"]["y_axis"]["label"]["font_size"],
                            "family": settings.styles["chart"]["y_axis"]["label"]["font_family"]}},
                },
                "yaxis2": {
                    "overlaying": "y",
                    "side": "right",
                    "linecolor": resolve_color(settings.styles["chart"]["chart_border_color"]),
                    "showline": True,
                    "ticks": "inside",
                    "tickcolor": "black",
                    "linewidth": 1,
                    "tickwidth": 1,
                    "range": y_range,
                    "tickfont": {"size": settings.styles["chart"]["y_axis2"]["ticks"]["font_size"],
                                 "family": settings.styles["chart"]["y_axis2"]["ticks"]["font_family"],
                                 "color": settings.styles["chart"]["y_axis2"]["ticks"]["font_color"]},
                    "title": {
                        "text": settings.yaxis2_title,
                        "font": {
                            "size": settings.styles["chart"]["y_axis2"]["label"]["font_size"],
                            "family": settings.styles["chart"]["y_axis2"]["label"]["font_family"]}},
                },
                "legend": {
                    "font": {
                        "size": settings.styles["chart"]["legend"]["font_size"],
                        "family": settings.styles["chart"]["legend"]["font_family"],
                        "color": resolve_color(settings.styles["chart"]["legend"]["font_color"])
                    },
                    "orientation": settings.legend_orientation.lower(),
                    "x": legend_positions.get(settings.legend_position.upper()).get("x"),
                    "y": legend_positions.get(settings.legend_position.upper()).get("y"),
                    "xanchor": legend_positions.get(settings.legend_position.upper()).get("xanchor"),
                    "yanchor": legend_positions.get(settings.legend_position.upper()).get("yanchor"),
                    "borderwidth": settings.styles["chart"]["legend"]["border_width"],
                    "yref": legend_positions.get(settings.legend_position.upper()).get("yref"),
                    "xref": legend_positions.get(settings.legend_position.upper()).get("xref"),
                    "bgcolor": resolve_color(settings.styles["chart"]["legend"]["bg_color"]),
                }
            }

    # Update conditionally only if the user explicitly specifies 'ncols'.
    legend_ncol = settings.legend_ncol
    if bool(legend_ncol):
        figure.layout.legend["entrywidth"] = 1 / legend_ncol
        figure.layout.legend["entrywidthmode"] = "fraction"

    figure.update_layout(layout)

