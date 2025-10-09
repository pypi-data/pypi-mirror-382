# st-time-entry

A Streamlit component that adds a modern time picker using [MUI X TimePicker](https://mui.com/x/react-date-pickers/time-picker/). Supports AM/PM and 24-hour formats, time range limits, and input validation.

## Features
- Modern Material UI (MUI X) TimePicker in Streamlit
- AM/PM and 24-hour support
- Set default time and restrict selectable time range
- Disable input as needed
- Returns time as a string (e.g., `"09:30 am"`)

## Installation

```bash
pip install st-time-entry
```

## Usage

```python
import streamlit as st
from st_time_entry import st_time_entry

# Basic usage
selected_time = st_time_entry(
                    "Pick a start time",
                    key="time_entry_1",
                )
st.write("Selected time:", selected_time)
```

## Development
- Frontend: React + TypeScript + MUI X Date Pickers
- Backend: Python (Streamlit custom component)

## License
This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).

## Acknowledgements

Based on [streamlit/component-template](https://github.com/streamlit/component-template).
