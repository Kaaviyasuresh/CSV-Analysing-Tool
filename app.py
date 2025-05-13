import streamlit as st
from audiorecorder import audiorecorder
import helper
from pathlib import Path
import uuid
import re
import os
import pandas as pd
import base64
from streamlit_login_auth_ui.widgets import __login__
import warnings
warnings.filterwarnings("ignore")

data_folder = Path("data")
data_folder.mkdir(parents=True, exist_ok=True)

def set_bg_hack(main_bg):
    file_extension = os.path.splitext(main_bg)[-1].lower().replace(".", "")
    with open(main_bg, "rb") as f:
        image_data = f.read()
    base64_image = base64.b64encode(image_data).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{file_extension};base64,{base64_image});
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


if 'csv_agent' not in st.session_state:
    st.session_state['csv_agent'] = None

if 'csv_file_path' not in st.session_state:
    st.session_state['csv_file_path'] = None

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = Path('data', uuid.uuid4().hex + '.pdf')

if "graph_file_list" not in st.session_state:
    st.session_state["graph_file_list"] = []

if "receiver_email_id" not in st.session_state:
    st.session_state["receiver_email_id"] = None

st.title("Data Analysis Agent App")

__login__obj = __login__(auth_token = "dk_prod_XHG9DC6V4EMCB2J8X6GJA01AFJMS", 
                    company_name = "Shims",
                    width = 200, height = 250, 
                    logout_button_name = 'Logout', hide_menu_bool = False, 
                    hide_footer_bool = False, 
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()
if LOGGED_IN == True:
    # set_bg_hack('sample.jpg')
    fetched_cookies = __login__obj.cookies
    if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
        username = fetched_cookies['__streamlit_login_signup_ui_username__']
        st.write(f"Welcome, {username}!")
        st.session_state["receiver_email_id"] = helper.get_email_by_username(username)
    user_choice = st.selectbox(label = "Select option", 
                            options = ["Upload Data", "Analysis", "Email"], 
                            index=0)

    if user_choice == "Upload Data":
        uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'])
        if st.button("Upload"):
            if uploaded_file is not None:
                df = helper.read_file(uploaded_file)
                local_file_path = Path("data", Path(uploaded_file.name).stem + ".csv")
                st.session_state['csv_file_path'] = local_file_path
                df.to_csv(local_file_path, index = False)
                st.session_state['csv_agent'] = helper.create_agent(str(local_file_path))
                query = "Descrive the provided dataset"
                response = st.session_state['csv_agent'].run(query)
                st.write("Dataset description: " + response)
                pdf_text = f"Dataset description:\n\n{response}"
                helper.add_text_and_image_to_pdf(st.session_state['session_id'], pdf_text, "xyz.txt")
                st.success("File was successfully created")
            else:
                st.error("File not uploaded")
    elif user_choice == "Analysis":
        if not st.session_state['csv_agent']:
            st.error("File not uploaded")
        else:
            type = st.selectbox(label = "Select option", 
                            options = ["Audio", "Text"], 
                            index=0)
            
            if type == "Audio":
                audio = audiorecorder("Click to record", "Click to stop recording")
                if len(audio) > 0:
                    st.audio(audio.export().read())  
                    audio.export("audio.wav", format="wav")
                    st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
                query = helper.get_english_transcription("audio.wav")
            else:
                query = st.text_input("Enter your query")

            column_names = st.multiselect(label = 'Columns', 
                                        options = pd.read_csv(st.session_state['csv_file_path'], index_col=0, nrows=0).columns.tolist(), 
                                        default=None)
            st.write(f"Query: {query}")
            if st.button("Run query"):
                if query:
                    org_query = query
                    pdf_text = f"Query: {query}\n\n"
                    if column_names:
                        query += f". Use columns: {', '.join(column_names)}"
                    response = st.session_state['csv_agent'].run(query)
                    pdf_text += f"Response: {response}\n\n"
                    st.write("Response: " + response)
                    
                    query = f"Query: {org_query}. Save a graph locally and return file name in double quotes to answer the query."
                    response = st.session_state['csv_agent'].run(query)
                    graph_file = re.findall(r'"([^"]*)"', response)[0]
                    print("graph_file: ",graph_file)
                    if Path(graph_file).exists:
                        st.image(graph_file)
                        st.session_state["graph_file_list"].append(graph_file)
                    else:
                        st.write("Graph cannot be generated")
                        graph_file = "xyz.txt"
                    helper.add_text_and_image_to_pdf(st.session_state['session_id'], pdf_text, graph_file)
                else:
                    st.error("Please define a query")
    else:
        if Path(st.session_state['session_id']).exists():
            with open(st.session_state['session_id'], "rb") as pdf_file:
                pdf_content = pdf_file.read()
            
            st.download_button(
                label="Download PDF",
                data=pdf_content,
                file_name=Path(st.session_state['session_id']).name,
                mime="application/pdf"
            )

            if st.button("send"):
                helper.send_pdf_email(st.session_state["receiver_email_id"], st.session_state['session_id'])
                st.success("Email sent successfully")
                for file in st.session_state["graph_file_list"]:
                    if Path(file).exists():
                        os.remove(file)
                os.remove(st.session_state['session_id'])
        else:
            st.error("No PDF file to send")