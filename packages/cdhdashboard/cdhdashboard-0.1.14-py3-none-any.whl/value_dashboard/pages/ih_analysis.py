import re
import time
from collections import defaultdict, OrderedDict

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_dimensions import st_dimensions
from streamlit_dynamic_filters import DynamicFilters
from streamlit_option_menu import option_menu

from value_dashboard.pipeline.datatools import get_reports_data_by_name
from value_dashboard.pipeline.ih import load_data
from value_dashboard.reports.registry import get_figures
from value_dashboard.utils.config import get_config
from value_dashboard.utils.py_utils import strtobool
from value_dashboard.utils.st_utils import highlight_and_format, format_dates

pd.options.styler.format.thousands = ','
pd.options.styler.format.na_rep = 'background-color: lightgrey;'
pd.options.styler.format.precision = 4
dataset_max_rows = 1000
pd.set_option("styler.render.max_elements", dataset_max_rows * 100)

dims = st_dimensions()
st.session_state['dashboard_dims'] = dims

if "data_loaded" not in st.session_state:
    st.warning("Please configure your files in the `data import` tab.")
    st.stop()

if strtobool(get_config()["ux"]["refresh_dashboard"]):
    count = st_autorefresh(interval=get_config()["ux"]["refresh_interval"], key="dashboard-counter")

tabs = ["🗃 Data Overview"]
st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 2rem;
                    padding-left: 1rem;
                    padding-right: 2rem;
                }
        </style>
        """, unsafe_allow_html=True)
f"""## 📊 Integrated Performance Dashboard: Business & Technical Metrics"""
figures = get_figures()
reports_name_map = OrderedDict()
reports = get_config()["reports"]
for report in reports:
    params = reports[report]
    if not params['metric'].startswith("clv"):
        reports_name_map[params["description"].strip()] = report
reports_list = list(reports_name_map.keys())
result = defaultdict(list)
pattern = re.compile(r'\[([^\[\]]+)\]')
for string in reports_list:
    matches = pattern.findall(string)
    for match in matches:
        cleaned_string = string  # re.sub(r'\[([^\[\]]+)\]', '', string).strip()
        result[match].append(cleaned_string)
result_dict = dict(result)
with st.sidebar:
    if 'dashboard_last_access_time' not in st.session_state:
        st.session_state['dashboard_last_access_time'] = time.time()
    if 'selected_report' not in st.session_state:
        previous_selected_report = None
    else:
        previous_selected_report = st.session_state['selected_report']

    previous_access_time = st.session_state['dashboard_last_access_time']

    manual_select = None
    if strtobool(get_config()["ux"]["refresh_dashboard"]):
        if previous_selected_report:
            if (time.time() - previous_access_time + 5) * 1000 >= get_config()["ux"]["refresh_interval"]:
                idx = reports_list.index(previous_selected_report)
                manual_select = (idx + 1) % len(reports_list)

    with st.expander("**Select report**", icon=":material/analytics:", expanded=True):
        selected_report = option_menu("", reports_list,
                                      # menu_icon="list-task",
                                      manual_select=manual_select,
                                      icons=["-" for r in reports_list],
                                      styles={
                                          "container": {"padding": "0!important", "background-color": "transparent"},
                                          "nav-link": {"font-size": "12px", "text-align": "left", "margin": "0px"}
                                      },
                                      key='select_report_menu')
    st.session_state['dashboard_last_access_time'] = time.time()
    st.session_state['selected_report'] = selected_report

df, params = get_reports_data_by_name(reports_name_map[selected_report], load_data())
dynamic_filters = DynamicFilters(df.to_pandas(),
                                 filters=get_config()["metrics"]["global_filters"])
with st.sidebar:
    st.write("Filter data globally 👇")
    dynamic_filters.display_filters()

globally_filtered_data = dynamic_filters.filter_df()
filtered_rep_data = figures[reports_name_map[selected_report]](globally_filtered_data, params)

c1, c2 = st.columns([0.7, 0.3], vertical_alignment="center")
c1.write("#### 🗃 Data Overview")
grp_by = reports[reports_name_map[selected_report]].get("group_by", filtered_rep_data.columns.tolist())
cols = list(set(filtered_rep_data.columns.tolist()) - set(grp_by))
column_order = grp_by + sorted(cols)
st.data_editor(format_dates(filtered_rep_data.head(dataset_max_rows)).map(highlight_and_format),
               width='stretch',
               column_order=column_order,
               height=640 if filtered_rep_data.shape[0] > 15 else 'auto',
               hide_index=True,
               disabled=True,
               key='dashboard-data')
