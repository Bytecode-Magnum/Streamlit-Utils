import streamlit as st
import polars as pl

from datetime import datetime,time
import io

class appendFiles:
    @classmethod
    def about(cls):
        st.markdown("""
                    #### Welcome to the **Data Merging Tool**! This tool allows you to upload multiple files, merge their data into one, and add an extra column at the end to identify the file source. Follow these steps to get started:

                    #### Instructions:
                    1. **File Selection**:
                        - Use the file upload option to select multiple files for merging.
                        - You can upload CSV, Excel, or similar file types supported by the tool.
                        - Example: Select files like `sales_data_2025.csv`, `customer_data.xlsx`, etc.

                    2. **Data Merging**:
                        - After selecting the files, the tool will automatically combine all the data from the files into one single file.
                        - Each row of data from the different files will be appended together.

                    3. **File Identification**:
                        - An extra column, named **'File Name'**, will be added to the merged dataset.
                        - This column will contain the name of the file from which each row of data originated. This helps identify and trace the data to its source.

                    4. **Download the Merged File**:
                        - After the files are merged, you will be able to download the final file with all the data combined and the **'File Name'** column included.
                        - Example: The merged file might look like this:
                          ```
                          | Column1 | Column2 | File Name |
                          |---------|---------|-----------|
                          | Data1   | Data2   | sales_data_2025.csv |
                          | Data3   | Data4   | customer_data.xlsx  |
                          ```

                    ### Notes:
                    - Ensure that all files you upload have the same structure (same columns) to prevent errors during the merge process.
                    - You can upload as many files as needed, and the tool will handle merging them for you.
                    - If you encounter any issues or errors, please double-check the file formats and structure.

                    ### Example:
                    - **Files Selected**: `sales_data_2025.csv`, `customer_data.xlsx`
                    - **Merged File Output**: `merged_data_with_file_identification.csv`
                    - The resulting file will contain data from both files, with an added **'File Name'** column to identify where each row came from.

                    Happy Data Merging!
                    """, unsafe_allow_html=True)


    @classmethod
    def fileUploader(cls):
        st.subheader("Choose the File Which you want to append")
        st.session_state.files = st.file_uploader('Select the Excel/Csv Files',accept_multiple_files=True)

    @classmethod
    @st.dialog('Processing')
    def process(cls):
        with st.spinner('Please Wait While we Process...'):
            appendedFiles = []
            st.session_state.buffer = io.BytesIO()
            for file in st.session_state.files:
                if file.name.lower().endswith('.csv'):
                    df = pl.read_csv(file, infer_schema_length=False)
                    if len(appendedFiles) != 0:
                        requiredColumns = appendedFiles[0].columns.copy()
                        requiredColumns.remove("File Name")
                        unMatches = []
                        if df.columns != requiredColumns:
                            for each in df.columns:
                                if each not in requiredColumns:
                                    unMatches.append(each)
                            st.error(f'Column Structure Not Matched For Files {file.name}, Revalidate the File Structure and Select Files Again. Following Columns {unMatches} not found in file {file.name}')
                            return
                    
                    df = df.with_columns(pl.lit(file.name.lower().replace('.csv', '').title()).alias("File Name"))
                    st.success("Read File: {}".format(file.name))
                    appendedFiles.append(df)
                    del(df)
                
                elif file.name.lower().endswith('.xlsx'):
                    df = pl.read_excel(file, infer_schema_length=False)
                    if len(appendedFiles) != 0:
                        requiredColumns = appendedFiles[0].columns.copy()
                        requiredColumns.remove("File Name")
                        unMatches = []
                        if df.columns != requiredColumns:
                            for each in requiredColumns:
                                if each not in df.columns:
                                    unMatches.append(each)
                            st.error(f'Column Structure Not Matched For Files {file.name}, Revalidate the File Structure and Select Files Again. Following Column {unMatches} not found in file {file.name}')
                            return
                    
                    df = df.with_columns(pl.lit(file.name.lower().replace('.xlsx', '').title()).alias("File Name"))
                    st.success("Read File: {}".format(file.name))
                    appendedFiles.append(df)
                    del(df)
                else:
                    st.warning(f'Skipping Append {file.name}, Invalid File Format {file.type}')
                    pass
            
            master = pl.concat(appendedFiles, how='vertical')
            # Store the processed data in session state
            st.session_state.processed_data = master
            st.session_state.file_size_large = master.shape[0] >= 600000
            if st.session_state.file_size_large:
                master.write_csv(st.session_state.buffer)
                st.success("Files Appended Successfully!")
                del(master)
                del(appendedFiles)   
            else:
                master.write_excel(st.session_state.buffer)
                st.success("Files Appended Successfully!")
                del(master)
                del(appendedFiles)         

    @classmethod
    def append(cls):
        if 'afPageIdx' not in st.session_state:
            st.session_state.afPageIdx = 0
        if 'file' not in st.session_state:
            st.session_state.file = []
        if 'buffer' not in st.session_state:
            st.session_state.buffer = None
        
        pages  = [appendFiles.about,appendFiles.fileUploader]
        current_page = st.session_state.afPageIdx
        pages[current_page]()

        navigation = st.columns(3)
        with navigation[2]:
            if current_page < len(pages) - 1:
                if st.button("Next", use_container_width=True):
                    st.session_state.afPageIdx += 1
                    st.rerun()
            elif current_page == len(pages) - 1:
                if len(st.session_state.files)!=0 and st.session_state.buffer is None:
                    if st.button('Append File', use_container_width=True):
                        appendFiles.process()
                        st.rerun()
                elif st.session_state.buffer is not None:
                    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if st.session_state.file_size_large:
                        if st.download_button('Download File', st.session_state.buffer, file_name=f'Appended File Master {time}.csv', 
                                           mime='text/csv',on_click=appendFiles.reset,use_container_width=True):
                            st.rerun()
                    else:
                        if st.download_button('Download File', st.session_state.buffer, file_name=f'Appended File Master {time}.xlsx', 
                                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                           on_click=appendFiles.reset,use_container_width=True):
                            st.rerun()

        with navigation[0]:
            if current_page > 0:
                if st.button("Previous", use_container_width=True):
                    st.session_state.afPageIdx -= 1
                    st.rerun()

    def reset():
        st.session_state.buffer = None