import streamlit as st
import pandas as pd
import openai

#1. Cấu hình cơ bản cho streamlit page:
st.set_page_config(
    page_title="Ask Your CSV",
    page_icon="",
    layout="wide"
)
#Khởi tạo openai client:
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
#Khởi tạo các tham số cần trong 1 section của streamlit:
if "messages" not in st.session_state: #Nếu chưa có message ban đầu thì khởi tạo
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "data_summary" not in st.session_state:
    st.session_state.data_summary = None

st.title(" Ask Your CSV")
st.markdown("Upload your data and ask questions in plain English")

#2. Tạo sidebar để upload data từ bên ngoài vào
with st.sidebar:
    st.header(" Data Upload")
    uploaded_file = st.file_uploader("Upload a CSV file", type = ["csv"]) #chỉ nhận file CSV

    if uploaded_file: #Nếu file này không rỗng
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df #cho df đọc từ csv -> df của session của streamlit

            #Create data summary for token optimization:
            #shape, column names, dtypes, sample (head(5)), basic statistics
            st.session_state.data_summary = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtype": df.dtypes.to_list(),
                "sample": df.head(3).to_dict(),
                "stats": df.describe().to_dict() if not df.empty else {} #Nếu df rỗng thì không có kết quả
            }

            st.success(f"✅ Loaded {df.shape[0]} rows x {df.shape[1]} columns") # IN RA KẾT QUẢ   

            #Data preview:
            with st.expander("Preview data"):
                st.dataframe(df.head(10)) #Hiển thị 10 dòng đầu tiên

            #Data summary:
            with st.expander("Data Prompt for AI"):
                st.session_state.data_summary


            #Basic statistics:
            with st.expander("Data Summary"):
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Total Rows", df.shape[0])
                    st.metric("Total Columns", df.shape[1])
                with col2:
                    st.metric("Memory Usage", f"{df.memory_usage().sum() / 1024:.1f} KB")
                    st.metric("Missing Values", df.isnull().sum().sum())
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please make sure your file is a valid CSV format.")
    else:
        st.info("Upload a CSV file to start analyzing!")

if st.session_state.df is not None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question about your data")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": "user_input"})
        with st.chat_message("user"):
            st.markdown(user_input)
    else:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.info("Please upload a CSV file to start!")

            st.markdown("### Example questions you can ask: ")
            st.markdown("""
            - What are the  main trends in my data ?
            - Show me a correlation matrix
            - Create a bar chart of the top 10 categories
            """) 