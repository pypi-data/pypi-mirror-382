def mm_to_px(mm, ppi):
    """Converts millimeters to pixels given the pixels per inch (PPI)."""
    return (mm / 25.4) * ppi
    # return mm * 3.78

# Todo: make generic function that converts report units (whatever we get) to respective ones we need / to px


#pt is what overlay_pdfs uses
def mm_to_pt(mm):
    """Converts millimeters to points."""
    return mm * 2.83465