import streamlit as st
import pandas as pd
from datetime import datetime, date
import pytz
import io
import main_v2

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Transform Data PDF-Excel", page_icon="📃", layout="centered")

# --- THÔNG TIN VERSION ---
version = '1.2'
developer = 'quanq.duy__'
de_tz = pytz.timezone("Europe/Berlin")
date_de = datetime.now(de_tz)
created_date = date_de.strftime("%d.%m.%Y")


# Sidebar hoặc Header để hiện version
st.markdown("**Created by** {}".format(developer))
st.caption("*Version {} (updated on {})*".format(version, created_date))
st.title("Transform Data From PDF To Excel")


# TRANSPARENT LIQUID GLASS (APPLE STYLE) ---
apple_transparent_glass_style = """
<style>
/* 1. Nền App chính: Màu trắng mờ hoặc xám cực nhẹ (#F8F9FA) */
.stApp {
    background-color: #F8F9FA !important;
}

/* 2. Hiệu ứng Kính Liquid Trong suốt (Glassmorphism mờ mạnh) */
/* Áp dụng cho File Uploader, DataFrame, Success/Error và Sidebar */
[data-testid="stFileUploader"], 
.stButton>button, 
[data-testid="stDataFrame"], 
div.stSuccess, div.stError, div.stWarning,
[data-testid="stSidebar"] > div:first-child {
    background: rgba(255, 255, 255, 0.01) !important; /* Gần như trong suốt hoàn toàn */
    backdrop-filter: blur(20px) saturate(500%); /* QUAN TRỌNG: Làm mờ cực mạnh nền phía sau để tạo độ dày cho kính */
    -webkit-backdrop-filter: blur(25px) saturate(180%);
    
    border: 1px solid rgba(0, 0, 0, 0.05) !important; /* Viền đen cực mảnh để định hình khối trên nền sáng */
    border-radius: 20px !important; /* Bo góc tròn mềm mại */
    box-shadow: none !important; /* Bỏ đổ bóng để trông phẳng và thanh thoát */
    transition: all 0.3s ease; /* Hiệu ứng mượt khi hover */
}

/* Tinh chỉnh khung Browse File (nơi có chữ Drag and drop) */
[data-testid="stFileUploader"] > section {
    background-color: transparent !important;
    # border: 1px dashed rgba(0, 0, 0, 0.00) !important; /* Viền đứt đoạn cho khu vực upload */
}

/* 3. Nút bấm "Liquid" (màu xám đậm để dễ đọc, bo góc) */
.stButton>button {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.01)) !important;
    color: #1E1E1E !important; /* Chữ xám đậm */
    font-weight: 500;
}

.stButton>button:hover {
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    background: rgba(0, 0, 0, 0.03) !important; /* Hiện màu cực nhẹ khi chạm vào */
    transform: scale(1.03); /* Phóng to nhẹ 1% tạo cảm giác liquid */
}

/* 4. Màu text: Dùng màu Anthracite */
h1, h2, h3, p, label, .stMarkdown {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1E1E1E !important; /* Chữ xám đậm Anthracite */
    letter-spacing: -0.3px;
}
</style>
"""
st.markdown(apple_transparent_glass_style, unsafe_allow_html=True)


# -------------------------------------------------------------------------------------------------------------------------

# --- KHỞI TẠO BIẾN TRONG SESSION STATE ---
# Streamlit sẽ load lại code mỗi khi thao tác, nên cần biến này để giữ dữ liệu
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

if 'final_df' not in st.session_state:
    st.session_state.final_df = None


# --- BƯỚC 1: IMPORT DATA ---
uploaded_files = st.file_uploader(
    "Select files that you need to transform", 
    type="pdf", 
    accept_multiple_files=True,
    label_visibility="collapsed",
    key="uploader_{}".format(st.session_state.uploader_key)
)

if uploaded_files:
    st.write("✅ Selected **{}** files.".format(len(uploaded_files)))


# --- SIDEBAR: NÚT RESET ---
if st.button("Reset / Clear Data", use_container_width=True):
    # Tăng key để ép file_uploader reset hoàn toàn danh sách file
    st.session_state.uploader_key += 1
    st.session_state.final_df = None
    st.rerun()


# --- BƯỚC 2: EXECUTE (TRANSFORM) ---
if st.button("Transform", use_container_width=True):
    if not uploaded_files:
        st.error("Please select at least 1 file!!!")
    else:
        try:
            with st.spinner('--- Processing... Please wait! 🥱😴 ---'):
                result_df, flag = main_v2.func_execute(uploaded_files)

                if result_df is not None:
                    if flag is True:
                        st.session_state.final_df = result_df
                        st.success("--- Success, data was transformed 🎉🎉 --- Let's buy food to celebrate 😍🍔🍟")
                    elif flag is False:
                        st.session_state.final_df = result_df
                        st.error("--- Failed, Please check your input data 😒 ---")
                else:
                    st.warning("None of data was found 🫠")
        except Exception as e:
            st.error("--- Error ---: {}".format(str(e)))

# --- BƯỚC 3: SHOW KẾT QUẢ & DOWNLOAD ---
if st.session_state.final_df is not None:
    try:
        if flag is True:
            st.divider()
            st.subheader("Preview 5 rows of transformed data 🫣")
            st.dataframe(st.session_state.final_df.head())

            # Tạo buffer để tải file về (Thay cho việc lưu vào folder local)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                st.session_state.final_df.to_excel(writer, index=False, sheet_name='Sheet1')

            st.download_button(
                label="📥 Download Excel file",
                data=buffer.getvalue(),
                file_name=f"Transformed PO_{date.today().strftime('%d.%m.%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            print('Exported data to excel file - done')
            print('--- Programm ended ---')
        elif flag is False:
            st.divider()
            st.subheader("Review these data again 😤")
            st.dataframe(st.session_state.final_df)
            print('--- Programm ended ---')
    except:
        print('')
    


# # Nút Exit (Trong web thì chỉ cần tắt tab, nhưng có thể dùng nút này để clear data)
# if st.sidebar.button("Reset / Clear Data"):
#     st.session_state.final_df = None
#     st.rerun()
