import streamlit as st
import pandas as pd
from datetime import date
import io
import main_v2

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Transform Data PDF-Excel", page_icon="📃", layout="centered")

# --- THÔNG TIN VERSION ---
version = '1.1'
created_date = "17.03.2026"
developer = 'quanq.duy__'

# Sidebar hoặc Header để hiện version
st.markdown("**Version {}** (updated on {})".format(version, created_date))
st.markdown("**Created by {}**".format(developer))
st.title("Transform Data From PDF To Excel")
# st.info("Công cụ hỗ trợ trích xuất và chuẩn hóa dữ liệu từ nhiều file PDF cùng lúc.")

# --- KHỞI TẠO BIẾN TRONG SESSION STATE ---
# Streamlit sẽ load lại code mỗi khi thao tác, nên cần biến này để giữ dữ liệu
if 'final_df' not in st.session_state:
    st.session_state.final_df = None

# --- BƯỚC 1: IMPORT DATA (BROWSE) ---
uploaded_files = st.file_uploader(
    "Select files that you need to transform", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    st.write("✅ Selected **{}** files.".format(len(uploaded_files)))

# --- BƯỚC 2: EXECUTE (TRANSFORM) ---
if st.button("👌 Transform", use_container_width=True):
    if not uploaded_files:
        st.error("Please select at least 1 file!!!")
    else:
        try:
            with st.spinner('--- Processing... Please wait! 🥱😴 ---'):
                # Gọi hàm xử lý từ main_script_v2
                # Lưu ý: Bạn cần sửa hàm func_execute trong main_script để nhận danh sách file buffer
                result_df = main_v2.func_execute(uploaded_files)
                
                if result_df is not None:
                    st.session_state.final_df = result_df
                    st.success("--- Success, data was transformed 🎉🎉 ---\n Let's buy food to celebrate 🍕🍔🍟🍗")
                else:
                    st.warning("None of data was found 🫠")
        except Exception as e:
            st.error(f"--- Error ---: {str(e)}")

# --- BƯỚC 3: SHOW KẾT QUẢ & DOWNLOAD ---
if st.session_state.final_df is not None:
    st.divider()
    st.subheader("Preview 10 rows of transformed data 🫣")
    st.dataframe(st.session_state.final_df.head(10))

    # Tạo buffer để tải file về (Thay cho việc lưu vào folder local)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        st.session_state.final_df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    st.download_button(
        label="📥 Download Excel file",
        data=buffer.getvalue(),
        file_name=f"Tong hop PO_{date.today().strftime('%d.%m.%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    print('Exported data to excel file - done')
    print('--- Programm ended ---')

# Nút Exit (Trong web thì chỉ cần tắt tab, nhưng có thể dùng nút này để clear data)
if st.sidebar.button("Reset / Clear Data"):
    st.session_state.final_df = None
    st.rerun()