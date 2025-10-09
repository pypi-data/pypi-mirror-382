import os
import streamlit.components.v1 as components

# Toggle "release" mode depending on your workflow.
_RELEASE = True

if not _RELEASE:
    # For development, connect to Vite's dev server (adjust port if needed)
    _time_entry = components.declare_component(
        "time_entry",
        url="http://localhost:3001",  # URL to your running frontend dev server
    )
else:
    # For release, point to the local build
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _time_entry = components.declare_component("time_entry", path=build_dir)

def st_time_entry(label, default=None, key=None, disabled=False, range=None):
    """
    A modern time entry Streamlit custom component.

    Args:
        label (str): The label to display.
        default (str): The default (preselected) time in "HH:mm" format.
        key (str): Streamlit widget key.
        disabled (bool): Whether the input should be disabled.
        range (list): A list of two strings representing the min and max time.
            Example: ["09:00 am", "05:00 pm"].
    Returns:
        str or None: The time as "HH:mm" (24h), or None if not selected.
    """
    return _time_entry(label=label, default=default, key=key, disabled=disabled)