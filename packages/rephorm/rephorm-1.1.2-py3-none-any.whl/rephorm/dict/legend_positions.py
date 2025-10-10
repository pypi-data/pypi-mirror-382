legend_positions = {
    # Center positions
    "C": {  # Center (Inline)
        "x": 0.5,
        "y": 0.5,
        "xanchor": "center",
        "yanchor": "middle",
        "yref": "paper"
    },
    # Inside positions
    "N": {  # North (Top-Center)
        "x": 0.5,
        "y": 1,
        "xanchor": "center",
        "yanchor": "top",
        "yref": "paper"
    },
    "S": {  # South (Bottom-Center)
        "x": 0.5,
        "y": 0,
        "xanchor": "center",
        "yanchor": "bottom",
        "yref": "paper"
    },
    "E": {  # East (Right-Center)
        "x": 1,
        "y": 0.5,
        "xanchor": "right",
        "yanchor": "middle",
        "yref": "paper"
    },
    "W": {  # West (Left-Center)
        "x": 0,
        "y": 0.5,
        "xanchor": "left",
        "yanchor": "middle",
        "yref": "paper"
    },
    "NE": {  # North-East (Top-Right)
        "x": 1,
        "y": 1,
        "xanchor": "right",
        "yanchor": "top",
        "yref": "paper"
    },
    "NW": {  # North-West (Top-Left)
        "x": 0,
        "y": 1,
        "xanchor": "left",
        "yanchor": "top",
        "yref": "paper"
    },
    "SE": {  # South-East (Bottom-Right)
        "x": 1,
        "y": 0,
        "xanchor": "right",
        "yanchor": "bottom",
        "yref": "paper"
    },
    "SW": {  # South-West (Bottom-Left)
        "x": 0,
        "y": 0,
        "xanchor": "left",
        "yanchor": "bottom",
        "yref": "paper"
    },

    # Outside positions
    "NO": {  # North-Outside (Above Top-Center)
        "x": 0.5,
        "y": 0.89,
        "xanchor": "center",
        "yanchor": "top",
        "yref": "container"
    },
    "SO": {  # South-Outside (Below Bottom-Center)
        "x": 0.5,
        # "y": 0,
        "xanchor": "center",
        # "yanchor": "bottom",
        # "yref": "container"
    },
    # South-Outside (ADJUSTED) Need proper testing
    # TODO: Consider changing back to "paper" and off-setting POS using negatives.
    # "SO": {
    #     "x": 0.5,
    #     "y": -0.15,
    #     "xanchor": "center",
    #     "yanchor": "top",
    #     "yref": "paper"
    # },
    "EO": {  # East-Outside (Right of Chart)
        "x": 0.8,
        "y": 0.5,
        "xanchor": "left",
        "yanchor": "middle",
        "yref": "container",
        "xref": "container"
    },
    "WO": {  # West-Outside (Left of Chart)
        "x": 0,
        "y": 0.5,
        "xanchor": "left",
        "yanchor": "middle",
        "yref": "container",
        "xref": "container"
    },
    "NEO": {  # North-East-Outside (Above Top-Right)
        "x": 1,
        "y": -0.1,
        "xanchor": "right",
        "yanchor": "top",
        "yref": "container"
    },
    "NWO": {  # North-West-Outside (Above Top-Left)
        "x": 0,
        "y": -0.1,
        "xanchor": "left",
        "yanchor": "top",
        "yref": "container"
    },
    "SEO": {
    "x": 1,
    "y": 0,
    "xanchor": "right",
    "yanchor": "bottom",
    "yref": "container",
    },
    "SWO": {  # South-West-Outside (Below Bottom-Left)
        "x": 0,
        "y": 0,
        "xanchor": "left",
        "yanchor": "bottom",
        "yref": "container"
    }
}
