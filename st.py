import streamlit as st


ROW_CONFIGS = [
    {"id": 1, "default_label": "Row 1", "color": "green"},
    {"id": 2, "default_label": "Row 2", "color": "red"},
]


# Initialize session state keys only once to keep state across reruns.
if "row_labels" not in st.session_state or not isinstance(
    st.session_state.row_labels, dict
):
    st.session_state.row_labels = {}
if "last_submissions" not in st.session_state or not isinstance(
    st.session_state.last_submissions, dict
):
    st.session_state.last_submissions = {}
if "active_dialog_row" not in st.session_state:
    st.session_state.active_dialog_row = None
if "dialog_input_should_clear" not in st.session_state or not isinstance(
    st.session_state.dialog_input_should_clear, dict
):
    st.session_state.dialog_input_should_clear = {}

for row in ROW_CONFIGS:
    row_id = row["id"]
    st.session_state.row_labels.setdefault(row_id, row["default_label"])
    st.session_state.last_submissions.setdefault(row_id, "")
    st.session_state.dialog_input_should_clear.setdefault(row_id, False)
    input_key = f"dialog_input_{row_id}"
    if input_key not in st.session_state:
        st.session_state[input_key] = st.session_state.row_labels[row_id]


def _open_dialog(row_id: int):
    """Open the rename dialog for the requested row."""
    st.session_state.active_dialog_row = row_id
    st.session_state.dialog_input_should_clear[row_id] = True


def _store_submission(row_id: int, text: str):
    """Persist the submitted text for a row, close the dialog, and refresh."""
    trimmed = text.strip() or st.session_state.row_labels[row_id]
    st.session_state.row_labels[row_id] = trimmed
    st.session_state.last_submissions[row_id] = trimmed
    st.session_state.active_dialog_row = None
    st.session_state.dialog_input_should_clear[row_id] = True
    st.rerun()


def _clear_row(row_id: int):
    """Clear the label shown in column 1 for the requested row."""
    st.session_state.row_labels[row_id] = ""
    st.session_state.last_submissions[row_id] = ""
    st.session_state.dialog_input_should_clear[row_id] = True
    st.session_state.active_dialog_row = None
    st.rerun()


@st.dialog("Rename row")
def rename_dialog():
    row_id = st.session_state.active_dialog_row
    if row_id is None:
        return

    input_key = f"dialog_input_{row_id}"
    if st.session_state.dialog_input_should_clear.get(row_id):
        st.session_state[input_key] = st.session_state.row_labels[row_id]
        st.session_state.dialog_input_should_clear[row_id] = False

    # A form lets Enter trigger the same action as clicking submit.
    with st.form(f"text_capture_form_row_{row_id}", clear_on_submit=False):
        text = st.text_input(
            "Rename the label",
            key=input_key,
            placeholder="Type here and press Enter…",
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            _store_submission(row_id, text)


st.title("Dialog demo")
st.write("Use the table to rename each row via its dialog.")

with st.container(border=True):
    header_cols = st.columns([3, 0.5, 1])
    header_cols[0].markdown("**Row Name**")
    # header_cols[1].markdown("**Rename**")
    # header_cols[2].markdown("**Clear**")

for row in ROW_CONFIGS:
    row_id = row["id"]
    with st.container(border=True):
        cols = st.columns([1, 0.25, 0.25], vertical_alignment="center")
        with cols[0]:
            st.markdown(
                f"<span style='color:{row['color']}; font-weight:bold;'>"
                f"{st.session_state.row_labels[row_id] or '&nbsp;'}"
                "</span>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.button(
                "Rename",
                key=f"open_dialog_{row_id}",
                on_click=_open_dialog,
                args=(row_id,),
            )
        with cols[2]:
            st.button(
                ":red[Clear]",
                key=f"clear_row_{row_id}",
                on_click=_clear_row,
                args=(row_id,),
                use_container_width=True,
            )

if st.session_state.active_dialog_row is not None:
    rename_dialog()

for row in ROW_CONFIGS:
    row_id = row["id"]
    last_value = st.session_state.last_submissions[row_id]
    if last_value:
        st.success(f"Row {row_id} now reads: {last_value}")
