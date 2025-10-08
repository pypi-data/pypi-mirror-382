from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_CM_bhavcopy
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_FO_bhavcopy
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_indices_bhavcopy
import pytest
from datetime import datetime
import pandas as pd

# Test Case for CM Bhavcopy
def test_CM_bhavcopy1():
    start_date = datetime(2024,1,1)
    end_date = datetime(2024,1,31)
    symbols = ['tcs']
    series = ['EQ']
    data = get_CM_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols, series=series)
    assert type(data) == pd.DataFrame
    assert data.shape[0] > 10
    assert data.shape[1] == 34
    print(data)


def test_CM_bhavcopy2():
    
    end_date = datetime(2016,1,31)
    symbols = ['TCS', 'HDFCBANK', 'infy']
    series = ['EQ','BE']
    data2 = get_CM_bhavcopy(end_date=end_date, symbols=symbols, series=series)
    assert type(data2) == pd.DataFrame
    assert data2.shape[0] > 60
    assert data2.shape[1] == 34
    print(data2)

def test_CM_bhavcopy3():
    start_date = datetime(2024,1,1)
    symbols = ['TCS', 'HDFCBANK']
    series = ['EQ']
    data3 = get_CM_bhavcopy(start_date=start_date, symbols=symbols,series=series)
    assert type(data3) == pd.DataFrame  
    assert data3.shape[0] > 400
    assert data3.shape[1] == 34
    # print(data3)

def test_CM_bhavcopy4():
    symbols = ['TCS']
    series = ['EQ']
    data4 = get_CM_bhavcopy(symbols=symbols,series=series)
    assert type(data4) == pd.DataFrame
    assert data4.shape[0] > 800
    assert data4.shape[1] == 34 
    # print(data4)


# Test Case for FO Bhavcopy
def test_FO_bhavcopy1():
    start_date = datetime(2023,12,1)
    end_date = datetime(2023,12,10)
    symbols = ['BANKNIFTY']
    data5 = get_FO_bhavcopy(start_date,end_date,symbols)
    assert type(data5) == pd.DataFrame
    assert data5.shape[0] > 8000
    assert data5.shape[1] == 34
    # print(data5)

def test_FO_bhavcopy2():
    end_date = datetime(2016,5,31)
    symbols = ['BANKNIFTY']
    data6 = get_FO_bhavcopy(end_date=end_date,symbols=symbols)
    assert type(data6) == pd.DataFrame
    assert data6.shape[0] > 100
    assert data6.shape[1] == 34
    # print(data6)

def test_FO_bhavcopy3():
    start_date = datetime(2023,12,1)
    symbols = ['BANKNIFTY','DJIA']
    data7 = get_FO_bhavcopy(start_date=start_date,symbols=symbols)
    assert type(data7) == pd.DataFrame
    assert data7.shape[0] > 1000
    assert data7.shape[1] == 34
    # print(data7)

def test_FO_bhavcopy4():
    symbols = ['BANKNIFTY']
    data8 = get_FO_bhavcopy(symbols=symbols)
    assert type(data8) == pd.DataFrame
    assert data8.shape[0] > 100
    assert data8.shape[1] == 34
    # print(data8)

def test_indices_bhavcopy1():
    start_date = datetime(2023,12,1)
    end_date = datetime(2023,12,10)
    symbols = ["Nifty 50"]
    data9 = get_indices_bhavcopy(start_date=start_date, end_date=end_date, symbols=symbols)
    assert type(data9) == pd.DataFrame
    assert data9.shape[0] > 5
    assert data9.shape[1] == 13
    # print(data9)
def test_indices_bhavcopy2():
    end_date = datetime(2016,5,31)
    symbols = ["Nifty 50", "Nifty 100"]
    data10 = get_indices_bhavcopy(end_date=end_date, symbols=symbols)
    assert type(data10) == pd.DataFrame
    assert data10.shape[0] > 5
    assert data10.shape[1] == 13
    # print(data10)
def test_indices_bhavcopy3():
    start_date = datetime(2023,12,1)
    symbols = ["Nifty 50", "Nifty 100"]
    data11 = get_indices_bhavcopy(start_date=start_date, symbols=symbols)
    assert type(data11) == pd.DataFrame
    assert data11.shape[0] > 5
    assert data11.shape[1] == 13
    # print(data11)

def test_indices_bhavcopy4():
    symbols = ["Nifty 50", "Nifty 100"]
    data12 = get_indices_bhavcopy(symbols=symbols)
    assert type(data12) == pd.DataFrame
    assert data12.shape[0] > 5
    assert data12.shape[1] == 13
    print(data12)