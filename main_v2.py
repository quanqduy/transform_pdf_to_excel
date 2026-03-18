import pandas as pd
# import numpy as np
# from datetime import date
import pdfplumber, os 
# import sys
import tempfile

'''command 17.03.2026'''
# def func_import_data ():
#     # file_path_import = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xls;*.xlsx;*.xlsb")])
#     files_path_import = filedialog.askopenfilenames(filetypes=[("All Files", "*.*")], multiple=True)
#     # print(files_path_import)
#     list_filenames = list(files_path_import)
#     # print(list_filenames)
#     return list_filenames

def function_read_pdf (**kwargs):
    table_name = kwargs.get('table_name')
    all_data_list = []
    with pdfplumber.open(table_name) as pdf:
        for i, page in enumerate(pdf.pages):
            # 1. Trích xuất văn bản để tìm Mã Đơn Hàng + Delivery date
            text = page.extract_text()
            if text:
                po_num = None
                delivery_date = None

                for line in text.split('\n'):
                    # Tìm dòng có chứa từ khóa
                    if "Mã Đơn Hàng" in line or "PO No." in line:
                        # print(line)
                        po_num = line.split(':')[-1].strip()
                    if ("Ngày Phân Phối" in line or "Last Delivery Date" in line) and ':' in line:
                        # print(line)
                        delivery_date = line.split(':')[-1].strip()
                        # print(delivery_date)
                    
            # 2. Trích xuất bảng
            table = page.extract_table()
            if table:
                # Chuyển bảng thành DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])

                # 3. Thêm một cột mới để lưu Mã Đơn Hàng + Delivery date
                df['MA_DON_HANG'] = po_num
                df['PAGE_NUMBER'] = i + 1
                df['DELIVERY_DATE'] = delivery_date

                all_data_list.append(df)
    all_data_df = pd.concat(all_data_list, ignore_index=True)
    return all_data_df


'''---------------------------------------------------------------------------------------------------------------------------------------------'''
# def func_main_process():
#     input_list = func_import_data()
    # print(input_list)
def func_main_process(input_list):
    '''Đọc data bàng pdfplumber để lấy toàn bộ dữ liệu (chưa có số PO)'''
    list_df = []
    for tbl in input_list:
        # print(tbl)
        df_readed = function_read_pdf(table_name = tbl)

        #Add 18.03.2026
        df_readed['FILE_PATH'] = tbl

        list_df.append(df_readed)
    tables = pd.concat(list_df, ignore_index=True)
    # print(tables)
    print('Read data from list - success')


    '''Add 17.03.2026 _ fix lỗi tên các tiêu đề cột'''
    tables.columns = [col.replace('\n', '').replace(' ', '') for col in tables.columns]
    # 1. Định nghĩa "Bản đồ từ khóa": Tên Chuẩn -> [Danh sách từ khóa nhận diện]
    mapping = {
        'STT': ['STT'],
        'CHI TIẾT MÃ HÀNG': ['CHITIẾT', 'CHI TIẾTMÃHÀNG', 'CHITIET'],
        'SL ĐẶT HÀNG': ['SL', 'ĐẶTHÀNG', 'SLĐẶTHÀNG'],
        'NGÀY SX TỐI THIỂU': ['NGÀYSX', 'NGÀYSXTỐITHIỂU'],
        'HSD TỐI THIỂU': ['HSD', 'HSDTỐITHIỂU'],
        'ĐƠN GIÁ TỈ LỆ VAT': ['ĐƠNGIÁTỔNTỈLỆVATGIÁ', 'ĐƠNGIÁ', 'TỈLỆVAT'],
        'TỔNG CỘNG GIÁ TRỊ VAT': ['GCỘNGTRỊVAT', 'TỔNGCỘNGGIÁTRỊVAT', 'TRỊVAT', 'GIÁTRỊVAT']   
    }
    # 2. Gom dữ liệu về cột chuẩn
    for standard_name, keywords in mapping.items():
        # Tìm tất cả các cột thực tế đang có trong DF mà khớp với bộ từ khóa
        matched_cols = [col for col in tables.columns if any(kw.upper() in col for kw in keywords)]
        if matched_cols:
            # "Ép dẹp" các cột này: 
            # bfill(axis=1) sẽ lấp đầy NaN bằng giá trị của cột bên cạnh (từ phải sang trái)
            # .iloc[:, 0] lấy cột đầu tiên sau khi đã được lấp đầy giá trị
            tables[standard_name] = tables[matched_cols].bfill(axis=1).iloc[:, 0]
        else:
            # Nếu không tìm thấy cột nào khớp thì để trống
            tables[standard_name] = None

    '''Replace cho đoạn này'''
    # try:
    #     tables = tables.rename(columns=
    #         {
    #         'NGÀY SX TỐI\nTHIỂU': 'NGÀY SX TỐI THIỂU',
    #         'ĐƠN GIÁ TỔN\nTỈ LỆ VAT GIÁ': 'ĐƠN GIÁ_TỈ LỆ VAT_1',
    #         'G CỘNG\nTRỊ VAT': 'TỔNG CỘNG_GIÁ TRỊ VAT_1',
    #         'ĐƠN GIÁ\nTỈ LỆ VAT': 'ĐƠN GIÁ_TỈ LỆ VAT_2',
    #         'TỔNG CỘNG\nGIÁ TRỊ VAT': 'TỔNG CỘNG_GIÁ TRỊ VAT_2'
    #         }
    #     )
    # except:
    #     None

    # print(tables)
    '''Add 18.03.2026'''
    po_delivery_date_df = tables[['MA_DON_HANG', 'DELIVERY_DATE', 'FILE_PATH']].drop_duplicates().dropna()
    #-------------------
    # new_row = {'MA_DON_HANG': '359010022025', 'DELIVERY_DATE': '31/07/2025', 'FILE_PATH': 'D:\WORK\Projekte\Prj_Transform pdf_excel\Folder PO\Purchase Order_359010022024_1747119879612.pdf'}
    # po_delivery_date_df = pd.concat([po_delivery_date_df, pd.DataFrame([new_row])], ignore_index=True)
    #-------------------
    po_delivery_date_df = po_delivery_date_df.sort_values(by=['MA_DON_HANG', 'DELIVERY_DATE'], ascending=[True, True], ignore_index=True)
    po_delivery_date_df['MAPPING'] = po_delivery_date_df['MA_DON_HANG'] + '-' + po_delivery_date_df['DELIVERY_DATE']
    is_unique = po_delivery_date_df['MAPPING'].is_unique
    if not is_unique:
        duplicates = po_delivery_date_df[po_delivery_date_df.duplicated(subset=['MAPPING'], keep=False)]
        # print(duplicates)
        duplicates.drop(['FILE_PATH', 'MAPPING'], axis=1, inplace=True)
        duplicates['REASON'] = 'PO Number is duplicated'
        template_excel = duplicates
        flag = False
    else:
        # print('Ok')
        '''Khởi tạo template kết quả - excel + xử lý dữ liệu khi process xong pdf'''
        template_excel = pd.DataFrame(columns=['Số PO', 'STT', 'Mã SP 7 số', 'Mã SP 13 số', 'Tên sản phẩm', 'Số lượng', 'Đơn giá', '% Thuế', 'Giá trị sau VAT', 'Hạn sử dụng tối thiểu'])
        template_excel['Số PO'] = tables['MA_DON_HANG']
        template_excel['STT'] = template_excel.groupby(['Số PO']).cumcount()
        # template_excel['Ngày phân phối'] = tables['DELIVERY_DATE']
        template_excel['Mã SP 7 số'] = tables['CHI TIẾT MÃ HÀNG'].str[:7].str.replace('\n', '', regex=False)
        template_excel['Mã SP 13 số'] = tables['CHI TIẾT MÃ HÀNG'].str[8:21].str.replace('\n', '', regex=False)
        template_excel['Tên sản phẩm'] = tables['CHI TIẾT MÃ HÀNG'].str[21:].str.replace('\n', ' ', regex=False)
        template_excel['Số lượng'] = tables['SL ĐẶT HÀNG']
        template_excel['Hạn sử dụng tối thiểu'] = tables['HSD TỐI THIỂU']
        template_excel['Đơn giá'] = tables['ĐƠN GIÁ TỈ LỆ VAT'].str.split('\n').str[0]
        template_excel['% Thuế'] = tables['ĐƠN GIÁ TỈ LỆ VAT'].str.split('\n').str[1]
        template_excel['Giá trị sau VAT'] = tables['TỔNG CỘNG GIÁ TRỊ VAT'].str.split('\n').str[0]
        template_excel['Đơn giá'] = template_excel['Đơn giá'].astype(str).str.replace(',', '', regex=False).str.strip()
        template_excel['Đơn giá'] = pd.to_numeric(template_excel['Đơn giá'], errors='coerce').fillna(0).astype(int)
        template_excel['Giá trị sau VAT'] = template_excel['Giá trị sau VAT'].astype(str).str.replace(',', '', regex=False).str.strip()
        template_excel['Giá trị sau VAT'] = pd.to_numeric(template_excel['Giá trị sau VAT'], errors='coerce').fillna(0).astype(int)
        '''Lọc bỏ các hàng không liên quan'''
        template_excel['Số lượng'] = pd.to_numeric(template_excel['Số lượng'], errors='coerce')
        template_excel = template_excel.dropna(subset=['Số lượng'])
        template_excel = template_excel.astype({'Số lượng': int})
        template_excel = template_excel.astype({'Số PO': str, 'Mã SP 7 số': str, 'Mã SP 13 số': str, 'Số lượng': 'int64'})

        template_excel = template_excel.merge(po_delivery_date_df[['MA_DON_HANG', 'DELIVERY_DATE']], how='left', left_on='Số PO', right_on='MA_DON_HANG')
        template_excel = template_excel.rename(columns={'DELIVERY_DATE': 'Ngày phân phối'})
        template_excel.drop(['MA_DON_HANG'], axis=1, inplace=True)
        template_excel = template_excel[['Số PO', 'STT', 'Ngày phân phối', 'Mã SP 7 số', 'Mã SP 13 số', 'Tên sản phẩm', 'Số lượng', 'Đơn giá', '% Thuế', 'Giá trị sau VAT', 'Hạn sử dụng tối thiểu']]
        print('Created template excel - done')
        flag = True
    return template_excel, flag


#17.03.2026
# def result_path(flag):
#     # Lấy đường dẫn file python đang chạy hiện tại
#     current_file = os.path.abspath(__file__)
#     global current_address
#     current_address = os.path.dirname(current_file)
#     # Khởi tạo folder để lưu kết quả
#     folder_filename = os.path.join(os.path.dirname(sys.argv[0]), 'Data Exported')
#     global result_directory
#     result_directory = str(folder_filename)  # Khởi tạo biến result_directory ở mọi trường hợp
#     # Tạo thư mục nếu nó chưa tồn tại
#     if flag == 'TRUE':
#         # Tạo thư mục nếu nó chưa tồn tại
#         if not os.path.exists(result_directory):
#             os.makedirs(result_directory)
#     return result_directory, current_address


'''Tùy chỉnh theo streamlit_17.03.2026'''
# def func_execute(list_pdf):
#     # list_pdf lúc này là danh sách các file object từ Streamlit
#     final_template = func_main_process(list_pdf)
#     if final_template is not None:
#         print('Processed data - done')
#         return final_template
    

def func_execute(list_pdf):
    #danh sách các UploadedFile từ Streamlit
    temp_paths = []
    
    # BƯỚC QUAN TRỌNG: Lưu file vào thư mục tạm của server
    for uploaded_file in list_pdf:
        # Tạo file tạm và không tự xóa ngay (để hàm sau còn đọc được)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_paths.append(tmp.name) # Lưu đường dẫn thực (string) vào list

    try:
        #truyền list các ĐƯỜNG DẪN vào hàm xử lý chính
        final_template = func_main_process(temp_paths)
        if final_template is not None:
            print('Processed data - done')
            return final_template      
    except Exception as e:
        print(f"Error during processing: {e}")
        return None
    finally:
        #Dọn dẹp file tạm
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)
    return None
