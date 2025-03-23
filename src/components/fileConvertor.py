import streamlit as st
import polars as pl
from datetime import datetime
import csv
import zipfile
from io import BytesIO

delimeter_dict = {
    'Comma':',',
    'Pipe':'|'
}



class fileConvertor:
    @classmethod
    def about(cls):
        st.title("File Converter Tool")
        st.subheader("Project Overview")
        st.markdown("""
            **File Converter Tool** is designed to help users effortlessly convert files between different formats, specifically from Excel to CSV and vice versa. 
            By simply selecting the source file and choosing the desired output format, users can quickly and easily convert their files to meet their needs.
        """)
        st.subheader("Purpose and Goals")
        st.markdown("""
            The File Converter Tool aims to simplify the process of file format conversion by:
            - **Allowing users to select the source file** and choose between Excel and CSV formats.
            - **Quickly converting files** from Excel to CSV or CSV to Excel, without the need for manual adjustments.
            - **Ensuring seamless conversion** with a user-friendly interface for smooth operation.
        """)

    @classmethod
    def process(cls):
        st.subheader("File Convertor:")
        selectType = st.radio("Select the Type of File you want to Convert",['Excel to CSV','CSV to Excel'],index=0)
        if selectType == 'Excel to CSV':
                st.session_state.filetoConvert = st.file_uploader("Select the File Which you want to Convert",type=['xlsx','XLSX'],accept_multiple_files=True)
        else:
            st.session_state.delimeter = st.radio("Select the Delimeter",['Comma', 'Pipe'],index=0)
            st.session_state.filetoConvert = st.file_uploader("Select the File Which you want to Convert",type=['csv','CSV'],accept_multiple_files=True)

        
    @classmethod
    @st.dialog("Converting Files")
    def convert(cls):
        with st.spinner("PLEASE BE PATIENT, WHILE WE PROCESS"):
            st.session_state.zipBuffer = BytesIO()
            with zipfile.ZipFile(st.session_state.zipBuffer,'w',zipfile.ZIP_DEFLATED) as zip:
                for file in st.session_state.filetoConvert:
                    if file.name.lower().endswith(".csv"):
                        buffer = BytesIO()
                        delimeter = delimeter_dict.get(st.session_state.delimeter)
                        df = pl.read_csv(file, separator=delimeter,infer_schema_length=False)
                        df.write_excel(buffer,autofilter=False,autofit=True)
                        buffer.seek(0)
                        zip.writestr(file.name.replace(".csv",".xlsx"),buffer.getvalue())
                        del(buffer)

                    elif file.name.lower().endswith(".xlsx"):
                        buffer = BytesIO()
                        df = pl.read_excel(file, infer_schema_length=False)
                        df.write_csv(buffer)
                        buffer.seek(0)
                        zip.writestr(file.name.replace(".xlsx",".csv"),buffer.getvalue())
                        del(buffer)
            st.session_state.zipBuffer.seek(0)


    @classmethod
    def reset(cls):
        st.session_state.zipBuffer = None


    @classmethod
    def convertor(cls):
        if 'fcPageIdx' not in st.session_state:
            st.session_state.fcPageIdx = 0
        if 'filetoConvert' not in st.session_state:
            st.session_state.filetoConvert = []
        if 'delimeter' not in st.session_state:
            st.session_state.delimeter = None
        if 'zipBuffer' not in st.session_state:
            st.session_state.zipBuffer = None

        
        pages = [fileConvertor.about,fileConvertor.process]
        current_page = st.session_state.fcPageIdx
        pages[current_page]()

        navigation = st.columns(3)
        with navigation[2]:
            if current_page<len(pages)-1:
                if st.button("Next",use_container_width=True):
                    st.session_state.fcPageIdx += 1
                    st.rerun()

            if current_page ==1:
                if st.session_state.zipBuffer is not None and len(st.session_state.filetoConvert)!=0:
                    if st.download_button("Download",use_container_width=True,data=st.session_state.zipBuffer,file_name="converted_files.zip"):
                        fileConvertor.reset()
                        st.rerun()
                elif st.session_state.zipBuffer is None and len(st.session_state.filetoConvert)!=0:
                    if st.button("Convert",use_container_width=True):
                        fileConvertor.convert()
                        st.rerun()



        with navigation[0]:
            if current_page>0:
                if st.button("Previous",use_container_width=True):
                    st.session_state.fcPageIdx -= 1
                    st.rerun()
    