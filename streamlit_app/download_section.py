"""Reusable download UI for explorer pages."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from streamlit_app.export_common import ExportBundle, zip_bytes, zip_html_only, zip_png_only


def render_download_section(
    build_bundle: Callable[[], ExportBundle],
    *,
    chart_stems: tuple[str, ...],
    zip_prefix: str,
    export_key: tuple,
    session_bundle_key: str,
    session_key_key: str,
) -> None:
    if st.session_state.get(session_key_key) != export_key:
        st.session_state.pop(session_bundle_key, None)

    with st.expander("Download options", expanded=True):
        if st.button("Prepare download package", type="primary", use_container_width=True):
            with st.spinner("Building PNG, HTML, and map files…"):
                st.session_state[session_bundle_key] = build_bundle()
                st.session_state[session_key_key] = export_key

        stored: ExportBundle | None = st.session_state.get(session_bundle_key)
        if stored is None:
            st.info("Click **Prepare download package** to generate files for your current view.")
            return

        files = stored.files
        st.success(
            f"Ready: **{len(files)}** files "
            f"({stored.png_chart_count} PNG, {sum(1 for k in files if k.endswith('.html'))} HTML)."
        )
        if stored.png_errors:
            for err in stored.png_errors:
                st.caption(err)

        z1, z2, z3 = st.columns(3)
        with z1:
            st.download_button(
                "All files (ZIP)",
                zip_bytes(files),
                f"{zip_prefix}_all.zip",
                "application/zip",
                use_container_width=True,
            )
        with z2:
            st.download_button(
                "PNG only (ZIP)",
                zip_png_only(files),
                f"{zip_prefix}_png.zip",
                "application/zip",
                use_container_width=True,
                disabled=not any(k.endswith(".png") for k in files),
            )
        with z3:
            st.download_button(
                "HTML only (ZIP)",
                zip_html_only(files),
                f"{zip_prefix}_html.zip",
                "application/zip",
                use_container_width=True,
            )

        st.markdown("**Charts — PNG and HTML**")
        for stem in chart_stems:
            label = stored.chart_labels.get(stem, stem)
            c_png, c_html = st.columns(2)
            with c_png:
                if f"{stem}.png" in files:
                    st.download_button(
                        f"{label} (PNG)",
                        files[f"{stem}.png"],
                        f"{stem}.png",
                        "image/png",
                        use_container_width=True,
                        key=f"dl_png_{zip_prefix}_{stem}",
                    )
                else:
                    st.caption(f"{label}: PNG unavailable")
            with c_html:
                if f"{stem}.html" in files:
                    st.download_button(
                        f"{label} (HTML)",
                        files[f"{stem}.html"],
                        f"{stem}.html",
                        "text/html",
                        use_container_width=True,
                        key=f"dl_html_{zip_prefix}_{stem}",
                    )

        if "interactive_map.html" in files or "map_snapshot.png" in files:
            st.markdown("**Map**")
            m1, m2 = st.columns(2)
            with m1:
                if "map_snapshot.png" in files:
                    st.download_button(
                        f"{stored.chart_labels.get('map_snapshot', 'Map snapshot')} (PNG)",
                        files["map_snapshot.png"],
                        "map_snapshot.png",
                        "image/png",
                        use_container_width=True,
                        key=f"dl_map_png_{zip_prefix}",
                    )
            with m2:
                if "interactive_map.html" in files:
                    st.download_button(
                        f"{stored.chart_labels.get('interactive_map', 'Interactive map')} (HTML)",
                        files["interactive_map.html"],
                        "interactive_map.html",
                        "text/html",
                        use_container_width=True,
                        key=f"dl_map_html_{zip_prefix}",
                    )
