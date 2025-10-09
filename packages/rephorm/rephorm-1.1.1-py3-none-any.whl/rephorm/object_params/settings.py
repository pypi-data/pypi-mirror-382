from typing import Dict
import irispie as ir

from rephorm.dict.styles import default_styles

"""
    This Dictionary defines all possible parameters that can be applied to any object within the report.
    
    - default_value - default value of the parameter
    - type - for type checking | if type is None, then it is not being checked ("useful" in case of Complex data Types)
    - ultimates - list of objects that should get/receive this parameter
"""

object_params = {
    "span": {
        "default_value": ir.start >> ir.end,
        "type": ir.Span,
        "ultimates": ["Chart", "Table", "ChartSeries", "TableSeries"],
    },
    "highlight" : {
        "default_value": None,
        "type": ir.Span,
        "ultimates": ["Chart", "Table", "TableSection", "TableSeries"],
    },
    "show_legend" : {
        "default_value": True,
        "type": bool,
        "ultimates": ["ChartSeries"],
    },
    "yaxis": {
        "default_value": "left",
        "type": str,
        "possible_values":
                    {"left", "right"},
        "ultimates": ["ChartSeries"],
    },
    "update_traces" : { # todo: check if this is used
        "default_value": None,
        "type": Dict,
        "ultimates": ["ChartSeries"],
    },
    "show_grid" : {
        "default_value": True,
        "type": bool,
        "ultimates": ["Chart"],
    },
    "axis_border" : {
        "default_value": False,
        "type": bool,
        "ultimates": ["Chart"],
    },
    "xaxis_title" : {
        "default_value": "",
        "type": str,
        "ultimates": ["Chart"],
    },
    "yaxis_title" : {
        "default_value": "",
        "type": str,
        "ultimates": ["Chart"],
    },
    "yaxis2_title" : {
        "default_value": "",
        "type": str,
        "ultimates": ["Chart"],
    },
    "legend_orientation" : {
        "default_value": "h",
        "type": str,
        "ultimates": ["Chart"],
    },
    "legend_position" : {
        "default_value": "SO",
        "type": str,
        "possible_values":
            {"N", "S", "E", "W",
            "NE", "NW", "SE", "SW",
            "NO", "SO", "EO", "WO",
            "NEO", "NWO", "SEO", "SWO"},
        "ultimates": ["Chart"],
    },
    "ncol" : {
        "default_value": 2,
        "type": int,
        "ultimates": ["Grid"],
    },
    "nrow" : {
        "default_value": 2,
        "type": int,
        "ultimates": ["Grid"],
    },
    "apply_report_layout": {
        "default_value": False,
        "type": bool,
        "ultimates": ["Chart"],
    },
    "layout": {
        "default_value": None,
        "type": None,
        "ultimates": ["Grid"],
    },
    "comparison_series" : {
        "default_value": False,
        "type": bool,
        "ultimates": ["TableSeries"],
    },
    "series_type" : {
        "default_value": "line",
        "type": str,
        "possible_values": {"line", "bar", "contribution_bar", "barcon", "conbar", "bar_stack", "bar_group", "bar_overlay", "bar_relative"},
        "ultimates": ["Chart", "ChartSeries"],
    },
    "markers_mode" : {
        "default_value": "lines",
        "type": str,
        "possible_values": {"lines+markers", "lines", "markers"},
        "ultimates": ["ChartSeries"], # TEST IT: Chart was removed as Chart should not use it in any way
    },
    "legend" : {
        "default_value": None,
        "type": tuple,
        "ultimates": ["Chart", "ChartSeries"],
    },
    "compare_style" : {
        "default_value": "",
        "type": str,
        "ultimates": ["TableSeries"],
    },
    "marker_symbol" : {
        "default_value": "asterisk",
        "type": str,
        "ultimates": ["Chart", "ChartSeries"],
    },
    "orientation" : {
        "default_value": "P",
        "type": str,
        "ultimates": ["Report"],
    },
    "unit" : {
        "default_value": "pt",
        "type": str,
        "ultimates": ["Report"],
    },
    "format" : {
        "default_value": "A4",
        "type": str,
        "ultimates": ["Report"],
    },
    "decimal_precision" : {
        "default_value": 1,
        "type": int,
        "ultimates": ["TableSeries"],
    },
    "show_units" : {
        "default_value": True,
        "type": bool,
        "ultimates": ["TableSection", "Table"],
    },
    "zeroline" : {
        "default_value": False,
        "type": bool,
        "ultimates": ["Chart"],
    },
    "legend_ncol" : {
        "default_value": None,
        "type": int,
        "ultimates": ["Chart"],
    },
    "frequency" : {
        "default_value": None,
        "type": None, #Cant check this one
        "ultimates": ["Table"],
    },
    "styles": {
        "default_value": default_styles(),
        "type": None, # TODO: change to Dict later on
        "ultimates": ["Report", "Chapter", "TableSection", "ChartSeries", "TableSeries", "Table", "Chart", "Grid", "Text"],
    },
    "logo": {
        "default_value": "",
        "type": str,
        "ultimates": ["Report"],
    }
}