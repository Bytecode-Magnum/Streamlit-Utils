import streamlit as st
import subprocess
import os
import sys
from src.components.conversionRate import currencyConversion
from src.components.appendFiles import appendFiles
from src.components.exportFile import exportFile
from src.components.compareData import compareData
from src.components.importFile import importFile
from src.components.fileConvertor import fileConvertor

st.set_page_config(layout='wide',page_title='Simfoni Utils')

    #: navigation bar to navigate to different modules of DAD

def get_resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


def main():
    add_selectbox = st.sidebar.image('./src/assets/Simfoni.com-Logo-removebg-preview.png')

    option = st.sidebar.radio('Select a Task',['Currency Conversion','Save to Database','Append Files','Validate Files','Export Database Table','File Convertor'],index=0)
    st.session_state.current_page = option
    if st.session_state.current_page == 'Currency Conversion':
        convertor = currencyConversion()
        convertor.Convertor()

    elif st.session_state.current_page == 'Save to Database':
        exporter = exportFile()
        exporter.Exporter()

    elif st.session_state.current_page == 'Append Files':
        append = appendFiles()
        append.append()

    elif st.session_state.current_page == 'Validate Files':
        compare = compareData()
        compare.compare()

    elif st.session_state.current_page == 'Export Database Table':
        importfile = importFile()
        importfile.importer()

    elif st.session_state.current_page == 'File Convertor':
        convertorFile = fileConvertor()
        convertorFile.convertor()


if __name__ == '__main__':
    # For development/direct running
    if getattr(sys, 'frozen', False):
        # We are running in a bundle
        bundle_dir = os.path.dirname(sys.executable)
        # Change to the appropriate working directory if needed
        os.chdir(bundle_dir)
        
    # Use this approach instead of streamlit.web.cli for better exe compatibility
    app_path = get_resolve_path("app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path, "--global.developmentMode=False"])