import streamlit as st
from datetime import datetime
from st_time_entry import st_time_entry
cols = st.columns(2)
with cols[0]:
    st.write("**Start time**")
    st_time_entry(
        "Pick a start time",
        range = ["09:00 am", "05:00 pm"],
        key="time_entry_1",
    )
with cols[1]:
    st.write("**End time**")
    st_time_entry(
        "Pick an end time",
        # set default to right now
        default=datetime.now().strftime("%I:%M %p"),
        range = ["09:00 am", "05:00 pm"],
        disabled=True,
        key="time_entry_2",
    )
# convert to datetime objects
if st.session_state.time_entry_1 and st.session_state.time_entry_2:
    # convert the time strings to datetime objects
    # the day for each is set to today
    today = datetime.today().date()
    start_time_obj = datetime.strptime(st.session_state.time_entry_1, "%I:%M %p").time()
    end_time_obj = datetime.strptime(st.session_state.time_entry_2, "%I:%M %p").time()
    start_time = datetime.combine(today, start_time_obj)
    end_time = datetime.combine(today, end_time_obj)
    if start_time > end_time:
        st.error("Start time must be before end time.")
    elif end_time > start_time:
        st.success("Start time is before end time.")
    elif end_time == start_time:
        st.warning("Start time is equal to end time.")