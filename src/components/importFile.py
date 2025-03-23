import streamlit as st
import polars as pl
import os
from io import BytesIO
from datetime import datetime
import openpyxl
import psycopg2 as pg
from dotenv import load_dotenv
import numpy as np
import pandas as pd
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

class importFile:
    
    @classmethod
    def about(cls):
        st.title("Export File from Database")
        st.subheader("Project Overview")
        st.markdown("""
            **Export File from Database** is a tool designed to effortlessly import data from external files (Excel/CSV) into specific database tables. 
            By simply selecting the table name and the desired column names, users can quickly map and import all relevant data into the database.
        """)
        st.subheader("Purpose and Goals")
        st.markdown("""
            The tool streamlines the process of importing data into a database by:
            - **Allowing users to select the target table and columns** for easy mapping.
            - **Automating data import** from files (Excel/CSV) to the specified database columns.
            - **Ensuring seamless data integration** into the database for further processing.
        """)
    @classmethod
    def chooseTable(cls):
        st.subheader('Select the Database Name and Table Name From Database')
        choice = st.selectbox('Choose Database',['SADB','TailSpend'],index=0)
        if choice!=st.session_state.dbChoice:
            st.session_state.dbChoice = choice
            importFile.getTables()

        if st.session_state.dbChoice is not None:
                # if st.session_state.dbChoice == 'SADB':
                    selectedTable = st.selectbox('Select the Table Name',st.session_state.tables,index=None)
                    if selectedTable!=st.session_state.selectedTable:
                        st.session_state.selectedTable = selectedTable
                        importFile.getColumns()

        else:
            st.caption('Please Select the Database Name')

        if st.session_state.selectedTable is not None:
            st.session_state.selectedColumns = st.multiselect('Select the Columns to Import',options=st.session_state.dbColumns  )
            st.caption("Total Transactions in Table: "+str(st.session_state.totalTransactions))
            if not st.session_state.selectedColumns:
                st.caption('Please Select the Columns to Import')

    @classmethod
    @st.dialog('Please Wait',width='small')
    def getColumns(cls):
        with st.spinner("Please Wait File We Fetch Table Schema"):
            st.write("Selected Table: ",st.session_state.selectedTable)
            connection = _get_connection()
            cursor = _get_cursor(connection)
            query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{st.session_state.selectedTable}'"
            cursor.execute(query)
            columns = cursor.fetchall()
            columns = [each[0] for each in columns]
            columns = np.sort(columns)
            st.session_state.dbColumns = columns
            query2 = f'''SELECT COUNT(*) FROM "{st.session_state.selectedTable}"'''
            cursor.execute(query2)
            result2 = cursor.fetchall()
            st.session_state.totalTransactions = result2[0][0]
            st.success('Table Schema Fetched Successfully')
            cursor.close()  
            connection.close()

    @classmethod
    @st.dialog('Processing',width='small')
    def getTables(cls):
        with st.spinner("Fetching Database and Table Schema, Please Wait"):
            st.write("Select Database: ",st.session_state.dbChoice)
            if st.session_state.dbChoice == 'TailSpend':
                st.session_state.credentials['user'] = os.getenv('virtuosi_username')
                st.session_state.credentials['database'] = os.getenv('virtuosi_database')
                st.session_state.credentials['host'] = os.getenv('virtuosi_host')
                st.session_state.credentials['port'] = os.getenv('virtuosi_port')
                st.session_state.credentials['password'] = os.getenv('virtuosi_password')

            elif st.session_state.dbChoice == 'SADB':
                st.session_state.credentials['user'] = os.getenv('sadb_username')
                st.session_state.credentials['database'] = os.getenv('sadb_database')
                st.session_state.credentials['host'] = os.getenv('sadb_host')
                st.session_state.credentials['port'] = os.getenv('sadb_port')
                st.session_state.credentials['password'] = os.getenv('sadb_password')
            st.session_state.tables = []
            connection = _get_connection()
            cursor = _get_cursor(connection)
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            result = cursor.fetchall()
            tables = [each[0] for each in result]
            tables = np.sort(tables)
            st.session_state.tables = tables
            query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{st.session_state.tables[0]}'"
            cursor.execute(query)
            columns = cursor.fetchall()
            columns = [each[0] for each in columns]
            columns = np.sort(columns)
            st.session_state.dbColumns = columns
            st.success('Tables Schema Fetched From Database')
            cursor.close()  
            connection.close()

    # Function to export data
    @classmethod
    @st.dialog("Exporting Data")
    def export_data(cls):
        with st.spinner("PLEASE BE PATIENT, WHILE WE EXPORT DATA"):
            # Initialize buffer for exporting data
            st.session_state.bufferData = BytesIO()

            column_info = st.session_state.selectedColumns
            db_table_name = st.session_state.selectedTable
            connection = _get_connection()
            cursor = connection.cursor()

            # Set limit (batch size) for each query

            # Track the start time
            start_time = datetime.now()

            try:
                columns = ",".join([f'"{col}"' for col in column_info])
                query = f'''
                COPY (SELECT {columns} FROM "{db_table_name}") TO STDOUT WITH CSV HEADER
            '''
            
            # Execute COPY command and write to the buffer
                cursor.copy_expert(query, st.session_state.bufferData)
                end_time = datetime.now()
                time_taken = (end_time - start_time).total_seconds()
                st.caption(f'Table: {db_table_name}, Total Time Taken: {time_taken} seconds')
                print(f'Table: {db_table_name}, Total Time Taken: {time_taken} seconds')
                st.success("Data Exported Successfully!")

            except Exception as e:
                st.error(f"Error occurred: {e}")
                return None

            finally:
                # Close the cursor and connection
                cursor.close()
                connection.close()




    @classmethod
    def importer(cls):
        if 'ifPageIdx' not in st.session_state:
            st.session_state.ifPageIdx = 0
        if 'tables' not in st.session_state:
            st.session_state.tables = []
        if 'dbColumns' not in st.session_state:
            st.session_state.dbColumns = []
        if 'selectedColumns' not in st.session_state:
            st.session_state.selectedColumns = []
        if 'credentials' not in st.session_state:  
            st.session_state.credentials = {}
        if 'dbChoice' not in st.session_state:
            st.session_state.dbChoice = None
        if 'selectedTable' not in st.session_state:
            st.session_state.selectedTable = None
        if 'bufferData' not in st.session_state:
            st.session_state.bufferData = None
        if 'totalTransactions' not in st.session_state:
            st.session_state.totalTransactions = None

        pages = [importFile.about,importFile.chooseTable]
        current_page = st.session_state.ifPageIdx
        pages[current_page]()

        navigation = st.columns(3)
        with navigation[2]:
            if current_page<len(pages)-1:
                if st.button('Next',use_container_width=True):
                    st.session_state.ifPageIdx += 1
                    st.rerun()

            if current_page==1:
                if st.session_state.tables is not None and st.session_state.dbChoice is not None and len(st.session_state.selectedColumns)!=0 and st.session_state.bufferData is None:
                    if st.button("Export Data",use_container_width=True):
                        importFile.export_data()
                        st.rerun()
                elif st.session_state.bufferData is not None:
                    time = datetime.now().strftime("%Y_%m_%d_%H_%M")
                    file_name = f"temp_{st.session_state.selectedTable}_extract_{time}.csv"
                    if st.download_button('Download File', st.session_state.bufferData, file_name=file_name, 
                                           mime='text/csv',on_click=importFile.reset,use_container_width=True):
                        st.rerun()

        with navigation[0]:
            if current_page>0:
                if st.button("Previous",use_container_width=True):
                    st.session_state.ifPageIdx -= 1
                    st.rerun()
    @classmethod
    def reset(cls):
        st.session_state.bufferData = None
            