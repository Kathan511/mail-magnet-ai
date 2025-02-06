import streamlit as st
import validators

from utils import utils

#expander
st.set_page_config(layout="wide")

# Initialize session state variables
if 'api_flag' not in st.session_state:
    st.session_state['api_flag'] = None
if 'urls' not in st.session_state:
    st.session_state['urls'] = []
if 'feedback' not in st.session_state:
    st.session_state['feedback'] = None
if 'process_complete' not in st.session_state:
    st.session_state['process_complete'] = False
if 'show_feedback' not in st.session_state:
    st.session_state['show_feedback'] = False

if 'draft_email' not in st.session_state:
    st.session_state['draft_email'] = ''

if 'accept_flag' not in st.session_state:
    st.session_state['accept_flag'] = ''

if 'after_human_feedback' not in st.session_state:
    st.session_state['after_human_feedback'] = ''

config ={"configurable":{"thread_id":"1"}}

# Processing function to be reused
def process_data(file_content,llm,hf_flag,**kwargs):
    
    # Check for valid API key flag
    if st.session_state['api_flag']:
        if not hf_flag:
            #invoke the graph with provided text file
            result=graph.invoke({"target_urls":st.session_state['urls'],
                        "source_text":file_content,
                        "llm":llm},config=config)
        else:
            human_feedback = kwargs.get('human_feedback')
            print(f"HUMAN: {human_feedback}")

            #invoke the graph with provided text file
            graph.update_state(config=config,values={"human_reviewer_feedback":human_feedback},as_node='human_feedback_func')



            result=graph.invoke(None,config=config)

        st.session_state['process_complete'] = True

        return result['draft_email']
    else:
        st.error("Please provide an API Key in the sidebar to proceed.")

# Sidebar for API key input

# initialize llm
api_key=st.secrets['OPENAI_API_KEY']
flag,llm = utils.initialize_llm(api_key)

if flag:
    st.session_state['api_flag'] = True
    
    #Build a graph
    graph = utils.build_graph()






# Main app title
st.title("MailMagnet AI 📩")
st.text('Craft emails that attract, engage, and convert—automatically!')

# URL management functions
def add_url():
    new_url = st.session_state['url_input']
    if new_url:
        if validators.url(new_url):
            st.session_state['urls'].append(new_url)
            st.session_state['url_input'] = ""
        else:
            st.error("Invalid URL. Please enter a valid URL.")

def remove_url(index):
    st.session_state['urls'].pop(index)

# URL input UI
st.text_input(
    "Add URL(s)",
    key='url_input',
    on_change=add_url,
    placeholder="Please provide the URL of the target company that showcases their offerings (i.e. About Us page)"
)

# Display URLs with remove buttons
st.text("Entered URLs:")
for i, url in enumerate(st.session_state['urls']):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"{i + 1}. {url}")
    with col2:
        if st.button(f"Remove URL {i + 1}", key=f"remove_{i}"):
            remove_url(i)
            st.rerun()  # Refresh UI after removal

# File uploader (optional)
uploaded_file = st.file_uploader("Upload a text file of Source file", type=["txt"])

if uploaded_file:
    file_content = uploaded_file.getvalue().decode("utf-8")

# Main process button (only shows before processing is complete)
if not st.session_state['process_complete']:
    if st.session_state['accept_flag']:
        st.success("### Here is your final email")
        st.markdown(
                f"""
                <div style="
                    border: 2px solid white;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: black;
                    color: white;
                    font-size: 18px;
                    ">
                    {st.session_state['draft_email']}
                </div>
                """,
                unsafe_allow_html=True
            )

        new_process_btn=st.button("Start New Email Draft Process")
            
        if new_process_btn:
            # Reset session state variables
            st.session_state['process_complete'] = False
            st.session_state['show_feedback'] = False
            st.session_state['accept_flag'] = ''
            st.session_state['draft_email'] = ''
            st.session_state['urls'] = []
        
            # Refresh the app
            st.rerun()

    
    else:
        if st.button("Process",type='primary'):
            if uploaded_file and len(st.session_state['urls'])!=0:

                draft_email = process_data(file_content,llm,hf_flag=False)
                # #st.rerun()  # Update UI after processing
                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid white;
                        padding: 10px;
                        border-radius: 5px;
                        background-color: black;
                        color: white;
                        font-size: 18px;
                        ">
                        {draft_email}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # st.markdown(draft_email)
                st.session_state['draft_email'] = draft_email
            else:
                st.warning("Please Submit URLs and Text file.")


# Post-processing workflow: repeatedly ask for Accept or Modify until accepted
if st.session_state['process_complete']:
    st.write("### Processing Complete!")
    
    # If user chooses Modify, show feedback UI.
    if st.session_state['show_feedback']:
        st.markdown(
                f"""
                <div style="
                    border: 2px solid white;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: black;
                    color: white;
                    font-size: 18px;
                    ">
                    {st.session_state['draft_email']}
                </div>
                """,
                unsafe_allow_html=True
            )
        feedback = st.text_input(
            "Provide your feedback (human_feedback):",
            key="human_feedback",
            placeholder="Enter your feedback here"
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("Process Feedback"):
                if feedback:
                    # Re-run processing with the provided feedback
                    draft_email = process_data(file_content,llm,hf_flag=True,human_feedback=feedback)
                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid white;
                            padding: 10px;
                            border-radius: 5px;
                            background-color: black;
                            color: white;
                            font-size: 18px;
                            ">
                            {draft_email}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.session_state['draft_email'] = draft_email

                    st.success("Feedback processed successfully!")
                    # Hide feedback input to show Accept/Modify options again
                    st.session_state['show_feedback'] = False
                    st.session_state['after_human_feedback'] = True
                    st.rerun()
                else:
                    st.warning("Please enter feedback before processing")
        with col2:
            if st.button("Cancel"):
                st.session_state['show_feedback'] = False
                #st.rerun()
    else:
        if st.session_state['after_human_feedback']:
            st.markdown(
                        f"""
                        <div style="
                            border: 2px solid white;
                            padding: 10px;
                            border-radius: 5px;
                            background-color: black;
                            color: white;
                            font-size: 18px;
                            ">
                            {st.session_state['draft_email']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        st.write("What would you like to do next?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Accept"):
                st.success("Processing accepted!")
                # Reset processing so that the app can start over if needed.
                draft_email=process_data(file_content,llm,hf_flag=True,human_feedback=None)

                st.session_state['accept_flag'] = True
                ##final email
                st.session_state['process_complete'] = False
                st.text("Done")
                st.rerun()                
        with col2:
            if st.button("Modify"):
                st.session_state['show_feedback'] = True
                #st.rerun()
