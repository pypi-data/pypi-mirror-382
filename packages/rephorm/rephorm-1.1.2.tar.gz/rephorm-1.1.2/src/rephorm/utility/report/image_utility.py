# Todo: Consider making part of ChartMapper method (that should be implemented from interface) | Rename to render_chart
import plotly.io as pio
pio.kaleido.scope.mathjax = None

def to_image(series, image_format="pdf", width=None, height=None):
    """
    Converts a chart to an image in the specified format and dimensions.
    """
    try:
        return series.to_image(format=image_format, width=width, height=height)

    except Exception as e:
        print(f"Error generating image from chart: {e}")
        return None