import streamlit as st
from datetime import datetime
import polars as pl
import pandas as pd
import time
import requests
import io

api_key = '2878b9747043b793ac3d26449c8fb6c4'
all_currencies = {'AFN - Afghan Afghani': 'AFN',
                  'ALL - Albanian Lek': 'ALL',
                  'AMD - Armenian Dram': 'AMD',
                  'AOA - Angolan Kwanza': 'AOA',
                  'ARS - Argentine Peso': 'ARS',
                  'AUD - Australian Dollar': 'AUD',
                  'AWG - Aruban Florin': 'AWG',
                  'AZN - Azerbaijani Manat': 'AZN',
                  'DZD - Algerian Dinar': 'DZD',
                  'BAM - Bosnia-Herzegovina Convertible Mark': 'BAM',
                  'BBD - Barbadian Dollar': 'BBD',
                  'BDT - Bangladeshi Taka': 'BDT',
                  'BGN - Bulgarian Lev': 'BGN',
                  'BHD - Bahraini Dinar': 'BHD',
                  'BIF - Burundian Franc': 'BIF',
                  'BMD - Bermudan Dollar': 'BMD',
                  'BND - Brunei Dollar': 'BND',
                  'BOB - Bolivian Boliviano': 'BOB',
                  'BRL - Brazilian Real': 'BRL',
                  'BSD - Bahamian Dollar': 'BSD',
                  'BTC - Bitcoin': 'BTC',
                  'BTN - Bhutanese Ngultrum': 'BTN',
                  'BWP - Botswanan Pula': 'BWP',
                  'BYR - Belarusian Ruble': 'BYR',
                  'BZD - Belize Dollar': 'BZD',
                  'GBP - British Pound Sterling': 'GBP',
                  'CAD - Canadian Dollar': 'CAD',
                  'CDF - Congolese Franc': 'CDF',
                  'CLF - Chilean Unit of Account (UF)': 'CLF',
                  'CLP - Chilean Peso': 'CLP',
                  'CNY - Chinese Yuan': 'CNY',
                  'COP - Colombian Peso': 'COP',
                  'CRC - Costa Rican Colón': 'CRC',
                  'CUC - Cuban Convertible Peso': 'CUC',
                  'CUP - Cuban Peso': 'CUP',
                  'CVE - Cape Verdean Escudo': 'CVE',
                  'CZK - Czech Republic Koruna': 'CZK',
                  'HRK - Croatian Kuna': 'HRK',
                  'KHR - Cambodian Riel': 'KHR',
                  'KMF - Comorian Franc': 'KMF',
                  'KYD - Cayman Islands Dollar': 'KYD',
                  'XAF - CFA Franc BEAC': 'XAF',
                  'XOF - CFA Franc BCEAO': 'XOF',
                  'XPF - CFP Franc': 'XPF',
                  'DJF - Djiboutian Franc': 'DJF',
                  'DKK - Danish Krone': 'DKK',
                  'DOP - Dominican Peso': 'DOP',
                  'EGP - Egyptian Pound': 'EGP',
                  'ERN - Eritrean Nakfa': 'ERN',
                  'ETB - Ethiopian Birr': 'ETB',
                  'EUR - Euro': 'EUR',
                  'XCD - East Caribbean Dollar': 'XCD',
                  'FJD - Fijian Dollar': 'FJD',
                  'FKP - Falkland Islands Pound': 'FKP',
                  'GEL - Georgian Lari': 'GEL',
                  'GGP - Guernsey Pound': 'GGP',
                  'GHS - Ghanaian Cedi': 'GHS',
                  'GIP - Gibraltar Pound': 'GIP',
                  'GMD - Gambian Dalasi': 'GMD',
                  'GNF - Guinean Franc': 'GNF',
                  'GTQ - Guatemalan Quetzal': 'GTQ',
                  'GYD - Guyanaese Dollar': 'GYD',
                  'XAU - Gold (troy ounce)': 'XAU',
                  'HKD - Hong Kong Dollar': 'HKD',
                  'HNL - Honduran Lempira': 'HNL',
                  'HTG - Haitian Gourde': 'HTG',
                  'HUF - Hungarian Forint': 'HUF',
                  'IDR - Indonesian Rupiah': 'IDR',
                  'ILS - Israeli New Sheqel': 'ILS',
                  'INR - Indian Rupee': 'INR',
                  'IQD - Iraqi Dinar': 'IQD',
                  'IRR - Iranian Rial': 'IRR',
                  'ISK - Icelandic Króna': 'ISK',
                  'JEP - Jersey Pound': 'JEP',
                  'JMD - Jamaican Dollar': 'JMD',
                  'JOD - Jordanian Dinar': 'JOD',
                  'JPY - Japanese Yen': 'JPY',
                  'KES - Kenyan Shilling': 'KES',
                  'KGS - Kyrgystani Som': 'KGS',
                  'KWD - Kuwaiti Dinar': 'KWD',
                  'KZT - Kazakhstani Tenge': 'KZT',
                  'LAK - Laotian Kip': 'LAK',
                  'LBP - Lebanese Pound': 'LBP',
                  'LRD - Liberian Dollar': 'LRD',
                  'LSL - Lesotho Loti': 'LSL',
                  'LTL - Lithuanian Litas': 'LTL',
                  'LVL - Latvian Lats': 'LVL',
                  'LYD - Libyan Dinar': 'LYD',
                  'IMP - Manx pound': 'IMP',
                  'MAD - Moroccan Dirham': 'MAD',
                  'MDL - Moldovan Leu': 'MDL',
                  'MGA - Malagasy Ariary': 'MGA',
                  'MKD - Macedonian Denar': 'MKD',
                  'MMK - Myanma Kyat': 'MMK',
                  'MNT - Mongolian Tugrik': 'MNT',
                  'MOP - Macanese Pataca': 'MOP',
                  'MRO - Mauritanian Ouguiya': 'MRO',
                  'MUR - Mauritian Rupee': 'MUR',
                  'MVR - Maldivian Rufiyaa': 'MVR',
                  'MWK - Malawian Kwacha': 'MWK',
                  'MXN - Mexican Peso': 'MXN',
                  'MYR - Malaysian Ringgit': 'MYR',
                  'MZN - Mozambican Metical': 'MZN',
                  'ANG - Netherlands Antillean Guilder': 'ANG',
                  'BYN - New Belarusian Ruble': 'BYN',
                  'KPW - North Korean Won': 'KPW',
                  'NAD - Namibian Dollar': 'NAD',
                  'NGN - Nigerian Naira': 'NGN',
                  'NIO - Nicaraguan Córdoba': 'NIO',
                  'NOK - Norwegian Krone': 'NOK',
                  'NPR - Nepalese Rupee': 'NPR',
                  'NZD - New Zealand Dollar': 'NZD',
                  'TWD - New Taiwan Dollar': 'TWD',
                  'OMR - Omani Rial': 'OMR',
                  'PAB - Panamanian Balboa': 'PAB',
                  'PEN - Peruvian Nuevo Sol': 'PEN',
                  'PGK - Papua New Guinean Kina': 'PGK',
                  'PHP - Philippine Peso': 'PHP',
                  'PKR - Pakistani Rupee': 'PKR',
                  'PLN - Polish Zloty': 'PLN',
                  'PYG - Paraguayan Guarani': 'PYG',
                  'QAR - Qatari Rial': 'QAR',
                  'RON - Romanian Leu': 'RON',
                  'RUB - Russian Ruble': 'RUB',
                  'RWF - Rwandan Franc': 'RWF',
                  'CHF - Swiss Franc': 'CHF',
                  'KRW - South Korean Won': 'KRW',
                  'LKR - Sri Lankan Rupee': 'LKR',
                  'RSD - Serbian Dinar': 'RSD',
                  'SAR - Saudi Riyal': 'SAR',
                  'SBD - Solomon Islands Dollar': 'SBD',
                  'SCR - Seychellois Rupee': 'SCR',
                  'SDG - Sudanese Pound': 'SDG',
                  'SEK - Swedish Krona': 'SEK',
                  'SGD - Singapore Dollar': 'SGD',
                  'SHP - Saint Helena Pound': 'SHP',
                  'SLL - Sierra Leonean Leone': 'SLL',
                  'SOS - Somali Shilling': 'SOS',
                  'SRD - Surinamese Dollar': 'SRD',
                  'STD - São Tomé and Príncipe Dobra': 'STD',
                  'SVC - Salvadoran Colón': 'SVC',
                  'SYP - Syrian Pound': 'SYP',
                  'SZL - Swazi Lilangeni': 'SZL',
                  'WST - Samoan Tala': 'WST',
                  'XAG - Silver (troy ounce)': 'XAG',
                  'XDR - Special Drawing Rights': 'XDR',
                  'ZAR - South African Rand': 'ZAR',
                  'THB - Thai Baht': 'THB',
                  'TJS - Tajikistani Somoni': 'TJS',
                  'TMT - Turkmenistani Manat': 'TMT',
                  'TND - Tunisian Dinar': 'TND',
                  'TOP - Tongan Paʻanga': 'TOP',
                  'TRY - Turkish Lira': 'TRY',
                  'TTD - Trinidad and Tobago Dollar': 'TTD',
                  'TZS - Tanzanian Shilling': 'TZS',
                  'AED - United Arab Emirates Dirham': 'AED',
                  'UAH - Ukrainian Hryvnia': 'UAH',
                  'UGX - Ugandan Shilling': 'UGX',
                  'USD - United States Dollar': 'USD',
                  'UYU - Uruguayan Peso': 'UYU',
                  'UZS - Uzbekistan Som': 'UZS',
                  'VEF - Venezuelan Bolívar Fuerte': 'VEF',
                  'VND - Vietnamese Dong': 'VND',
                  'VUV - Vanuatu Vatu': 'VUV',
                  'YER - Yemeni Rial': 'YER',
                  'ZMK - Zambian Kwacha (pre-2013)': 'ZMK',
                  'ZMW - Zambian Kwacha': 'ZMW',
                  'ZWL - Zimbabwean Dollar': 'ZWL'}
        

class currencyConversion:
    @classmethod
    def about(cls):
        st.subheader("Read the Below Instructions:")
        st.markdown("""
                    Welcome to the **Currency Conversion Rate Tool**! This tool helps you fetch the daily and average conversion rates for multiple currencies over a specified date range. Follow these steps to get started:

                    ### Instructions:
                    1. **Target Currency Selection**:
                        - Use the dropdown menu to select the target currency for which you want to calculate conversion rates.
                        - Example: Select **USD - United States Dollar** as the target currency.

                    2. **Base Currency Selection**:
                        - Choose one or more base currencies from the multi-select box.
                        - Example: Select currencies like **EUR - Euro**, **GBP - British Pound Sterling**, etc.

                    3. **Date Range Selection**:
                        - Use the date picker to specify the start and end dates for your query.
                        - We can select a Maximum Range of 1 Year.
                        - Ensure the date range is valid (the end date must not be earlier than the start date).

                    4. **Fetch Conversion Rates**:
                        - Click the **Get Conversion Rate** button to start the calculation process.
                        - Wait a moment while the rates are fetched and processed.

                    ### Output:
                    - The tool will save the conversion rates in a CSV file with the following naming convention:
                    `TargetCurrency_Currency_Rate_StartDate_EndDate_Time.csv`

                    ### Notes:
                    - Ensure your internet connection is active for the tool to fetch live data.
                    - Check that your API key is valid and has sufficient requests available.
                    - If you encounter an error, recheck the input details and try again.

                    ### Example:
                    - **Target Currency**: USD - United States Dollar
                    - **Base Currencies**: EUR, GBP, INR
                    - **Date Range**: 2025-01-01 to 2025-01-31
                    - Output File: `USD_Currency_Rate_2025-01-01_2025-01-31_TimeStamp.csv`

                    Happy Currency Tracking!
                    """, unsafe_allow_html=True)

    @classmethod
    @st.dialog("Calculating..")
    def get_currency(cls,sourceCurrencies,targetCurrencies,start_date,end_date):
        try:
            with st.spinner('Processing Please Wait'):
                st.session_state.csv_buffer = io.BytesIO()
                base_url = (
                            f"https://api.currencylayer.com/timeframe?"
                            f"access_key={api_key}&start_date={start_date}&end_date={end_date}&source={sourceCurrencies}&currencies={targetCurrencies}"
                        )
                response = requests.get(base_url)
                data = response.json()['quotes']
                uniqueCurrencies = list(data[list(data.keys())[0]].keys())

                appendedDates = list(data.keys())*len(uniqueCurrencies)

                currencies = ([[currency.replace(sourceCurrencies,'')]*len(data.keys()) for currency in uniqueCurrencies])
                appendedCurrencies = [currency for sublist in currencies for currency in sublist]

                appendedRates = []
                df = pd.DataFrame(data).transpose()
                for each in uniqueCurrencies:
                    appendedRates.extend(df[each].to_list())

                appendedRates = [1/rate for rate in appendedRates]

                master = pl.DataFrame({'Date':appendedDates,'Currency':appendedCurrencies,'FX Rate':appendedRates})

                master = master.with_columns(
                    pl.col('FX Rate').cast(pl.Float32).alias("FX Rate"),
                    pl.col('Date').str.to_date('%Y-%m-%d').alias("Date")
                )

                if st.session_state.conversion_type == 'Monthly':
                        master = master.group_by([pl.col('Date').dt.strftime("%B").alias('Month'), pl.col('Currency').alias('Currency')])\
                                .agg(pl.col('FX Rate').mean().alias('FX Rate')).sort(by=['Month','Currency'],descending=False)
                        
                elif st.session_state.conversion_type == 'Average' :
                    master = master.group_by(pl.col('Currency').alias('Currency'))\
                    .agg(pl.col('FX Rate').mean().alias('FX Rate')).sort(by='Currency',descending=False)

                elif st.session_state.conversion_type == 'Yearly' :
                    master = master.group_by([pl.col('Date').dt.year().alias('Year'),pl.col('Currency').alias('Currency')])\
                    .agg(pl.col('FX Rate').mean().alias('FX Rate')).sort(by=['Year','Currency'],descending=False)

                st.success('Exchange Rate Calculated, Please Downloaded.')
                
                master.write_csv(st.session_state.csv_buffer)
                st.session_state.csv_buffer.seek(0)
                time.sleep(2)
                return

        except Exception as e:
            st.warning(f'Unable {e} Error Occured')

    @classmethod
    def close_dialog(cls):
        # Clean up session state for next run
        if 'processed_data' in st.session_state:
            del st.session_state.processed_data
        if 'file_size_large' in st.session_state:
            del st.session_state.file_size_large
        st.session_state.dialog_closed = True  



    @classmethod
    def getExchangeRate(cls):
        
        
        st.subheader("Get Exchange Rate For 168 Currencies in Seconds")
        # Set the input widgets and update session state with the user inputs
        st.session_state.target_currency = st.selectbox(
            label='Select the Target Currency', 
            options=all_currencies.keys(),
            index=None, 
            placeholder='Target Currency',
            on_change=currencyConversion.reset
        )

        st.session_state.base_currency = st.multiselect(
            label='Select the Base Currency', 
            options=all_currencies.keys(),
            on_change=currencyConversion.reset
        )

        st.session_state.start_date = st.date_input(
            label='Select the Start Date', 
            key='start',
            on_change=currencyConversion.reset
        )

        st.session_state.end_date = st.date_input(
            label='Select the End Date', 
            key='end',
            on_change=currencyConversion.reset
        )

        st.session_state.conversion_type = st.selectbox(
            "Select the Conversion Rate Type",
            options=['Average', 'Daily', 'Monthly','Yearly'],
            index=0,
            on_change=currencyConversion.reset
        )



                

    def Convertor(self):
        global navigation_cols
        if 'ccPageIdx' not in st.session_state:
            st.session_state.ccPageIdx = 0
        if 'target_currency' not in st.session_state:
            st.session_state.target_currency = None
        if 'base_currency' not in st.session_state:
            st.session_state.base_currency = []
        if 'start_date' not in st.session_state:
            st.session_state.start_date = None
        if 'end_date' not in st.session_state:
            st.session_state.end_date = None
        if 'conversion_type' not in st.session_state:
            st.session_state.conversion_type = 'Average'  # Default to 'Average'
        if 'csv_buffer' not in st.session_state:
            st.session_state.csv_buffer = None

        pages = [currencyConversion.about,currencyConversion.getExchangeRate]
        current_page = st.session_state.ccPageIdx
        pages[current_page]()
            
        st.session_state.CCnavigation_cols = st.columns(3)
        with st.session_state.CCnavigation_cols[2]:
            if current_page>0:
                if st.button('Previous',use_container_width=True):
                    st.session_state.ccPageIdx-=1
                    st.rerun()

            elif current_page<len(pages)-1:
                if st.button("Next",use_container_width=True):
                    st.session_state.ccPageIdx+=1
                    st.rerun()

        with st.session_state.CCnavigation_cols[0]:

            if st.session_state.csv_buffer is None:
                if not st.session_state.target_currency or not st.session_state.base_currency or not st.session_state.start_date or not st.session_state.end_date or not st.session_state.conversion_type:
                    st.warning("Please fill in all the fields before proceeding!")
                elif st.button('Get Convesion Rates',use_container_width=True):
                    # Proceed only if the date range is within 365 days
                    st.session_state.base_currency = [all_currencies.get(currency) for currency in st.session_state.base_currency]
                    st.session_state.target_currency = all_currencies.get(st.session_state.target_currency)

                    if not (st.session_state.end_date - st.session_state.start_date).days > 365:
                        sourceCurrencies = st.session_state.target_currency
                        targetCurrencies = ",".join(st.session_state.base_currency)
                        currencyConversion.get_currency(sourceCurrencies, targetCurrencies, st.session_state.start_date, st.session_state.end_date)
                        st.rerun()
                    else:
                        st.warning('Total Period of 365 Days Can be Selected at Once!')

            elif st.session_state.csv_buffer is not None and current_page == 1:
                time = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
                file_name = f'Conversion_Rates_{time}.csv'
                st.download_button('Download Results',data = st.session_state.csv_buffer,file_name=file_name,use_container_width=True,
                                   on_click=currencyConversion.reset)
    def reset():
        st.session_state.csv_buffer = None