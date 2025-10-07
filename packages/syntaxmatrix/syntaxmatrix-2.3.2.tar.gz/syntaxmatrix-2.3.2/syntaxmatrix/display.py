 # -----------------------------------------------------------------
#  Paste *inside* syntaxmatrix/display.py – only the show() body
# -----------------------------------------------------------------
def show(obj):
    """
    Render common objects so the Dashboard (or chat) always shows output.
    """
    import io, base64, numbers
    from IPython.display import display, HTML
    import pandas as pd
    import matplotlib.figure as mpfig

    # ── matplotlib Figure ─────────────────────────────────────────
    if isinstance(obj, mpfig.Figure):
        display(obj)                  
        return None
    
    if isinstance(obj, (pd.Series, pd.DataFrame)):

        html = obj.to_html(classes="smx-table", border=0)
        wrapped_html = (
            "<style>"
            ".smx-table{border-collapse:collapse;font-size:0.9em;white-space:nowrap;}"
            ".smx-table th{background:#f0f2f5;text-align:left;padding:6px 8px;border:1px solid gray;}"
            ".smx-table td{border:1px solid #ddd;padding:6px 8px;}"
            ".smx-table tbody tr:nth-child(even){background-color:#f9f9f9;}"
            "</style>"
            "<div style='overflow-x:auto; max-width:100%; margin-bottom:1rem;'>"
            + html +
            "</div>"
        )
        display(HTML(wrapped_html))
        return None

    # ── dict of scalars → pretty 2-col table ─────────────────────
    if isinstance(obj, dict) and all(isinstance(v, numbers.Number) for v in obj.values()):
        df_ = pd.DataFrame({"metric": list(obj.keys()),
                            "value":  list(obj.values())})
        display(df_)
        return None

    # ── 2-tuple of numbers (mse, r²) ─────────────────────────────
    if (isinstance(obj, tuple) and len(obj) == 2 and
            all(isinstance(v, numbers.Number) for v in obj)):
        mse, r2 = obj
        df_ = pd.DataFrame({"metric": ["Mean-squared error", "R²"],
                            "value":  [mse, r2]})
        display(df_)
        return None

    # ── fallback ─────────────────────────────────────────────────
    display(HTML(f"<pre>{obj}</pre>"))

    return None
