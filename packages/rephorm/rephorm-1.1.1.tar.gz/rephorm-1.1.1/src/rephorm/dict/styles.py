DEFAULT_FONT_FAMILY = "Helvetica" # This was agreed upon

def default_styles(font_family=DEFAULT_FONT_FAMILY):
    return {
        "table": {
            "highlight_color": "#E0E0E0",
            "title": {
                "font_style": "B",
                "font_family": font_family,
                "font_color": "#000000",
                "font_size": 13,
            },
            "heading": {
                "font_style": "",
                "font_family": font_family,
                "font_color": "#000000",
                "font_size": 10,
                "highlight_color": "#E0E0E0",
            },
            "series": {
                "font_style": "",
                "font_family": font_family,
                "font_color": "#000000",
                "font_size": 10,
                "highlight_color": "#E0E0E0",
            },
            "section": {
                "font_style": "",
                "font_family": font_family,
                "font_color": "#000000",
                "font_size": 10,
                "highlight_color": "#E0E0E0",
            }
        },
        "text": {
            "font_style": "",
            "font_family": font_family,
            "font_size": 10,
            "title": {
                "font_style": "B",
                "font_family": font_family,
                "font_size": 16,
            }
        },
        "footnotes": {
            "font_size": 8,
            "font_color": "#000000",
            "font_style": "",
            "font_family": font_family,
        },
        "grid": {
            "title": {
                "font_style": "B",
                "font_family": font_family,
                "font_color": "#000000",
                "font_size": 13,
            },
        },
        "chapter": {
            "title": {
                "font_style": "B",
                "font_family": font_family,
                "font_color": "#000000",
                "font_size": 16,
            },
            "font_style": "",
            "font_family": font_family,
            "font_size": 11,
        },
        "chart": {
            "highlight_color": "rgba(0, 0, 0, 0.12)",
            "grid_color": "lightgrey",
            "bg_color": "rgba(0, 255, 0, 0)",
            "chart_border_color": "#000000",
            "line_styles_order": [
                "solid"
            ],
            "line_color_order": [
                "rgb(31, 119, 180)",
                "rgb(255, 127, 14)",
                "rgb(44, 160, 44)",
                "rgb(214, 39, 40)",
                "rgb(148, 103, 189)",
                "rgb(140, 86, 75)",
                "rgb(227, 119, 194)",
                "rgb(127, 127, 127)",
                "rgb(188, 189, 34)",
                "rgb(23, 190, 207)"
            ],
            "bar_color_order": [
                "rgb(31, 119, 180)",
                "rgb(255, 127, 14)",
                "rgb(44, 160, 44)",
                "rgb(214, 39, 40)",
                "rgb(148, 103, 189)",
                "rgb(140, 86, 75)",
                "rgb(227, 119, 194)",
                "rgb(127, 127, 127)",
                "rgb(188, 189, 34)",
                "rgb(23, 190, 207)"
            ],
            "line_width_order": [1],
            "series": {
                "bar_edge_color": "black",
                "bar_face_color": None,
                "bar_edge_width": 1.0,
                "line_width": None,
                "line_style": None,
                "line_color": None,
                "marker_color": "#46b336",
                "marker_size": 1,
                "marker_width": 1,
            },
            "legend": {
                "border_width": 0,
                "bg_color": "rgba(255, 255, 255, 0)",
                "font_style": "",
                "font_family": font_family,
                "font_color": "#000000",
                "font_size": 8,
            },
            "title": {
                "font_style": "",
                "font_family": font_family,
                "font_color": "#000000",
                "font_size": 11,
            },
            "x_axis": {
                "ticks": {
                    "font_size": 10,
                    "font_color": "#000000",
                    "font_family": font_family,
                },
                "label": {
                    "font_size": 10,
                    "font_color": "#000000",
                    "font_family": font_family,
                }
            },
            "y_axis": {
                "ticks": {
                    "font_size": 10,
                    "font_color": "#000000",
                    "font_family": font_family,
                },
                "label": {
                    "font_size": 10,
                    "font_color": "#000000",
                    "font_family": font_family,
                },
            },
            "y_axis2": {
                "ticks": {
                    "font_size": 10,
                    "font_color": "#000000",
                    "font_family": font_family,

                },
                "label": {
                    "font_size": 10,
                    "font_color": "#000000",
                    "font_family": font_family,
                }
            },
        },
        "report": {
            # only front page title
            "title": {
                "font_style": "B",
                "font_size": 25,
                "font_color": "#000000",
                "font_family": font_family,
            },
            "subtitle": {
                "font_style": "B",
                "font_size": 21,
                "font_color": "#000000",
                "font_family": font_family,
            },
            "abstract": {
                "height": 50,
                "font_size": 10,
                "font_color": "#000000",
                "font_family": font_family,
            },
            "footer": {
                "height": 15,
                "top_margin": 5,
                "top_padding": 5,
            },
            "header": {
                "height": 20,
                "bottom_margin": 5,
            },
            "font_style": "",
            "font_family": font_family,
            "font_color": "#000000",
            "page_margin_top": 10,
            "page_margin_right": 40,
            "page_margin_bottom": 15,
            "page_margin_left": 40,
            #Todo: Find a better name for it.
            "title_bottom_padding": 10,
            "logo_height": 15,
        }
    }