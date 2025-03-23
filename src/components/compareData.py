import streamlit as st
import polars as pl
import pandas as pd
import os
from io import BytesIO


class compareData:
    @classmethod
    def about(cls):
        st.subheader("Read the Below Instructions:")
        st.markdown("""
                    Welcome to the **File Comparison Tool**! This tool compares two files cell by cell and generates output files with comparison results and null counts.

        ### Instructions:
        1. **Upload File 1 and File 2**:
        - Upload two files (CSV or Excel) to compare. Both files should have the same structure (same number of rows and columns).

        2. **Comparison**:
        - The tool will compare both files and generate:
            - A **Boolean Comparison File** showing **True** (match) or **False** (no match) for each cell.
            - A **Null Values Report** showing the number of **null values** in each file.

        3. **Download Results**:
        - Once the comparison is complete, download:
            - The **Boolean Comparison File** and the **Null Values Report**.

        4. **Notes**:
        - Ensure both files are structured identically for accurate comparison.

        Click **Compare Files** to start the process.
        """)

    @classmethod
    @st.dialog('Comparing Files')
    def process(cls):
        with st.spinner('Please Wait While we Process'):
            if st.session_state.filetoCompare1 and st.session_state.filetoCompare2:
                df1 = pl.read_excel(st.session_state.filetoCompare1,infer_schema_length=False)
                df2 = pl.read_excel(st.session_state.filetoCompare2,infer_schema_length=False)

                if df1.columns!= df2.columns:
                    st.error("Columns of Both Files Should be Same")
                    st.stop()

                elif df1.shape[0] != df2.shape[0]:
                    st.error("Rows of Both Files Should be Same")
                    st.stop()

                else:
                    compare = df1.with_columns([(df1[each] == df2[each]).alias(each) for each in df1.columns if each in df1.columns ])
                    compare = compare.with_columns(pl.arange(1,compare.height).alias("Row Number"))
                    compare = compare.to_pandas()
                    
                    nullCounts = {}
                    st.session_state.excel_buffer = BytesIO()
                    for each in df1.columns:
                        nullCounts[each] = {
                            f'{st.session_state.filetoCompare1.name}' : df1[each].is_null().sum(),
                            f'{st.session_state.filetoCompare2.name}' : df2[each].is_null().sum(),
                        }
                    nullCountDf = pd.DataFrame(nullCounts).transpose()
                    with pd.ExcelWriter(st.session_state.excel_buffer,engine='xlsxwriter') as writer:
                        compare.to_excel(writer,sheet_name='Comparison',index=False)
                        nullCountDf.to_excel(writer,sheet_name='NullCounts')

                    st.success("Please Close Dialog Box And Download the Results!")



    @classmethod
    def compare_data(cls):
        st.subheader("Select the Files Which You Want To Compare: ")
        st.session_state.filetoCompare1 = st.file_uploader('Select The Master File 1')
        st.session_state.filetoCompare2 = st.file_uploader('Select The Master File 2')
        


    def compare(cls):
        if 'cdPageIdx' not in st.session_state:
            st.session_state.cdPageIdx = 0
        if 'filetoCompare1' not in st.session_state:
            st.session_state.filetoCompare1 = None
        if 'filetoCompare2' not in st.session_state:
            st.session_state.filetoCompare2 = None
        if 'excel_buffer' not in st.session_state:
            st.session_state.excel_buffer = None
        
        
        
        pages = [compareData.about, compareData.compare_data]
        current_page = st.session_state.cdPageIdx
        pages[current_page]()

        navigation = st.columns(3)
        with navigation[2]:
            if current_page>0:
                if st.button('Previous',use_container_width=True):
                    st.session_state.cdPageIdx-=1
                    st.rerun()

            elif current_page<len(pages)-1:
                if st.button("Next",use_container_width=True):
                    st.session_state.cdPageIdx+=1
                    st.rerun()

        with navigation[0]:
            if st.session_state.excel_buffer is not None and current_page==1:
                if st.download_button('Download Results',data=st.session_state.excel_buffer,
                                      file_name=f'Compare_Results_{st.session_state.filetoCompare1.name}.xlsx',
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True):
                    st.session_state.excel_buffer=None
            elif st.session_state.excel_buffer is None:
                if st.session_state.filetoCompare1 and st.session_state.filetoCompare2:
                    if st.button('Compare Files',use_container_width=True):
                        compareData.process()
                        st.rerun()
                    