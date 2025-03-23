from typing import List, Optional
import polars as pl
import streamlit as st
from datetime import datetime


class Dialog:
    @staticmethod
    @st.dialog('Alert!')
    def show_error(message: str):
        st.error(message, icon='😭')

    @staticmethod
    @st.dialog('Warning!')
    def show_warning(message: str):
        st.warning(message)

    @staticmethod
    @st.dialog("Success!")
    def show_success(message: str):
        st.success(message, icon='🎉')

    @staticmethod
    @st.dialog('Read File')
    def read_file(file):
        with st.spinner('Reading File, Please Wait'):
            try:
                if file.name.lower().endswith('.csv'):
                    df = pl.read_csv(file,infer_schema_length=False)
                    st.success(f'File Read, Total Records: {df.shape[0]}, Total Columns: {df.shape[1]}')
                    return True,df

                elif file.name.lower().endswith(".xlsx"):
                    df = pl.read_excel(file,infer_schema_length=False)
                    st.success(f'File Read, Total Records: {df.shape[0]}, Total Columns: {df.shape[1]}')
                    return True, df
                
                else:
                    st.error(f'File type {file.type} not allowed, Expected Type Excel/Csv')
                    return None

            except Exception as e:
                st.error(f"Unable to Load File Due to {e}")
                return None