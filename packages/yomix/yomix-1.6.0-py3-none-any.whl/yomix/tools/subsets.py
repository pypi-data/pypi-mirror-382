# """
# Provides tools for defining and managing data subsets.

# This module contains the `subset_buttons` function, which creates the necessary
# Bokeh widgets to allow users to interactively select and define two distinct
# groups of data points, labeled "Subset A" and "Subset B". It handles both the
# assignment of points to these subsets and their visual highlighting on the main
# scatter plot.
# """

import bokeh.models


def subset_buttons(
    points_bokeh_plot: bokeh.plotting.figure,
    source_rotmatrix_etc: bokeh.models.ColumnDataSource,
    bt_slider_range: bokeh.models.RangeSlider,
) -> tuple[
    bokeh.models.Button,
    bokeh.models.Toggle,
    bokeh.models.CheckboxGroup,
    bokeh.models.Button,
    bokeh.models.Toggle,
    bokeh.models.CheckboxGroup,
    bokeh.models.Button,
    bokeh.models.Button,
    bokeh.models.Button,
    bokeh.models.Button,
]:
    """
    Generate toggle switches and buttons for setting, highlighting, and selecting
    subsets of samples directly within from the scatterplot.

    Args:
        points_bokeh_plot (bokeh.plotting.figure):
            The main Bokeh scatter plot figure.

        source_rotmatrix_etc (bokeh.models.ColumnDataSource):
            Data source for tracking points' positions after rotations in the scatterplot.

        bt_slider_range (bokeh.models.RangeSlider):
            Slider for filtering samples based on a selected feature's value. It is
            passed here so its value can be reset when the user clears a selection.

    Returns:
        Tuple containing all the created Bokeh widgets so they can be added
            to the main application layout.

            - **bt_A** (:class:`bokeh.models.Button`): Button to assign the current selection to Subset A.
            - **toggle_A** (:class:`bokeh.models.Toggle`): Toggle to turn the visual
              highlighting of Subset A on or off.
            - **hidden_checkbox_A** (:class:`bokeh.models.CheckboxGroup`): Hidden widget storing Subset A samples indices.
            - **bt_B** (:class:`bokeh.models.Button`): Button to assign the current
              selection to Subset B.
            - **toggle_B** (:class:`bokeh.models.Toggle`): Toggle to turn the visual
              highlighting of Subset B on or off.
            - **hidden_checkbox_B** (:class:`bokeh.models.CheckboxGroup`): Hidden widget storing Subset B samples indices..
            - **bt_AplusB** (:class:`bokeh.models.Button`): Button to select the
              union of Subset A and Subset B.
            - **bt_nothing** (:class:`bokeh.models.Button`): Button to clear the
              current selection.
            - **bt_selectA** (:class:`bokeh.models.Button`): Button to select all
              samples from Subset A.
            - **bt_selectB** (:class:`bokeh.models.Button`): Button to select all
              samples from Subset B.
    """  # noqa

    source = points_bokeh_plot.select(dict(name="scatterplot"))[0].data_source
    button_width = 112
    # big_button_width = 235

    toggle_A = bokeh.models.Toggle(
        label="Highlight A: ON", width=button_width, active=True
    )
    toggle_B = bokeh.models.Toggle(
        label="Highlight B: ON", width=button_width, active=True
    )

    hidden_checkbox_A = bokeh.models.CheckboxGroup(
        labels=["0"] * len(source.data["name"]), active=[]
    )

    hidden_checkbox_B = bokeh.models.CheckboxGroup(
        labels=["0"] * len(source.data["name"]), active=[]
    )

    size_redef_code = """
        point_s[i] = point_s_ref[i] * size_coef[0] * (
            2.5 * Math.max(hA[i], hB[i]) + 1.0);
        line_c[i] = -1. + hA[i] * 0.25 + hB[i] * 0.90;
        line_w[i] = point_s_ref[i] * size_coef[0] * 0.85 * Math.max(
            hA[i], hB[i]);
    """

    toggle_A.js_on_change(
        "active",
        bokeh.models.CustomJS(
            args=dict(source=source, source_rotmatrix_etc=source_rotmatrix_etc),
            code="""
        const data = source.data;
        const data_rotmatrix_etc = source_rotmatrix_etc.data;
        const hA = data['highlighted_A'];
        const hB = data['highlighted_B'];
        const sA = data['subset_A'];
        const point_s = data['point_size'];
        const point_s_ref = data['point_size_ref'];
        const line_c = data['line_color'];
        const line_w = data['line_width'];
        const size_coef = data_rotmatrix_etc['size_coef'];
        if (this.active) {
            this.label = 'Highlight A: ON';
            for (let i = 0; i < hA.length; i++) {
                hA[i] = sA[i];"""
            + size_redef_code
            + """
            }
        } else {
            this.label = 'Highlight A: OFF';
            for (let i = 0; i < hA.length; i++) {
                hA[i] = 0.;"""
            + size_redef_code
            + """
            }
        }
        source.change.emit();
    """,
        ),
    )
    toggle_B.js_on_change(
        "active",
        bokeh.models.CustomJS(
            args=dict(source=source, source_rotmatrix_etc=source_rotmatrix_etc),
            code="""
        const data = source.data;
        const data_rotmatrix_etc = source_rotmatrix_etc.data;
        const hB = data['highlighted_B'];
        const hA = data['highlighted_A'];
        const sB = data['subset_B'];
        const point_s = data['point_size'];
        const point_s_ref = data['point_size_ref'];
        const line_c = data['line_color'];
        const line_w = data['line_width'];
        const size_coef = data_rotmatrix_etc['size_coef'];
        if (this.active) {
            this.label = 'Highlight B: ON';
            for (let i = 0; i < hB.length; i++) {
                hB[i] = sB[i];"""
            + size_redef_code
            + """
            }
        } else {
            this.label = 'Highlight B: OFF';
            for (let i = 0; i < hB.length; i++) {
                hB[i] = 0.;"""
            + size_redef_code
            + """
            }
        }
        source.change.emit();
    """,
        ),
    )

    callback_AB_part_1 = """
        const indices = source.selected.indices;
        const data = source.data;
        const data_rotmatrix_etc = source_rotmatrix_etc.data;
        const point_s = data['point_size'];
        const point_s_ref = data['point_size_ref'];
        const sA = data['subset_A'];
        const sB = data['subset_B'];
        const hA = data['highlighted_A'];
        const hB = data['highlighted_B'];
        const line_c = data['line_color'];
        const line_w = data['line_width'];
        const size_coef = data_rotmatrix_etc['size_coef'];
        for (let i = 0; i < point_s.length; i++) {
    """
    callback_AB_part_2 = (
        size_redef_code
        + """
        }

        source.change.emit();
        toggle.active=true;
    """
    )

    callback_js_A = bokeh.models.CustomJS(
        args=dict(
            source=source,
            source_rotmatrix_etc=source_rotmatrix_etc,
            toggle=toggle_A,
            cbx=hidden_checkbox_A,
            cbx_other=hidden_checkbox_B,
        ),
        code=callback_AB_part_1
        + """
            sA[i] = 0.;
        }
        var t = [];
        var t_remove = [];
        for (let i = 0; i < indices.length; i++) {
            sA[indices[i]] = 1.;
            if (sB[indices[i]] == 1.) {
                t_remove.push(data["index"][indices[i]]);
            }
            sB[indices[i]] = 0.;
            hB[indices[i]] = 0.;
            t.push(data["index"][indices[i]]);
        }
        if (t_remove.length > 0) {
            let difference = cbx_other.active.filter(x => !t_remove.includes(x));
            cbx_other.active = difference;
            cbx_other.change.emit();
        }
        cbx.active = t;
        cbx.change.emit();
        const t_active = toggle.active;
        for (let i = 0; i < point_s.length; i++) {
            if (t_active) {
                hA[i] = sA[i];
            }
        """
        + callback_AB_part_2,
    )

    callback_js_B = bokeh.models.CustomJS(
        args=dict(
            source=source,
            source_rotmatrix_etc=source_rotmatrix_etc,
            toggle=toggle_B,
            cbx=hidden_checkbox_B,
            cbx_other=hidden_checkbox_A,
        ),
        code=callback_AB_part_1
        + """
            sB[i] = 0.;
        }
        var t = [];
        var t_remove = [];
        for (let i = 0; i < indices.length; i++) {
            sB[indices[i]] = 1.;
            if (sA[indices[i]] == 1.) {
                t_remove.push(data["index"][indices[i]]);
            }
            sA[indices[i]] = 0.;
            hA[indices[i]] = 0.;
            t.push(data["index"][indices[i]]);
        }
        if (t_remove.length > 0) {
            let difference = cbx_other.active.filter(x => !t_remove.includes(x));
            cbx_other.active = difference;
            cbx_other.change.emit();
        }
        cbx.active = t;
        cbx.change.emit();
        const t_active = toggle.active;
        for (let i = 0; i < point_s.length; i++) {
            if (t_active) {
                hB[i] = sB[i];
            }
        """
        + callback_AB_part_2,
    )

    bt_A = bokeh.models.Button(
        label="Set subset A", width=button_width, button_type="primary"
    )
    bt_B = bokeh.models.Button(
        label="Set subset B", width=button_width, button_type="danger"
    )

    bt_A.js_on_click(callback_js_A)
    bt_B.js_on_click(callback_js_B)

    bt_selectA = bokeh.models.Button(label="A", width=button_width // 4)
    bt_selectA.js_on_click(
        bokeh.models.CustomJS(
            args=dict(source=source),
            code="""
        const data = source.data;
        var t = [];
        const sA = data['subset_A'];
        const point_s = data['point_size'];
        for (let i = 0; i < point_s.length; i++) {
            if (sA[i] == 1.) {
                t.push(i);
            }
        }
        source.selected.indices = t;
        source.change.emit();
    """,
        )
    )

    bt_selectB = bokeh.models.Button(label="B", width=button_width // 4)
    bt_selectB.js_on_click(
        bokeh.models.CustomJS(
            args=dict(source=source),
            code="""
        const data = source.data;
        var t = [];
        const sB = data['subset_B'];
        const point_s = data['point_size'];
        for (let i = 0; i < point_s.length; i++) {
            if (sB[i] == 1.) {
                t.push(i);
            }
        }
        source.selected.indices = t;
        source.change.emit();
    """,
        )
    )

    bt_AplusB = bokeh.models.Button(label="A+B", width=43)
    bt_AplusB.js_on_click(
        bokeh.models.CustomJS(
            args=dict(source=source),
            code="""
        const data = source.data;
        var t = [];
        const sA = data['subset_A'];
        const sB = data['subset_B'];
        const point_s = data['point_size'];
        for (let i = 0; i < point_s.length; i++) {
            if (sB[i] == 1. || sA[i] == 1.) {
                t.push(i);
            }
        }
        source.selected.indices = t;
        source.change.emit();
    """,
        )
    )

    bt_nothing = bokeh.models.Button(label="nothing", width=50)
    bt_nothing.js_on_click(
        bokeh.models.CustomJS(
            args=dict(source=source, btsr=bt_slider_range),
            code="""
        const data = source.data;
        source.selected.indices = [];
        source.change.emit();
        btsr.value = [btsr.start, btsr.end];
        btsr.change.emit();
    """,
        )
    )

    return (
        bt_A,
        toggle_A,
        hidden_checkbox_A,
        bt_B,
        toggle_B,
        hidden_checkbox_B,
        bt_AplusB,
        bt_nothing,
        bt_selectA,
        bt_selectB,
    )
