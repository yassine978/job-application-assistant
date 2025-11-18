"""Statistics card component."""

import streamlit as st
from typing import Optional


def render_stat_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: Optional[str] = None
) -> None:
    """Render a statistics card.

    Args:
        label: Stat label
        value: Main value to display
        delta: Change/delta value
        icon: Optional emoji icon
    """
    with st.container():
        if icon:
            st.markdown(f"### {icon} {label}")
        else:
            st.markdown(f"### {label}")

        st.metric(label="", value=value, delta=delta, label_visibility="collapsed")


def render_stats_row(stats: list) -> None:
    """Render a row of statistics cards.

    Args:
        stats: List of stat dictionaries with keys: label, value, delta, icon
    """
    cols = st.columns(len(stats))

    for i, stat in enumerate(stats):
        with cols[i]:
            render_stat_card(
                label=stat.get('label', ''),
                value=stat.get('value', '0'),
                delta=stat.get('delta'),
                icon=stat.get('icon')
            )
