import copy

from rephorm.dict.styles import default_styles, DEFAULT_FONT_FAMILY
from rephorm.object_params.settings import object_params
from rephorm.utility.merge.chart_properties_manager import get_bar_color, get_line_color, \
    get_line_style, update_chart_properties, get_line_width
from rephorm.utility.merge.merge_styles import update_nested_structure, create_nested_structure


def merge_settings(obj, params):
    """
    obj - The current object (e.g., Report, Chapter, etc.)
    params - A dictionary of parameters to propagate | That is report. settings
    """
    #Todo: Known issue: if you set report.font_size on level of chart,
    # it will not recalculate font sizes for chart and it's children.
    # ...
    # This is because at that point of iteration there is local params dictionary,
    # and we update it with what comes from children. To update reference
    # font format when children gets report.font_size parameter (reference parameters)
    # we would need to reinitialize default dict with those values from the children,
    # but we cant do it because we would loose the state of the local params,
    # which already have some important settings preset for us.
    # ...

    local_params = copy.deepcopy(params)

    parent_styles = create_nested_structure(obj.__class__.__name__, local_params.get("styles", {}))
    parent_font_family = parent_styles.get("report", {}).get("font_family", DEFAULT_FONT_FAMILY)

    object_styles = create_nested_structure(obj.__class__.__name__, obj.settings.__dict__.get("styles", {}))
    obj_font_family = object_styles.get("font_family", parent_font_family)

    # We update the default styles with styles coming from the previous parent (local_params["styles"]),
    # preserving inherited values. This avoids overwriting/resetting them as before (line 40),
    # where default_styles was directly assigned to local_params["styles"].

    local_params["styles"] = update_nested_structure(
        default_styles(obj_font_family),
        create_nested_structure(obj.__class__.__name__,local_params.get("styles", {}))
    )

    for key in object_params.keys():
        # Check if the key exists in params; if not, use its default value
        parent_value = local_params.get(key, None)
        # Check if obj.settings already has this key set
        if hasattr(obj.settings, key) and getattr(obj.settings, key) is not None:
            current_obj_value = getattr(obj.settings, key)

            if key == "styles":
                current_obj_value = update_nested_structure(parent_value, create_nested_structure(obj.__class__.__name__, current_obj_value))

            setattr(obj.settings, key, current_obj_value)
            local_params[key] = current_obj_value

        elif parent_value is not None:
            ultimate_owners = object_params.get(key, {}).get("ultimates", [])
            if type(obj).__name__ in ultimate_owners:
                setattr(obj.settings, key, parent_value)

        # If no value is set yet, use the default from ultimate_setting_owner
        elif getattr(obj.settings, key, None) is None:
            ultimate_owners = object_params.get(key, {}).get("ultimates", [])
            if type(obj).__name__ in ultimate_owners:
                if key == "styles":
                    setattr(obj.settings, key, getattr(local_params, key))
                else:
                    setattr(obj.settings, key, object_params[key].get("default_value", None))

    if obj.__class__.__name__ == "Chart":
        structured_styles = create_nested_structure(obj.__class__.__name__, obj.settings.styles) \
            if hasattr(obj.settings, "styles") \
            else {}
        update_chart_properties(structured_styles.get("chart", {}).get("bar_color_order", None),
                                structured_styles.get("chart", {}).get("line_color_order", None),
                                structured_styles.get("chart", {}).get("line_styles_order", None),
                                structured_styles.get("chart", {}).get("line_width_order", None),
                                )

    if hasattr(obj, "CHILDREN") and isinstance(obj.CHILDREN, list):
        list_of_obj = [obj.CHILDREN[-1]] if obj.__class__.__name__ == "Report" and obj.CHILDREN else obj.CHILDREN
        for child in list_of_obj:
            if hasattr(child, "settings"):
                merge_settings(child, local_params)
                handle_object_properties(child, child.settings.styles)

"""
This function process final styles dictionary and assigns colors to chartSeries based on series type, using predefined color order.
If the color is not user-defined, it assigns the next color from the global color order. (Non user defined colors coming as "None" by default)

When we call this function we do not need to ensure that the necessary dict structure
exists or that keys are present, because who calls this function should already have it set.
This function should not be called on styles dict, that was not processed (missing keys/values)
or that is not properly structured (dict that is flat / or not following the correct order)
"""

# TODO: Implement multivariate series support with consistent color assignment
#  Current Issue:
#  When creating a single series object that contains multiple data components (multivariate),
#  the color assignment system only applies a single color to the entire series.
#  Implementation:
#  Here we would detect if the series that is coming are multivariate or single,
#  basically check if single, assign color, else create an array for the length of
#  data columns in the series, populate it with get_bar_color() until it's full,
#  and pass it to styles as "bar_face_color"

def handle_object_properties(obj, merged_styles):

    if obj.__class__.__name__ == "ChartSeries":

        is_multivariate = obj.data.num_variants > 1

        series_type = getattr(obj.settings, "series_type")
        series_styles = merged_styles["chart"]["series"]

        def assign_style(key, generator_func):
            if key not in series_styles or series_styles[key] is None:
                if is_multivariate:
                    series_styles[key] = [generator_func() for _ in range(obj.data.num_variants)]
                else:
                    series_styles[key] = generator_func()

        if series_type in (
            "bar", "contribution_bar", "barcon", "conbar", "bar_color_stack",
            "bar_group", "bar_overlay", "bar_relative"
        ):
            assign_style("bar_face_color", get_bar_color)
        else:
            assign_style("line_color", get_line_color)
            assign_style("line_style", get_line_style)
            # line width: typically same for all?
            assign_style("line_width", get_line_width)


