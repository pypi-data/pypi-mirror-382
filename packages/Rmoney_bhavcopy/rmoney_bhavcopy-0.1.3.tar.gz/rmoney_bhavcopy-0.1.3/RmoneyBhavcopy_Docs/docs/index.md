# Welcome to RmoneyBhavcopy Library
-----------------------------------------------------------------------------------------------------------------------------------------------------
## Introduction
This Python Library is designed to fetch BhavCopy data (daily market reports) from a PostgreSQL database for specified symbols, date ranges, and series. The script provides utility functions to standardize data formats, parse dates, and retrieve data for Cash Market (CM), Futures and Options (FO), and Indices.

## Features
- Fetch Market Data Across Segments.

- Standardize Data Formats.

- Connects securely to a PostgreSQL database using configuration details.

- Supports flexible defaults for date ranges and symbols.

- Accepts ticker symbols in any case (lowercase, uppercase, or mixed).

- Raises a ValueError if the start_date is greater than the end_date.

- Defaults to January 1, 2016, as the start_date if none is specified.

- Defaults to the current date as the end_date if none is specified.

- Defaults to January 1, 2016, as the start_date and the current date as the end_date if neither is specified.


## Installation
- **Create Virtual Environment** (*Optional*)
```bash
python -m venv .venv
```
- **Install Library using pip**
```bash
pip install http://pypi.rmoneyindia.in:8080/rmoney_bhavcopy-0.1.2-py3-none-any.whl
```

- **Install Library using uv**
```bash
uv add --frozen http://192.168.50.40:8080/rmoney_bhavcopy-0.1.2-py3-none-any.whl
```
```bash
uv sync
```

## Examples
**Example 1**:Fetching bhavcopy for Specific Stocks,Index and FNO.

```python
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_CM_bhavcopy,get_FO_bhavcopy,get_indices_bhavcopy
from datetime import datetime

CM_data = get_CM_bhavcopy(
    start_date= datetime(2022,1,1),
    end_date=datetime(2022,1,31),
    symbols= ['TCS','TECHM'],
    series= ['EQ']
)
print(CM_data)

FO_data = get_FO_bhavcopy(
    start_date= datetime(2022,1,1),
    end_date=datetime(2022,1,31),
    symbols= ['TCS','TECHM'],
)
print(FO_data)

indices_data = get_indices_bhavcopy(
    start_date= datetime(2022,1,1),
    end_date=datetime(2022,1,31),
    symbols= ["Nifty 50","Nifty 100"]
)
print(indices_data)
```
**Example 2**: Fetching bhavcopy without marked the Starting Date (then the start_date = datetime(2016,1,1), By default).

```python
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_CM_bhavcopy,get_FO_bhavcopy,get_indices_bhavcopy
from datetime import datetime

CM_data = get_CM_bhavcopy(
    end_date=datetime(2022,1,31),
    symbols= ['TCS','TECHM'],
    series= ['EQ']
)
print(CM_data)

FO_data = get_FO_bhavcopy(

    end_date=datetime(2022,1,31),
    symbols= ['TCS','TECHM'],
)
print(FO_data)

indices_data = get_indices_bhavcopy(
    end_date=datetime(2022,1,31),
    symbols= ["Nifty 50","Nifty 100"]
)
print(indices_data)
```

**Example 3**: Fetching bhavcopy without without marked the Ending Date (then the end_date = datetime.now(), By default).

```python
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_CM_bhavcopy,get_FO_bhavcopy,get_indices_bhavcopy
from datetime import datetime

CM_data = get_CM_bhavcopy(
    start_date= datetime(2022,1,1),
    symbols= ['TCS','TECHM'],
    series= ['EQ']
)
print(CM_data)

FO_data = get_FO_bhavcopy(
    start_date= datetime(2022,1,1),
    symbols= ['TCS','TECHM'],
)
print(FO_data)

indices_data = get_indices_bhavcopy(
    start_date= datetime(2022,1,1),
    symbols= ["Nifty 50","Nifty 100"]
)
print(indices_data)
```

**Example 4**: Fetching bhavcopy without marked the Starting Date and Ending Date (then the start_date = datetime(2016,1,1) and end_date = datetime.now(), By default).

```python
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_CM_bhavcopy,get_FO_bhavcopy,get_indices_bhavcopy
from datetime import datetime

CM_data = get_CM_bhavcopy(
    symbols= ['TCS','TECHM'],
    series= ['EQ']
)
print(CM_data)

FO_data = get_FO_bhavcopy(
    symbols= ['TCS','TECHM'],
)
print(FO_data)

indices_data = get_indices_bhavcopy(
    symbols= ["Nifty 50","Nifty 100"]
)
print(indices_data)
```

## Output
![Output](./img/output.png)

## Note
`get_CM_bhavcopy(start_date, end_date, symbols, series)`

- **Purpose**: Fetch Cash Market BhavCopy data for multiple symbols over a specified date range.

- **Parameters**:
    - `start_date` (Optional[datetime.date]): Start date (default is 2016-01-01).
    - `end_date` (Optional[datetime.date]): End date (default is the current date).
    - `symbols` (Optional[List[str]]): List of symbols to fetch data for.
    - `series` (Optional[List[str]]): List of series types (e.g., 'EQ', 'GB').

- **Returns**: A Pandas DataFrame containing the fetched data
- Raises:
    - ValueError: If any arguments are invalid.
```python
# Example 1: Fetching data for specific stocks
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_CM_bhavcopy
from datetime import datetime
data = get_CM_bhavcopy(
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 31),
    symbols=['TCS', 'HDFCBANK'],
    series=['EQ']
)

```
## Output
![Output](./img/cm.png)

----------------------------------------------------------------------------------------------------------------------------------------------------------
`get_FO_bhavcopy(start_date, end_date, symbols)`

- **Purpose**: Fetch FNO Market BhavCopy data for multiple symbols over a specified date range.

- **Parameters**:
    - `start_date` (Optional[datetime.date]): Start date (default is 2016-01-01).
    - `end_date` (Optional[datetime.date]): End date (default is the current date).
    - `symbols` (Optional[List[str]]): List of symbols to fetch data for.

- **Returns**: A Pandas DataFrame containing the fetched data
- Raises:
    - ValueError: If any arguments are invalid.

```python
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_FO_bhavcopy
from datetime import datetime
FO_data = get_FO_bhavcopy(
    start_date= datetime(2022,1,1),
    end_date=datetime(2022,1,31),
    symbols= ['TCS','TECHM'],
)
print(FO_data)
```
![Output](./img/fno.png)
----------------------------------------------------------------------------------------------------------------------------------------------------------
`get_indices_bhavcopy(start_date, end_date, symbols)`
- **Purpose**: Fetch Indices Market BhavCopy data for multiple symbols over a specified date range.

- **Parameters**:
    - `start_date` (Optional[datetime.date]): Start date (default is 2016-01-01).
    - `end_date` (Optional[datetime.date]): End date (default is the current date).
    - `symbols` (Optional[List[str]]): List of symbols to fetch data for.

- **Returns**: A Pandas DataFrame containing the fetched data.
- Raises:
    - ValueError: If any arguments are invalid.

```python
from Rmoney_bhavcopy.Bhavcopy_Reteriver import get_indices_bhavcopy
from datetime import datetime
Indices_data = get_indices_bhavcopy(
    start_date= datetime(2022,1,1),
    end_date=datetime(2022,1,31),
    symbols= ["Nifty 50","Nifty 100"]
)
print(Indices_data)
```
![Output](./img/indices.png)

## Gitlab
[GitLab Repository - RmoneyBhavcopy Library](http://gl.rmoneyindia.in/quant/bhavcopy)


