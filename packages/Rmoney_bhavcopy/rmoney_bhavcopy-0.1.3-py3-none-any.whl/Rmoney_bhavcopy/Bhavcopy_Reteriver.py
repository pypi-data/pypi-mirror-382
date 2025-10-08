import pandas as pd
import json
import psycopg2
from dateutil.parser import parse
from datetime import datetime
import logging
# import config
from . import config
from typing import List,Optional

# Configuration Mapping for headers
COLUMN_MAPPING_CM = {
    "SYMBOL": "TckrSymb",
    "SERIES": "SctySrs",
    "OPEN": "OpnPric",
    "HIGH": "HghPric",
    "LOW": "LwPric",
    "CLOSE": "ClsPric",
    "LAST": "LastPric",
    "PREVCLOSE": "PrvsClsgPric",
    "TOTTRDQTY": "TtlTradgVol",
    "TOTTRDVAL": "TtlTrfVal",
    "TIMESTAMP": "TradDt",
    "TOTALTRADES": "TtlNbOfTxsExctd",
    "ISIN": "ISIN"
}
COLUMN_MAPPING_FO = {
    "INSTRUMENT": "FinInstrmTp",
    "SYMBOL": "TckrSymb",
    "EXPIRY_DT": "XpryDt",
    "STRIKE_PR": "StrkPric",
    "OPTION_TYP": "OptnTp",
    "OPEN": "OpnPric",
    "HIGH": "HghPric",
    "LOW": "LwPric",
    "CLOSE": "ClsPric",
    "SETTLE_PR": "SttlmPric",
    "CONTRACTS": "TtlTradgVol",
    "VAL_INLAKH": "TtlTrfVal",
    "OPEN_INT": "OpnIntrst",
    "CHG_IN_OI": "ChngInOpnIntrst",
    "TIMESTAMP": "TradDt"
    
}

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_config_data():
    """Load configuration data."""
    return config.conf

def establish_connection():
    """Establish a database connection."""
    config_data = get_config_data()
    return psycopg2.connect(
        host=config_data['hostname'],
        database=config_data['database'],
        user=config_data['username'],
        password=config_data['pwd'],
        port=config_data['port']
    )

def fetch_data_CM(conn, startdate, enddate, symbol, series, table_name):
    """Fetch data from the specified table based on parameters."""
    cur = conn.cursor()
    
    if table_name == "bhavcopies_cm":
        query = """
            SELECT * FROM bhavcopies_cm
            WHERE timestamp >= %s AND timestamp <= %s
            AND symbol = %s AND series = %s
        """
        columns = [
            "SYMBOL", "SERIES", "OPEN", "HIGH", "LOW", "CLOSE", "LAST",
            "PREVCLOSE", "TOTTRDQTY", "TOTTRDVAL", "TIMESTAMP", "TOTALTRADES", "ISIN"
        ]
    elif table_name == "bhavcopies_udiff":
        query = """
            SELECT * FROM bhavcopies_udiff
            WHERE TradDt >= %s AND TradDt <= %s
            AND TckrSymb = %s AND SctySrs = %s
        """
        columns = [
            "TradDt", "BizDt", "Sgmt", "Src", "FinInstrmTp", "FinInstrmId", "ISIN",
            "TckrSymb", "SctySrs", "XpryDt", "FininstrmActlXpryDt", "StrkPric", "OptnTp",
            "FinInstrmNm", "OpnPric", "HghPric", "LwPric", "ClsPric", "LastPric",
            "PrvsClsgPric", "UndrlygPric", "SttlmPric", "OpnIntrst", "ChngInOpnIntrst",
            "TtlTradgVol", "TtlTrfVal", "TtlNbOfTxsExctd", "SsnId", "NewBrdLotQty",
            "Rmks", "Rsvd1", "Rsvd2", "Rsvd3", "Rsvd4"
        ]
    else:
        raise ValueError("Invalid table name provided.")

    cur.execute(query, (startdate, enddate, symbol, series))
    result = cur.fetchall()
    return pd.DataFrame(result, columns=columns)

def fetch_data_FO(conn, startdate, enddate, symbol, table_name):
    """Fetch data from the specified table based on provided parameters."""
    cur = conn.cursor()

    if table_name == "FO_bhavCopies_CM":
        query = """
            SELECT * FROM  FO_bhavCopies_CM
            WHERE TIMESTAMP >= %s AND TIMESTAMP <= %s
            AND SYMBOL = %s
        """
        columns = [
            "INSTRUMENT", "SYMBOL", "EXPIRY_DT", "STRIKE_PR", "OPTION_TYP", "OPEN", "HIGH", 
        "LOW", "CLOSE", "SETTLE_PR", "CONTRACTS", "VAL_INLAKH", "OPEN_INT", "CHG_IN_OI", "TIMESTAMP"
        ]
       
    elif table_name == "FO_Bhavcopies_UDiFF":
        query = """
            SELECT * FROM FO_Bhavcopies_UDiFF 
            WHERE TradDt >= %s AND TradDt <= %s 
            AND TckrSymb = %s 
        """
        columns = [
            "TradDt", "BizDt", "Sgmt", "Src", "FinInstrmTp", "FinInstrmId", "ISIN",
            "TckrSymb", "SctySrs", "XpryDt", "FininstrmActlXpryDt", "StrkPric", "OptnTp",
            "FinInstrmNm", "OpnPric", "HghPric", "LwPric", "ClsPric", "LastPric",
            "PrvsClsgPric", "UndrlygPric", "SttlmPric", "OpnIntrst", "ChngInOpnIntrst",
            "TtlTradgVol", "TtlTrfVal", "TtlNbOfTxsExctd", "SsnId", "NewBrdLotQty",
            "Rmks", "Rsvd1", "Rsvd2", "Rsvd3", "Rsvd4"
        ]
    else:
        raise ValueError("Invalid table name provided.")

    cur.execute(query, (startdate, enddate, symbol))
    
    result = cur.fetchall()

    return pd.DataFrame(result, columns=columns)

def fetch_data_Indices(conn, startdate, enddate, symbol, table_name):
    """Fetch data from the specified table based on provided parameters."""

    cur = conn.cursor()

    if table_name == "Indices_bhavCopies":
        query = """
            SELECT * FROM Indices_bhavCopies
            WHERE "Index Date" >= %s AND "Index Date" <= %s
            AND "Index Name" = %s

"""

        column = [
            "Index Name", "Index Date", "Open Index Value", "High Index Value", "Low Index Value", 
            "Closing Index Value", "Points Change", "Change(%)", "Volume", "Turnover (Rs. Cr.)", 
            "P/E", "P/B", "Div Yield"
        ]
    else:
        raise ValueError("Invalid table name provided.")
    
    cur.execute(query,(startdate,enddate,symbol))

    result = cur.fetchall()

    return pd.DataFrame(result, columns=column)

def map_columns_CM(dataframe, mapping, source_table):
    """Map DataFrame columns to a unified format."""
    if source_table == "bhavcopies_cm":
        dataframe = dataframe.rename(columns=mapping)
    return dataframe

def map_columns_FO(dataframe, mapping, source_table):
    """Map the columns of the given DataFrame to a unified format."""
    if source_table == "FO_bhavCopies_CM":
        dataframe = dataframe.rename(columns=mapping)

    return dataframe

def parse_date(date_str):
    """Parse input date to 'YYYY-MM-DD' format."""
    try:
        parsed_date = parse(date_str)
        return parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Invalid date format: {date_str}. Error: {e}")

def get_CM_bhavcopy(start_date:Optional[datetime.date]=datetime(2016,1,1), end_date:Optional[datetime.date]=datetime.now(), symbols :Optional[List[str]]=None, series:Optional[List[str]]=None):
    """
    Get the BhavCopy data for multiple symbols over a specified date range, ensuring consistent column mapping across different data sources.
        This function retrieves historical data from 2016-01-01 to yesterday's date
Parameters:
    startdate (str): The starting date for the data retrieval in 'YYYY-MM-DD' format.
    enddate (str): The ending date for the data retrieval in 'YYYY-MM-DD' format.
    symbols (list): A list of financial symbols (e.g., stock tickers) for which data is to be fetched.
    series (str): The type of data series to retrieve (e.g., 'EQ', 'GB','GS','SG').

Examples:
    Example 1: Fetching CM bhavcopy Data for Specific Stocks
        start_date = datetime(2023,1,1)
        end_date = datetime(2023,1,31)
        symbols = ['TCS', 'TECHM', 'HDFCBANK']
        series = ['EQ']
        bhavcopy_data = get_CM_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols, series=series)

    Example 2: Fetching Gold Bond bhavcopy Data for Multiple Symbols
        start_date = datetime(2024,1,1)
        end_date = datetime(2024,1,31)
        symbols = ['SGBSEP31II', 'SGBSEP27']
        series = ['GB']
        bhavcopy_data = get_CM_bhavcopy(start_date=start_start_date, end_date=end_date, symbols=symbols, series=series)

    Example 3: Fetching bhavcopy Data for a Single Symbol
        start_date = datetime(2024,1,1)
        end_date = datetime(2024,1,31)
        symbols = ['AGTL']
        series = ['EQ']
        bhavcopy_data = get_CM_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols, series=series)

    Example 4: Fetching bhavcopy Data Over a Longer Date Range
        start_date = datetime(2020,1,1)
        end_date = datetime(2024,1,31)
        symbols = ['ATGL', 'HDFCBAK', 'TCS']
        series = 'EQ'
        bhavcopy_data = get_CM_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols, series=series)

    Example 5: Fetching CM Bhavcopy Data without marked the Starting Date (then the start_date = datetime(2016,1,1), By default)
        end_date = datetime(2024,1,31)
        symbols = ['TCS']
        series = ['EQ']
        bhavcopy_data = get_CM_bhavcopy(end_date=end_date, symbols=symbols, series=series)

    Example 6: Fetching CM Bhavcopy Data without marked the ending date (then the end_date = datetime.now(), By Default (Current date of system))
        start_date = datetime(2024,1,1)
        symbols = ['TCS, 'TECHM']
        series = ['EQ']
        bhavcopy_data = get_CM_bhavcopy(start_date=start_date, symbols=symbols, series=series)

    Example 7: Fetching CM Bhavcopy Data without marking both the start_date and and end_date (then the start_date = datetime(2016,1,1) and end_date = datetime.now(), By Default)
        symbols = ['TCS, 'TECHM']
        series = ['EQ']
        bhavcopy_data = get_CM_bhavcopy(symbols=symbols, series=series)


    """

    conn = None
    if not isinstance(start_date, datetime):
            raise ValueError(f"Expected datetime, but got {type(start_date).__name__}")
        
    if not isinstance(end_date, datetime):
            raise ValueError(f"Expected datetime, but got {type(end_date).__name__}")
    if start_date > end_date:
        raise ValueError("startdate must be earlier than enddate.")
        
        
        # Validate date range
    try:
         # Convert symbols to upper case for consistency
        if symbols:
            symbols = [symbol.upper() for symbol in symbols]
        # Validate date range
        start_date_obj =  start_date.strftime("%Y-%m-%d")
        end_date_obj = end_date.strftime("%Y-%m-%d")
        if start_date_obj > end_date_obj:
            raise ValueError("startdate must be earlier than enddate.")

        # Validate symbols input
        if not symbols or not isinstance(symbols, list):
            raise ValueError("Symbols must be a non-empty list.")
        
        # Validate series input
        if not series or not isinstance(series, list) or not all(isinstance(s, str) for s in series):
            raise ValueError("Series must be a non-empty list of strings.")

        conn = establish_connection()
        logger.info("Database connection established.")
        
        all_data = pd.DataFrame()
        for symbol in symbols:
            try:
                logger.info(f"Fetching data for symbol: {symbol}")
                
                # Fetch data from both tables for each series
                cm_data = pd.DataFrame()
                udiff_data = pd.DataFrame()
                
                for s in series:
                    cm_data_temp = fetch_data_CM(conn, start_date, end_date, symbol, s, "bhavcopies_cm")
                    udiff_data_temp = fetch_data_CM(conn, start_date, end_date, symbol, s, "bhavcopies_udiff")
                    
                    cm_data = pd.concat([cm_data, cm_data_temp], ignore_index=True)
                    udiff_data = pd.concat([udiff_data, udiff_data_temp], ignore_index=True)
                
                # Map and merge data
                cm_data_mapped = map_columns_CM(cm_data, COLUMN_MAPPING_CM, "bhavcopies_cm")
                combined_data = pd.merge(udiff_data, cm_data_mapped, how="outer")
                
                # Append to the cumulative DataFrame
                all_data = pd.concat([all_data, combined_data], ignore_index=True)

            except Exception as e:
                logger.error(f"Error processing symbol {symbol}: {e}")

        return all_data

    except Exception as e:
        logger.error(f"Error: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

def get_FO_bhavcopy(start_date:Optional[datetime.date]=datetime(2016,1,1), end_date:Optional[datetime.date]=datetime.now(), symbols :Optional[List[str]]=None):
    """Get the BhavCopy data for multiple symbols over a specified date range, ensuring consistent column mapping across different data sources.
        This function retrieves historical data from 2016-01-01 to yesterday's date
Parameters:
    startdate (datetime): The starting date for the data retrieval in 'YYYY,MM,DD' format.
    enddate (datetime): The ending date for the data retrieval in 'YYYY,MM,DD' format.
    symbols (list): A list of financial symbols (e.g., BANKNIFTY tickers) for which data is to be fetched.
    

Examples:
    Example 1: Fetching FO bhavcopy Data for Specific Stocks
        start_date = datetime(2023,1,1)
        end_date = datetime(2023,1,31)
        symbols = ['BANKNIFTY', 'DJIA', 'NIFTYINFRA']
        bhavcopy_data = get_FO_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols)


    Example 3: Fetching FO bhavcopy Data for a Single Symbol
        start_date = datetime(2023,1,1)
        end_date = datetime(2023,1,31)
        symbols = ['BANKNIFTY']
        bhavcopy_data = get_FO_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols)

    Example 3: Fetching FO bhavcopy Data Over a Longer Date Range
        start_date = datetime(2020,1,1)
        end_date = datetime(2024,1,31)
        symbols = ['BANKNIFTY', 'DJIA', 'NIFTYINFRA']
        bhavcopy_data = get_FO_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols)

    Example 4: Fetching FO bhavcopy Data without marked the Starting Date (then the start_date = datetime(2016,1,1), By default)
        end_date = datetime(2017,1,31)
        symbols = ['BANKNIFTY', 'DJIA', 'NIFTYINFRA']
        bhavcopy_data = get_FO_bhavcopy(end_date=end_date, symbols=symbols)

    Example 5: Fetching FO bhavcopy Data without marked the Ending Date (then the end_date = datetime.now(), By Default (Current date of system))
        start_date = datetime(2023,1,1)
        symbols = ['BANKNIFTY', 'DJIA', 'NIFTYINFRA']
        bhavcopy_data = get_FO_bhavcopy(start_date=start_date, symbols=symbols)

    Example 6: Fetching FO Bhavcopy Data without marking both the start_date and and end_date (then the start_date = datetime(2016,1,1) and end_date = datetime.now(), By Default)
        symbols = ['BANKNIFTY', 'DJIA', 'NIFTYINFRA']
        bhavcopy_data = get_FO_bhavcopy(symbols=symbols)

""" 
    conn = None
    all_data = pd.DataFrame()  # Initialize an empty DataFrame for all symbols

    # Raise an error if startdate or enddate is not datetime
    if not isinstance(start_date, datetime):
            raise ValueError(f"Expected datetime, but got {type(start_date).__name__}")
        
    if not isinstance(end_date, datetime):
            raise ValueError(f"Expected datetime, but got {type(end_date).__name__}")
    
     # Convert symbols to upper case for consistency
    if symbols:
        symbols = [symbol.upper() for symbol in symbols]

    try:
        if start_date > end_date:
            raise ValueError("Startdate must be earlier than Enddate.")
        
        conn = establish_connection()

        for symbol in symbols:
            print(f"Fetching data for symbol: {symbol}")
            
            # Fetch data from both tables
            cm_data = fetch_data_FO(conn, start_date, end_date, symbol, "FO_bhavCopies_CM")
            udiff_data = fetch_data_FO(conn, start_date, end_date, symbol, "FO_Bhavcopies_UDiFF")

            # Map columns for consistency
            cm_data_mapped = map_columns_FO(cm_data, COLUMN_MAPPING_FO, "FO_bhavCopies_CM")

            # Merge data for this symbol
            combined_data = pd.merge(udiff_data, cm_data_mapped, how="outer")
            
            # Append to the cumulative DataFrame
            all_data = pd.concat([all_data, combined_data], ignore_index=True)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

    return all_data


def get_indices_bhavcopy(start_date:Optional[datetime.date]=datetime(2016,1,1), end_date:Optional[datetime.date]=datetime.now(), symbols :Optional[List[str]]=None):
    """Get the BhavCopy data for multiple symbols over a specified date range, ensuring consistent column mapping across different data sources.
        This function retrieves historical data from 2016-01-01 to yesterday's date
Parameters:
    startdate (datetime): The starting date for the data retrieval in 'YYYY,MM,DD' format.
    enddate (datetime): The ending date for the data retrieval in 'YYYY,MM,DD' format.
    symbols (list): A list of financial symbols (e.g., NIFTY 50, Nifty500 Momentum 50 tickers) for which data is to be fetched.
    

Examples:
    Example 1: Fetching Indices bhavcopy Data for Specific Stocks
        start_date = datetime(2023,1,1)
        end_date = datetime(2023,1,31)
        symbols = ["NIFTY 50", "Nifty500 Momentum 50", "NIFTY 100"]
        bhavcopy_data = get_indices_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols)
    

    Example 3: Fetching Indices bhavcopy Data for a Single Symbol
        start_date = datetime(2023,1,1)
        end_date = datetime(2023,1,31)
        symbols = ["NIFTY 50"]
        bhavcopy_data = get_indices_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols)

    Example 3: Fetching Indices bhavcopy Data Over a Longer Date Range
        start_date = datetime(2020,1,1)
        end_date = datetime(2024,1,31)
        symbols = ["NIFTY 50", "Nifty500 Momentum 50", "NIFTY 100"]
        bhavcopy_data = get_indices_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols)

    Example 4: Fetching Indices bhavcopy Data without marked the Starting Date (then the start_date = datetime(2016,1,1), By default)
        end_date = datetime(2017,1,31)
        symbols = ["NIFTY 50", "Nifty500 Momentum 50", "NIFTY 100"]
        bhavcopy_data = get_indices_bhavcopy(end_date=end_date, symbols=symbols)

    Example 5: Fetching Indices bhavcopy Data without marked the Ending Date (then the end_date = datetime.now(), By Default (Current date of system))
        start_date = datetime(2023,1,1)
        symbols = ["NIFTY 50", "Nifty500 Momentum 50", "NIFTY 100"]
        bhavcopy_data = get_FO_bhavcopy(start_date=start_date, symbols=symbols)

    Example 6: Fetching Indices Bhavcopy Data without marking both the start_date and and end_date (then the start_date = datetime(2016,1,1) and end_date = datetime.now(), By Default)
        symbols = ["NIFTY 50", "Nifty500 Momentum 50", "NIFTY 100"]
        bhavcopy_data = get_indices_bhavcopy(symbols=symbols)

""" 
    conn = None
    all_data = pd.DataFrame()  

    # Raise an error if startdate or enddate is not datetime
    if not isinstance(start_date, datetime):
            raise ValueError(f"Expected datetime, but got {type(start_date).__name__}")
        
    if not isinstance(end_date, datetime):
            raise ValueError(f"Expected datetime, but got {type(end_date).__name__}")
    
   

    try:
        if start_date > end_date:
            raise ValueError("Startdate must be earlier than Enddate.")
        
        conn = establish_connection()

        for symbol in symbols:
            print(f"Fetching data for symbol: {symbol}")
            
            # Fetch data from both tables
            indices_data = fetch_data_Indices(conn, start_date, end_date, symbol, "Indices_bhavCopies")
            
            # Append to the cumulative DataFrame
            all_data = pd.concat([all_data, indices_data], ignore_index=True)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

    return all_data



def main():
    """Main function to run the script."""
    startdate_FO = datetime(2023,12,1)
    enddate_FO = datetime(2023,12,10)
    symbols_FO = ['BANKNIFTY', 'DJIA', 'NIFTYINFRA']
    
    startdate_CM = datetime(2023,12,1)  
    enddate_CM = datetime(2023,12,10)
    symbols_CM = ["TCS","TECHM","HDFCBANK","20MICRONS"]
    series = ["EQ","BE"]  

    startdate_Indx = datetime(2023,12,1)
    enddate_Indx = datetime(2023,12,10)
    symbols_Indx = ["Nifty 50","Nifty 100", "Nifty 200"]

    # Fetch data
    data_CM = get_CM_bhavcopy(startdate_CM, enddate_CM, symbols_CM, series)
    if not data_CM.empty:
        print("BhavCopy Data Retrieved:")
        print(data_CM)

        
    else:
        print("No data found for the specified criteria.")

    data_FO = get_FO_bhavcopy(startdate_FO,enddate_FO, symbols_FO)
    if not data_FO.empty:
        print("FO BhavCopy Data Retrieved:")
        print(data_FO)
    else:
        print("No data found for the specified criteria.")

    data_idx = get_indices_bhavcopy(start_date=startdate_Indx,end_date=enddate_Indx,symbols=symbols_Indx)
    if not data_idx.empty:
        print("Indices BhavCopy Data Retrieved:")
        print(data_idx)

if __name__ == "__main__":
    main()
