def compute_grid_layout(nrow = 1, ncol = 1):
    """
    Computes the layout of a grid based on the number of rows and columns.
    """
    layout = []
    for indx in range(nrow):
        row_layout = []
        for indx in range(ncol):
            row_layout.append({})
        layout.append(row_layout)
    return layout