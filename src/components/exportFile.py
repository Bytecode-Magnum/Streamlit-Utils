import streamlit as st
import polars as pl
import os
from io import BytesIO
from datetime import datetime
import openpyxl
import psycopg2 as pg
from dotenv import load_dotenv
load_dotenv()


def _get_connection():
    try:
        conn = pg.connect(database=st.session_state.credentials['database'],user=st.session_state.credentials['user'],
                          password=st.session_state.credentials['password'],
                          port=st.session_state.credentials['port'],
                          host=st.session_state.credentials['host'])
        return conn
    except Exception as e:
        st.error(f"Unable to Create Conenction Due to {e}")

def _get_cursor(conn):
    return conn.cursor()


class exportFile:
    @classmethod
    def About(cls):
        st.title("About Export File to Database")

        # Overview
        st.subheader("Project Overview")
        st.markdown("""
            **Export File to Database** is a tool for seamlessly exporting data from files (Excel/CSV) to databases. 
            It automates the process, ensuring all fields are transferred as character varying data types for consistency.
        """)

        # Purpose and Goals
        st.subheader("Purpose and Goals")
        st.markdown("""
            The tool simplifies the process of importing files into a database by:
            - **Automating data export** from files to databases.
            - **Ensuring data consistency** with character varying data types.
        """)

        # Key Features
        st.subheader("Key Features")
        st.markdown("""
            - **File Selection**: Upload your Excel or CSV files.
            - **Database Selection**: Choose the target database.
            - **Automated Export**: Fields are automatically converted and exported to the database as character varying.
        """)

        # How It Works
        st.subheader("How It Works")
        st.markdown("""
            1. Upload your files.
            2. Select the target database.
            3. The tool automatically exports data, converting all fields to character varying.
        """)

        # Technologies Used
        st.subheader("Technologies Used")
        st.markdown("""
            - **Streamlit**: User interface for file and database selection.
            - **Psycopg2**: Manages database connections.
            - **Python**: Powers the logic and export process.
        """)

        # Summary
        st.subheader("Summary")
        st.markdown("""
            **Edport File to Database** streamlines data transfer from files to databases, ensuring efficiency and consistency.
        """)

    @classmethod
    def chooseFiles(cls):
        st.session_state.df = None
        st.subheader("Just Select File and Database, and export your file Database in No-time!")
        dbChoice = st.selectbox('Choose Database',['SADB','TailSpend'])
        if dbChoice == 'TailSpend':
            st.session_state.credentials['user'] = os.getenv('virtuosi_username')
            st.session_state.credentials['database'] = os.getenv('virtuosi_database')
            st.session_state.credentials['host'] = os.getenv('virtuosi_host')
            st.session_state.credentials['port'] = os.getenv('virtuosi_port')
            st.session_state.credentials['password'] = os.getenv('virtuosi_password')

        elif dbChoice == 'SADB':
            st.session_state.credentials['user'] = os.getenv('sadb_username')
            st.session_state.credentials['database'] = os.getenv('sadb_database')
            st.session_state.credentials['host'] = os.getenv('sadb_host')
            st.session_state.credentials['port'] = os.getenv('sadb_port')
            st.session_state.credentials['password'] = os.getenv('sadb_password')

        st.session_state.fileSelected = st.file_uploader('Choose the File Which You Want to Upload')
        st.session_state.tableName = st.text_input('Enter the Table Name')
        if st.session_state.fileSelected and st.session_state.tableName:
            if st.session_state.fileSelected.name.lower().endswith(".xlsx"):
                wb = openpyxl.load_workbook(st.session_state.fileSelected,read_only=True)
                st.session_state.wbName = st.selectbox("Select The sheet Name",options=wb.sheetnames)


        
    @staticmethod
    @st.dialog('Uploading File')
    def export(file):
        with st.spinner('Exporting File, Please Wait'):
            try:
                if file.name.lower().endswith('.csv'):
                    df = pl.read_csv(file,infer_schema_length=False)
                    st.success(f'File Read, Total Records: {df.shape[0]}, Total Columns: {df.shape[1]}')

                elif file.name.lower().endswith(".xlsx"):
                    df = pl.read_excel(file,infer_schema_length=False,sheet_name=st.session_state.wbName)
                    st.success(f'File Read, Total Records: {df.shape[0]}, Total Columns: {df.shape[1]}')

                else:
                    st.error(f'File type {file.type} not allowed, Expected Type Excel/Csv')
                    return 
                
                columns = ",".join([f'"{col}" TEXT' for col in df.columns])
                create_table_query  = f'CREATE TABLE "{st.session_state.tableName}" \n (' + columns + ')'
                conn = _get_connection()
                cursor = _get_cursor(conn)
                try:
                    cursor.execute(create_table_query)
                    conn.commit()
                except Exception as e:
                    st.error(f'Unable to Created Table Due to {e}: {datetime.now()}: {st.session_state.tableName}')
                    conn.rollback()
                    st.stop()
                
                try:
                    csv_buffer = BytesIO()
                    df.write_csv(csv_buffer,include_header=True)
                    csv_buffer.seek(0)

                except Exception as e:
                    st.error(f'Unable to Export Data To CSV buffer Due to {e}')
                
                try:
                    start_time = datetime.now().time()
                    cursor.copy_expert(f'COPY "{st.session_state.tableName}" FROM STDIN WITH CSV HEADER',csv_buffer)
                    conn.commit()
                    end_time = datetime.now().time()
                    start_time = datetime.combine(datetime.today(), start_time)
                    end_time = datetime.combine(datetime.today(), end_time)
                    time_difference = end_time - start_time
                    seconds_taken = time_difference.total_seconds()
                    st.success(f"File Exported To Database Successfully!")
                    st.caption(f'Table: {st.session_state.tableName}, Total Time Taken: {seconds_taken}')

                except Exception as e:
                    st.error(f"Unable to Export data To database due to {e}")
                    conn.rollback()
                    return  
                finally:
                    conn.close()


            except Exception as e:
                st.error(f"Unable to Load File Due to {e}")
        
        
# TODO Add temp as prefix and date as suffix


    
    def Exporter(self):
        if 'efPageIdx' not in st.session_state:
            st.session_state.efPageIdx = 0
        if 'wbName' not in st.session_state:
            st.session_state.wbName = None
        if 'fileSelected' not in st.session_state:
            st.session_state.fileSelected = None
        if 'credentials' not in st.session_state:  
            st.session_state.credentials = {}


        pages = [exportFile.About,exportFile.chooseFiles]
        current_page = st.session_state.efPageIdx
        pages[current_page]()
         
        navigation  = st.columns(3)
        with navigation[2]:
            if st.session_state.efPageIdx<len(pages)-1 and st.button('Next',use_container_width=True):
                st.session_state.efPageIdx +=1
                st.rerun()

            elif st.session_state.efPageIdx==len(pages)-1:
                if st.button('Export',use_container_width=True,disabled=not st.session_state.fileSelected):
                    exportFile.export(st.session_state.fileSelected)
            
        with navigation[0]:
            if st.session_state.efPageIdx>0 and st.button('Previous',use_container_width=True):
                st.session_state.efPageIdx -= 1
                st.rerun()

