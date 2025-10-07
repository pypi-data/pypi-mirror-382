"""
* NSE UTILITY *
Description: This utility is a Python Library to get publicly available data from the new NSE India website
Disclaimer: This utility is meant for educational purposes only. Downloading data from the NSE
website requires explicit approval from the exchange. Hence, the usage of this utility is for
limited purposes only under proper/explicit approvals.
Requirements: The following packages are to be installed (using pip) prior to using this utility
- pandas
- python 3.8 and above
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import zipfile
import random
import time
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings

class NseUtils:
    equity_market_list = ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY MIDCAP 50', 'NIFTY MIDCAP 100',
                          'NIFTY MIDCAP 150', 'NIFTY SMALLCAP 50', 'NIFTY SMALLCAP 100', 'NIFTY SMALLCAP 250',
                          'NIFTY MIDSMALLCAP 400', 'NIFTY 100', 'NIFTY 200', 'NIFTY AUTO',
                          'NIFTY BANK', 'NIFTY ENERGY', 'NIFTY FINANCIAL SERVICES', 'NIFTY FINANCIAL SERVICES 25/50',
                          'NIFTY FMCG', 'NIFTY IT', 'NIFTY MEDIA', 'NIFTY METAL', 'NIFTY PHARMA', 'NIFTY PSU BANK',
                          'NIFTY REALTY', 'NIFTY PRIVATE BANK', 'Securities in F&O', 'Permitted to Trade',
                          'NIFTY DIVIDEND OPPORTUNITIES 50', 'NIFTY50 VALUE 20', 'NIFTY100 QUALITY 30',
                          'NIFTY50 EQUAL WEIGHT', 'NIFTY100 EQUAL WEIGHT', 'NIFTY100 LOW VOLATILITY 30',
                          'NIFTY ALPHA 50', 'NIFTY200 QUALITY 30', 'NIFTY ALPHA LOW-VOLATILITY 30',
                          'NIFTY200 MOMENTUM 30', 'NIFTY COMMODITIES', 'NIFTY INDIA CONSUMPTION', 'NIFTY CPSE',
                          'NIFTY INFRASTRUCTURE', 'NIFTY MNC', 'NIFTY GROWTH SECTORS 15', 'NIFTY PSE',
                          'NIFTY SERVICES SECTOR', 'NIFTY100 LIQUID 15', 'NIFTY MIDCAP LIQUID 15']
    pre_market_list = ['NIFTY 50', 'Nifty Bank', 'Emerge', 'Securities in F&O', 'Others', 'All']

    def __init__(self):
        self.session = requests.Session()
        self._initialize_session()

    def _initialize_session(self):
        """Initialize session with proper cookies and headers"""
        self.headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Origin': 'https://www.nseindia.com'
        }
        try:
            self.session.get("https://www.nseindia.com", headers=self.headers, timeout=10)
            self.session.get("https://www.nseindia.com/market-data/live-equity-market", 
                           headers=self.headers, timeout=10)
            time.sleep(1)
        except requests.RequestException:
            pass

    def _get_random_user_agent(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        return random.choice(user_agents)

    def rotate_user_agent(self):
        self.headers['User-Agent'] = self._get_random_user_agent()

    def get_index_details(self, category, list_only=False):
        category = category.upper().replace('&', '%26').replace(' ', '%20')
        self.rotate_user_agent()
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={category}"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()["data"]
            df = pd.DataFrame(data)

            # Remove 'meta' column if it exists
            df = df.drop(["meta"], axis=1, errors='ignore')

            # Set index to 'symbol' for better readability
            df = df.set_index("symbol", drop=False)

            # If only the symbol list is required
            if list_only:
                symbol_list = sorted(df.index.tolist())
                return symbol_list

            # Reorder columns as per your requirement
            column_order = [
                "symbol", "previousClose", "open", "dayHigh", "dayLow", "lastPrice", 
                "change", "pChange", "totalTradedVolume", "totalTradedValue", 
                "nearWKH", "nearWKL", "perChange30d", "perChange365d", "ffmc"
            ]
            # Filter only available columns to avoid KeyError
            column_order = [col for col in column_order if col in df.columns]
            df = df[column_order]

            # Replace invalid float values with None immediately
            df = df.replace([pd.NA, float('nan'), float('inf'), float('-inf')], None)
            # Ensure all numeric columns are properly typed and NaN-free
            for col in df.columns:
                if df[col].dtype in ['float64', 'float32']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').replace(np.nan, None)

            return df
        except requests.RequestException:
            self._initialize_session()
            return self.get_index_details(category, list_only)
        except (ValueError, KeyError):
            return None
    
    def pre_market_info(self, category='All'):
        pre_market_xref = {"NIFTY 50": "NIFTY", "Nifty Bank": "BANKNIFTY", "Emerge": "SME", "Securities in F&O": "FO",
                        "Others": "OTHERS", "All": "ALL"}
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market'
        ref = requests.get(ref_url, headers=self.headers)
        url = f"https://www.nseindia.com/api/market-data-pre-open?key={pre_market_xref[category]}"
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()
            data = response.json()["data"]
            processed_data = [{
                "symbol": i["metadata"]["symbol"],
                "previousClose": i["metadata"]["previousClose"],
                "iep": i["metadata"]["iep"],
                "change": i["metadata"]["change"],
                "pChange": i["metadata"]["pChange"],
                "lastPrice": i["metadata"]["lastPrice"],
                "finalQuantity": i["metadata"]["finalQuantity"],
                "totalTurnover": i["metadata"]["totalTurnover"],
                "marketCap": i["metadata"]["marketCap"],
                "yearHigh": i["metadata"]["yearHigh"],
                "yearLow": i["metadata"]["yearLow"],
                "totalBuyQuantity": i["detail"]["preOpenMarket"]["totalBuyQuantity"],
                "totalSellQuantity": i["detail"]["preOpenMarket"]["totalSellQuantity"],
                "atoBuyQty": i["detail"]["preOpenMarket"]["atoBuyQty"],
                "atoSellQty": i["detail"]["preOpenMarket"]["atoSellQty"],
                "lastUpdateTime": i["detail"]["preOpenMarket"]["lastUpdateTime"]
            } for i in data]
            df = pd.DataFrame(processed_data)
            df = df.set_index("symbol", drop=False)
            return df
        except (requests.RequestException, ValueError):
            return None

    def nifty_adv_dec_info(self, category='All'):
        pre_market_xref = {
            "NIFTY 50": "NIFTY", 
            "Nifty Bank": "BANKNIFTY", 
            "Emerge": "SME", 
            "Securities in F&O": "FO",
            "Others": "OTHERS", 
            "All": "ALL"
        }
        
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market'
        
        try:
            ref = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref.raise_for_status()
            
            url = f"https://www.nseindia.com/api/market-data-pre-open?key={pre_market_xref.get(category, 'ALL')}"
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract values from 'niftyPreopenStatus'
            nifty_status = data.get("niftyPreopenStatus", {})
            pChange = nifty_status.get("pChange", "N/A")
            change = nifty_status.get("change", "N/A")
            lastPrice = nifty_status.get("lastPrice", "N/A")
            
            # Extract Advances, Declines, Unchanged & Timestamp
            advances = data.get("advances", 0)
            declines = data.get("declines", 0)
            unchanged = data.get("unchanged", 0)
            timestamp = data.get("timestamp", "Unknown")

            # Create a single-row DataFrame
            df = pd.DataFrame([{
                "lastPrice": lastPrice,
                "change": change,
                "pChange": pChange,
                "advances": advances,
                "declines": declines,
                "unchanged": unchanged,
                "timestamp": timestamp
            }])
            
            return df

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Nifty Advance-Decline data: {e}")
            return None
        
    def all_nse_adv_dec_info(self, category='All'):
        pre_market_xref = {
            "NIFTY 50": "NIFTY", 
            "Nifty Bank": "BANKNIFTY", 
            "Emerge": "SME", 
            "Securities in F&O": "FO",
            "Others": "OTHERS", 
            "All": "ALL"
        }
        
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market'
        
        try:
            ref = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref.raise_for_status()
            
            url = f"https://www.nseindia.com/api/market-data-pre-open?key={pre_market_xref.get(category, 'ALL')}"
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract Advances, Declines, Unchanged & Timestamp
            advances = data.get("advances", 0)
            declines = data.get("declines", 0)
            unchanged = data.get("unchanged", 0)
            timestamp = data.get("timestamp", "Unknown")

            # Create a single-row DataFrame
            df = pd.DataFrame([{
                "advances": advances,
                "declines": declines,
                "unchanged": unchanged,
                "timestamp": timestamp
            }])
            
            return df

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching All NSE Advance-Decline data: {e}")
            return None
        
    def clearing_holidays(self, list_only=False):
        self.rotate_user_agent()
        holiday_type = "clearing"
        try:
            response = self.session.get(
                f"https://www.nseindia.com/api/holiday-master?type={holiday_type}",
                headers=self.headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract only "CD" (Capital Market) holiday data
            if "CM" in data:
                df = pd.DataFrame(data["CD"], columns=["Sr_no", "tradingDate", "weekDay", "description", "morning_session", "evening_session"])
                
                if list_only:
                    return df["tradingDate"].tolist()
                return df
            else:
                return None
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching clearing holidays: {e}")
            return None
    
    def trading_holidays(self, list_only=False):
        self.rotate_user_agent()
        holiday_type = "trading"
        try:
            response = self.session.get(
                f"https://www.nseindia.com/api/holiday-master?type={holiday_type}",
                headers=self.headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract only "CM" (Capital Market) holiday data
            if "CM" in data:
                df = pd.DataFrame(data["CM"], columns=["Sr_no", "tradingDate", "weekDay", "description", "morning_session", "evening_session"])
                
                if list_only:
                    return df["tradingDate"].tolist()
                return df
            else:
                return None
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching trading holidays: {e}")
            return None

    def is_nse_trading_holiday(self, date_str=None):
        holidays = self.trading_holidays(list_only=True)
        if holidays is None:
            return None
        date_format = "%d-%b-%Y"
        try:
            if date_str:
                date_obj = datetime.strptime(date_str, date_format)
            else:
                date_obj = datetime.today()
            formatted_date = date_obj.strftime(date_format)
            return formatted_date in holidays
        except ValueError:
            return None

    def is_nse_clearing_holiday(self, date_str=None):
        holidays = self.clearing_holidays(list_only=True)
        if holidays is None:
            return None
        date_format = "%d-%b-%Y"
        try:
            if date_str:
                date_obj = datetime.strptime(date_str, date_format)
            else:
                date_obj = datetime.today()
            formatted_date = date_obj.strftime(date_format)
            return formatted_date in holidays
        except ValueError:
            return None

    def equity_info(self, symbol):
        symbol = symbol.replace(' ', '%20').replace('&', '%26')
        self.rotate_user_agent()
        ref_url = f'https://www.nseindia.com/get-quotes/equity?symbol={symbol}'
        ref = requests.get(ref_url, headers=self.headers)
        try:
            url = f'https://www.nseindia.com/api/quote-equity?symbol={symbol}'
            data = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10).json()
            if not data or 'error' in data:
                return None
            return {
                "Symbol": symbol,
                "companyName": data['info']['companyName'],
                "industry": data['info']['industry'],
                "boardStatus": data['securityInfo']['boardStatus'],
                "tradingStatus": data['securityInfo']['tradingStatus'],
                "tradingSegment": data['securityInfo']['tradingSegment'],
                "derivatives": data['securityInfo']['derivatives'],
                "surveillance": data['securityInfo']['surveillance']['surv'],
                "surveillanceDesc": data['securityInfo']['surveillance']['desc'],
                "Facevalue": data['securityInfo']['faceValue']
            }
        except (requests.RequestException, ValueError):
            return None

    def price_info(self, symbol):
        symbol = symbol.replace(' ', '%20').replace('&', '%26')
        self.rotate_user_agent()
        ref_url = f'https://www.nseindia.com/get-quotes/equity?symbol={symbol}'
        ref = requests.get(ref_url, headers=self.headers)

        try:
            url = f'https://www.nseindia.com/api/quote-equity?symbol={symbol}'
            data = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10).json()
            url = f'https://www.nseindia.com/api/quote-equity?symbol={symbol}&section=trade_info'
            trade_data = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10).json()

            if not data or 'error' in data:
                return None

            # Extract bid and ask data (handling missing values)
            bid_data = trade_data.get('marketDeptOrderBook', {}).get('bid', [])
            ask_data = trade_data.get('marketDeptOrderBook', {}).get('ask', [])
            total_buy_qty = trade_data.get('marketDeptOrderBook', {}).get('totalBuyQuantity', 0)
            total_sell_qty = trade_data.get('marketDeptOrderBook', {}).get('totalSellQuantity', 0)

            # Extract first 5 bid/ask levels (fill missing with 0)
            bid_prices = [entry.get("price", 0) or 0 for entry in bid_data[:5]] + [0] * (5 - len(bid_data))
            bid_quantities = [entry.get("quantity", 0) or 0 for entry in bid_data[:5]] + [0] * (5 - len(bid_data))

            ask_prices = [entry.get("price", 0) or 0 for entry in ask_data[:5]] + [0] * (5 - len(ask_data))
            ask_quantities = [entry.get("quantity", 0) or 0 for entry in ask_data[:5]] + [0] * (5 - len(ask_data))

            return {
                "Symbol": symbol,
                "PreviousClose": data['priceInfo']['previousClose'],
                "LastTradedPrice": data['priceInfo']['lastPrice'],
                "Change": data['priceInfo']['change'],
                "PercentChange": data['priceInfo']['pChange'],
                "deliveryToTradedQuantity": trade_data['securityWiseDP']['deliveryToTradedQuantity'],
                "Open": data['priceInfo']['open'],
                "Close": data['priceInfo']['close'],
                "High": data['priceInfo']['intraDayHighLow']['max'],
                "Low": data['priceInfo']['intraDayHighLow']['min'],
                "VWAP": data['priceInfo']['vwap'],
                "UpperCircuit": data['priceInfo']['upperCP'],
                "LowerCircuit": data['priceInfo']['lowerCP'],
                "Macro": data['industryInfo']['macro'],
                "Sector": data['industryInfo']['sector'],
                "Industry": data['industryInfo']['industry'],
                "BasicIndustry": data['industryInfo']['basicIndustry'],
                # Store bid/ask levels separately instead of lists
                "Bid Price 1": bid_prices[0], "Bid Quantity 1": bid_quantities[0],
                "Bid Price 2": bid_prices[1], "Bid Quantity 2": bid_quantities[1],
                "Bid Price 3": bid_prices[2], "Bid Quantity 3": bid_quantities[2],
                "Bid Price 4": bid_prices[3], "Bid Quantity 4": bid_quantities[3],
                "Bid Price 5": bid_prices[4], "Bid Quantity 5": bid_quantities[4],
                "Ask Price 1": ask_prices[0], "Ask Quantity 1": ask_quantities[0],
                "Ask Price 2": ask_prices[1], "Ask Quantity 2": ask_quantities[1],
                "Ask Price 3": ask_prices[2], "Ask Quantity 3": ask_quantities[2],
                "Ask Price 4": ask_prices[3], "Ask Quantity 4": ask_quantities[3],
                "Ask Price 5": ask_prices[4], "Ask Quantity 5": ask_quantities[4],
                "totalBuyQuantity": total_buy_qty,
                "totalSellQuantity": total_sell_qty
            }
        except (requests.RequestException, ValueError):
            return None

    def futures_data(self, symbol, indices=False):
        symbol = symbol.replace(' ', '%20').replace('&', '%26')
        self.rotate_user_agent()
        ref_url = f'https://www.nseindia.com/get-quotes/derivatives?symbol={symbol}'
        ref = requests.get(ref_url, headers=self.headers)
        try:
            url = f'https://www.nseindia.com/api/quote-derivative?symbol={symbol}'
            data = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10).json()
            lst = [i["metadata"] for i in data["stocks"] if i["metadata"]["instrumentType"] == ("Index Futures" if indices else "Stock Futures")]
            df = pd.DataFrame(lst)
            df = df.set_index("identifier", drop=True)
            return df
        except (requests.RequestException, ValueError):
            return None

    def get_option_chain(self, symbol, indices=False):
        symbol = symbol.replace(' ', '%20').replace('&', '%26')
        self.rotate_user_agent()
        ref_url = f'https://www.nseindia.com/get-quotes/derivatives?symbol={symbol}'
        ref = requests.get(ref_url, headers=self.headers)
        url = f"https://www.nseindia.com/api/option-chain-{'indices' if indices else 'equities'}?symbol={symbol}"
        try:
            data = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10).json()["records"]
            my_df = []
            for i in data["data"]:
                for k, v in i.items():
                    if k in ["CE", "PE"]:
                        info = v
                        info["instrumentType"] = k
                        info["timestamp"] = data["timestamp"]
                        my_df.append(info)
            df = pd.DataFrame(my_df)
            df = df.set_index("identifier", drop=True)
            return df
        except (requests.RequestException, ValueError):
            return None

    def get_52week_high_low(self, stock=None):
        self.rotate_user_agent()
        url = f'https://nsearchives.nseindia.com/content/CM_52_wk_High_low_{datetime.now().strftime("%d%m%Y")}.csv'
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = StringIO(response.text.replace(
                '"Disclaimer - The Data provided in the adjusted 52 week high and adjusted 52 week low columns  are adjusted for corporate actions (bonus, splits & rights).For actual (unadjusted) 52 week high & low prices, kindly refer bhavcopy."\n"Effective for 25-Jan-2024"\n',
                ''))
            df = pd.read_csv(data)
            if stock:
                row = df[df['SYMBOL'] == stock]
                if row.empty:
                    return None
                return {
                    "Symbol": stock,
                    "52 Week High": row["Adjusted 52_Week_High"].values[0],
                    "52 Week High Date": row["52_Week_High_Date"].values[0],
                    "52 Week Low": row["Adjusted 52_Week_Low"].values[0],
                    "52 Week Low Date": row["52_Week_Low_DT"].values[0]
                }
            return df
        except requests.RequestException:
            return None

    def fno_bhav_copy(self, trade_date: str = ""):
        self.rotate_user_agent()
        bhav_df = pd.DataFrame()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = 'https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_'
        payload = f"{str(trade_date.strftime('%Y%m%d'))}_F_0000.csv.zip"
        try:
            request_bhav = self.session.get(url + payload, headers=self.headers, timeout=10)
            if request_bhav.status_code == 200:
                zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
                for file_name in zip_bhav.filelist:
                    if file_name:
                        bhav_df = pd.read_csv(zip_bhav.open(file_name))
            else:
                url2 = "https://www.nseindia.com/api/reports?archives=" \
                       "%5B%7B%22name%22%3A%22F%26O%20-%20Bhavcopy(csv)%22%2C%22type%22%3A%22archives%22%2C%22category%22" \
                       f"%3A%22derivatives%22%2C%22section%22%3A%22equity%22%7D%5D&date={str(trade_date.strftime('%d-%b-%Y'))}" \
                       "&type=equity&mode=single"
                ref = requests.get('https://www.nseindia.com/reports-archives', headers=self.headers)
                request_bhav = self.session.get(url2, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
                request_bhav.raise_for_status()
                zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
                for file_name in zip_bhav.filelist:
                    if file_name:
                        bhav_df = pd.read_csv(zip_bhav.open(file_name))
            return bhav_df
        except (requests.RequestException, FileNotFoundError):
            return None

    def bhav_copy_with_delivery(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        use_date = trade_date.strftime("%d%m%Y")
        url = f'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{use_date}.csv'
        try:
            request_bhav = requests.get(url, headers=self.headers, timeout=10)
            request_bhav.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(request_bhav.content))
            bhav_df.columns = [name.replace(' ', '') for name in bhav_df.columns]
            bhav_df['SERIES'] = bhav_df['SERIES'].str.replace(' ', '')
            bhav_df['DATE1'] = bhav_df['DATE1'].str.replace(' ', '')
            return bhav_df
        except requests.RequestException:
            return None

    def equity_bhav_copy(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = 'https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_'
        payload = f"{str(trade_date.strftime('%Y%m%d'))}_F_0000.csv.zip"
        try:
            request_bhav = requests.get(url + payload, headers=self.headers, timeout=10)
            request_bhav.raise_for_status()
            zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
            bhav_df = pd.DataFrame()
            for file_name in zip_bhav.filelist:
                if file_name:
                    bhav_df = pd.read_csv(zip_bhav.open(file_name))
            return bhav_df
        except requests.RequestException:
            return None

    def bhav_copy_indices(self, trade_date: str):
        self.rotate_user_agent()
        trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
        url = f"https://nsearchives.nseindia.com/content/indices/ind_close_all_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
        try:
            nse_resp = requests.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            bhav_df = pd.read_csv(BytesIO(nse_resp.content))
            return bhav_df
        except (requests.RequestException, ValueError):
            return None

    def fii_dii_activity(self):
        self.rotate_user_agent()
        url = "https://www.nseindia.com/api/fiidiiTradeReact"
        try:
            data_json = requests.get(url, headers=self.headers, timeout=10).json()
            return pd.DataFrame(data_json)
        except (requests.RequestException, ValueError):
            return None

    def get_index_historic_data(self, index: str, from_date: str = None, to_date: str = None):
        index_data_columns = ['TIMESTAMP', 'INDEX_NAME', 'OPEN_INDEX_VAL', 'HIGH_INDEX_VAL', 'CLOSE_INDEX_VAL',
                              'LOW_INDEX_VAL', 'TRADED_QTY', 'TURN_OVER']
        if not from_date or not to_date:
            raise ValueError('Please provide valid parameters')
        try:
            from_dt = datetime.strptime(from_date, "%d-%m-%Y")
            to_dt = datetime.strptime(to_date, "%d-%m-%Y")
            if (to_dt - from_dt).days < 1:
                raise ValueError('to_date should be greater than from_date')
        except Exception as e:
            raise ValueError(f'Either or both from_date = {from_date} || to_date = {to_date} are not valid value')

        nse_df = pd.DataFrame(columns=index_data_columns)
        from_date = datetime.strptime(from_date, "%d-%m-%Y")
        to_date = datetime.strptime(to_date, "%d-%m-%Y")
        load_days = (to_date - from_date).days

        while load_days > 0:
            if load_days > 365:
                end_date = (from_date + timedelta(364)).strftime("%d-%m-%Y")
                start_date = from_date.strftime("%d-%m-%Y")
            else:
                end_date = to_date.strftime("%d-%m-%Y")
                start_date = from_date.strftime("%d-%m-%Y")

            data_df = self.get_index_data(index=index, from_date=start_date, to_date=end_date)
            if data_df is not None:
                from_date = from_date + timedelta(365)
                load_days = (to_date - from_date).days
                nse_df = pd.concat([nse_df, data_df], ignore_index=True)
        return nse_df

    def get_index_data(self, index: str, from_date: str, to_date: str):
        self.rotate_user_agent()
        index_data_columns = ['TIMESTAMP', 'INDEX_NAME', 'OPEN_INDEX_VAL', 'HIGH_INDEX_VAL', 'CLOSE_INDEX_VAL',
                              'LOW_INDEX_VAL', 'TRADED_QTY', 'TURN_OVER']
        index = index.replace(' ', '%20').upper()
        url = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={index}&from={from_date}&to={to_date}"
        try:
            data_json = self.session.get(url, headers=self.headers, timeout=10).json()
            data_close_df = pd.DataFrame(data_json['data']['indexCloseOnlineRecords']).drop(columns=['_id', "EOD_TIMESTAMP"])
            data_turnover_df = pd.DataFrame(data_json['data']['indexTurnoverRecords']).drop(columns=['_id', 'HIT_INDEX_NAME_UPPER'])
            data_df = pd.merge(data_close_df, data_turnover_df, on='TIMESTAMP', how='inner')
            data_df.drop(columns='TIMESTAMP', inplace=True)
            unwanted_str_list = ['FH_', 'EOD_', 'HIT_']
            new_col = [name.replace(unwanted, '') for unwanted in unwanted_str_list for name in data_df.columns]
            data_df.columns = new_col
            return data_df[index_data_columns]
        except (requests.RequestException, ValueError):
            return None

    def get_equity_full_list(self, list_only=False):
        self.rotate_user_agent()
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        try:
            nse_resp = self.session.get(url, headers=self.headers, timeout=10)
            nse_resp.raise_for_status()
            data_df = pd.read_csv(BytesIO(nse_resp.content))
            data_df = data_df[['SYMBOL', 'NAME OF COMPANY', ' SERIES', ' DATE OF LISTING', ' FACE VALUE']]
            if list_only:
                return data_df['SYMBOL'].tolist()
            return data_df
        except (requests.RequestException, ValueError):
            return None

    def get_fno_full_list(self, list_only=False):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/products-services/equity-derivatives-list-underlyings-information'
        ref = requests.get(ref_url, headers=self.headers)
        url = "https://www.nseindia.com/api/underlying-information"
    
        try:
            data_obj = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data_obj.raise_for_status()
            data_dict = data_obj.json()
            
            # Convert the relevant data to a DataFrame
            data_df = pd.DataFrame(data_dict['data']['UnderlyingList'])
            
            # Rename columns for clarity
            data_df = data_df.rename(columns={"serialNumber": "Serial Number", "symbol": "Symbol", "underlying": "Underlying"})
            
            if list_only:
                return data_df['Symbol'].tolist()
            return data_df[['Serial Number', 'Symbol', 'Underlying']]
        except (requests.RequestException, ValueError) as e:
            print(f"Error: {e}")
            return None

    def get_gainers_losers(self):
        self.rotate_user_agent()
        gain_loss_dict = {}
        ref_url = 'https://www.nseindia.com/market-data/top-gainers-losers'
        ref = requests.get(ref_url, headers=self.headers)
        try:
            url = 'https://www.nseindia.com/api/live-analysis-variations?index=gainers'
            data_obj = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data_obj.raise_for_status()
            data_dict = data_obj.json()
            
            nifty_gainer = pd.DataFrame(data_dict['NIFTY']['data'])['symbol'].to_list()
            banknifty_gainer = pd.DataFrame(data_dict['BANKNIFTY']['data'])['symbol'].to_list()
            next50_gainer = pd.DataFrame(data_dict['NIFTYNEXT50']['data'])['symbol'].to_list()
            allsec_gainer = pd.DataFrame(data_dict['allSec']['data'])['symbol'].to_list()
            fno_gainer = pd.DataFrame(data_dict['FOSec']['data'])['symbol'].to_list()

            url = 'https://www.nseindia.com/api/live-analysis-variations?index=loosers'
            data_obj = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data_obj.raise_for_status()
            data_dict = data_obj.json()

            nifty_loser = pd.DataFrame(data_dict['NIFTY']['data'])['symbol'].to_list()
            banknifty_loser = pd.DataFrame(data_dict['BANKNIFTY']['data'])['symbol'].to_list()
            next50_loser = pd.DataFrame(data_dict['NIFTYNEXT50']['data'])['symbol'].to_list()
            allsec_loser = pd.DataFrame(data_dict['allSec']['data'])['symbol'].to_list()
            fno_loser = pd.DataFrame(data_dict['FOSec']['data'])['symbol'].to_list()

            gain_dict = {
                'Nifty Gainer': nifty_gainer,
                'Bank Nifty Gainer': banknifty_gainer,
                'Nifty Next 50 Gainer': next50_gainer,
                'All Securities Gainer': allsec_gainer,
                'FNO Gainer': fno_gainer
            }
            loss_dict = {
                'Nifty Loser': nifty_loser,
                'Bank Nifty Loser': banknifty_loser,
                'Nifty Next 50 Loser': next50_loser,
                'All Securities Loser': allsec_loser,
                'FNO Loser': fno_loser
            }
            return gain_dict, loss_dict
        except (requests.RequestException, ValueError):
            return None

    def get_corporate_action(self, from_date_str: str = None, to_date_str: str = None, filter: str = None):
        self.rotate_user_agent()
        
        # Default date range (next 30 days)
        if from_date_str is None:
            from_date = datetime.now()
            from_date_str = from_date.strftime("%d-%m-%Y")
        if to_date_str is None:
            to_date = datetime.now() + timedelta(days=30)
            to_date_str = to_date.strftime("%d-%m-%Y")

        # Reference URL for cookies
        ref_url = 'https://www.nseindia.com/companies-listing/corporate-filings-actions'
        ref = requests.get(ref_url, headers=self.headers)

        try:
            url = f"https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date={from_date_str}&to_date={to_date_str}"
            data_obj = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            
            # Check if the response is valid
            data_obj.raise_for_status()
            json_data = data_obj.json()
            
            # Convert response to DataFrame
            corp_action = pd.DataFrame(json_data)

            # Apply filtering if needed
            if filter is not None:
                corp_action = corp_action[corp_action['subject'].str.contains(filter, case=False, na=False)]
            
            # Rename columns
            column_mapping = {
                "symbol": "SYMBOL",
                "comp": "COMPANY NAME",
                "series": "SERIES",
                "subject": "PURPOSE",
                "faceVal": "FACE VALUE",
                "exDate": "EX-DATE",
                "recDate": "RECORD DATE",
                "bcStartDate": "BOOK CLOSURE START DATE",
                "bcEndDate": "BOOK CLOSURE END DATE"
            }
            corp_action = corp_action.rename(columns=column_mapping)

            # Reorder columns
            column_order = [
                "SYMBOL", "COMPANY NAME", "SERIES", "PURPOSE", "FACE VALUE",
                "EX-DATE", "RECORD DATE", "BOOK CLOSURE START DATE", "BOOK CLOSURE END DATE"
            ]
            corp_action = corp_action[column_order]

            # Debug: Print the final number of records
            print(f"Final number of records in DataFrame: {len(corp_action)}")

            return corp_action

        except (requests.RequestException, ValueError) as e:
            print(f"Error occurred: {str(e)}")
            return None
        
    def get_corporate_action_all(self):
        self.rotate_user_agent()
    
        # Reference URL for cookies
        ref_url = 'https://www.nseindia.com/companies-listing/corporate-filings-actions'
        ref = requests.get(ref_url, headers=self.headers)

        try:
            url = f"https://www.nseindia.com/api/corporates-corporateActions?index=equities"
            data_obj = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            
            # Check if the response is valid
            data_obj.raise_for_status()
            json_data = data_obj.json()
            
            # Convert response to DataFrame
            corp_action = pd.DataFrame(json_data)
            
            # Rename columns
            column_mapping = {
                "symbol": "SYMBOL",
                "comp": "COMPANY NAME",
                "series": "SERIES",
                "subject": "PURPOSE",
                "faceVal": "FACE VALUE",
                "exDate": "EX-DATE",
                "recDate": "RECORD DATE",
                "bcStartDate": "BOOK CLOSURE START DATE",
                "bcEndDate": "BOOK CLOSURE END DATE"
            }
            corp_action = corp_action.rename(columns=column_mapping)

            # Reorder columns
            column_order = [
                "SYMBOL", "COMPANY NAME", "SERIES", "PURPOSE", "FACE VALUE",
                "EX-DATE", "RECORD DATE", "BOOK CLOSURE START DATE", "BOOK CLOSURE END DATE"
            ]
            corp_action = corp_action[column_order]

            return corp_action

        except (requests.RequestException, ValueError) as e:
            print(f"Error occurred: {str(e)}")
            return None

    def most_active_equity_stocks_by_volume(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-equities'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/live-analysis-most-active-securities?index=volume'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_equity_stocks_by_value(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-equities'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/live-analysis-most-active-securities?index=value'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_index_calls(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=calls-index-vol'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['OPTIDX']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_index_puts(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=puts-index-vol'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['OPTIDX']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_stock_calls(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=calls-stocks-vol'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['OPTSTK']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_stock_puts(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=puts-stocks-vol'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['OPTSTK']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_stock_calls_value(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=calls-stocks-val'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['OPTSTK']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_stock_puts_value(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=puts-stocks-val'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['OPTSTK']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None 

    def most_active_contracts_by_oi(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=oi'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['volume']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_contracts_by_volume(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=contracts'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['volume']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_futures_contracts_by_volume(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=futures'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['volume']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def most_active_options_contracts_by_volume(self):
        self.rotate_user_agent()
        ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
        ref = requests.get(ref_url, headers=self.headers)
        url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=options&limit=20'
        try:
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['volume']['data'])
            return df if not df.empty else None
        except (requests.RequestException, ValueError):
            return None

    def get_insider_trading(self, from_date: str = None, to_date: str = None):
        self.rotate_user_agent()
        
        if from_date is None:
            from_date = datetime.now() - timedelta(days=30)
            from_date_str = from_date.strftime("%d-%m-%Y")
            to_date_str = datetime.now().strftime("%d-%m-%Y")
        else:
            from_date_str = from_date
        
        if to_date is None:
            to_date_str = datetime.now().strftime("%d-%m-%Y")
        else:
            to_date_str = to_date
        
        ref_url = 'https://www.nseindia.com/companies-listing/corporate-filings-insider-trading'
        ref = requests.get(ref_url, headers=self.headers)

        try:
            url = f'https://www.nseindia.com/api/corporates-pit?index=equities&from_date={from_date_str}&to_date={to_date_str}'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            data = response.json()
            df = pd.DataFrame(data['data'])

            # Changing only the column order
            column_order = [
                "symbol", "company", "anex", "acqName", "personCategory",
                "secType", "befAcqSharesNo", "befAcqSharesPer", "remarks", "secAcq",
                "secVal", "tdpTransactionType", "securitiesTypePost", "afterAcqSharesNo",
                "afterAcqSharesPer", "acqfromDt", "acqtoDt", "intimDt", "acqMode",
                "derivativeType", "tdpDerivativeContractType", "buyValue", "buyQuantity",
                "sellValue", "sellquantity", "exchange", "remarks", "date", "xbrl"
            ]

            df = df[column_order]  # Reordering DataFrame columns
            
            return df
        except (requests.RequestException, ValueError):
            return None
        
    def get_52week_high(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/market-data/52-week-high-equity-market'
        api_url = 'https://www.nseindia.com/api/live-analysis-data-52weekhighstock'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()
            
            if 'data' in data and isinstance(data['data'], list):
                df = pd.DataFrame(data['data'])

                # Selecting and ordering columns
                df = df[['symbol', 'series', 'ltp', 'pChange', 'new52WHL', 'prev52WHL', 'prevHLDate']]

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if no data is found

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching 52-week high data: {e}")
            return None
        
    def get_52week_low(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/market-data/52-week-low-equity-market'
        api_url = 'https://www.nseindia.com/api/live-analysis-data-52weeklowstock'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()
            
            if 'data' in data and isinstance(data['data'], list):
                df = pd.DataFrame(data['data'])

                # Selecting and ordering columns
                df = df[['symbol', 'series', 'ltp', 'pChange', 'new52WHL', 'prev52WHL', 'prevHLDate']]

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if no data is found

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching 52-week low data: {e}")
            return None
    

    def get_market_statistics(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com'
        api_url = 'https://www.nseindia.com/api/NextApi/apiClient?functionName=getMarketStatistics'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()
            # print("Raw API Response:", data)  # Debugging Step

            if 'data' in data:
                snapshot = data['data'].get('snapshotCapitalMarket', {})
                fifty_two_week = data['data'].get('fiftyTwoWeek', {})
                circuit = data['data'].get('circuit', {})

                # Creating a DataFrame with extracted values
                df = pd.DataFrame([{
                    'total': snapshot.get('total', None),
                    'advances': snapshot.get('advances', None),
                    'declines': snapshot.get('declines', None),
                    'unchange': snapshot.get('unchange', None),
                    'high': fifty_two_week.get('high', None),
                    'low': fifty_two_week.get('low', None),
                    'upper': circuit.get('upper', None),
                    'lower': circuit.get('lower', None),
                }])

                print("DataFrame Created:\n", df)  # Debugging Step
                
                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if no data is found

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching market statistics: {e}")
            return None
        
    def get_block_deal(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/market-data/block-deal-watch'
        api_url = 'https://www.nseindia.com/api/block-deal'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()
            
            if 'data' in data and isinstance(data['data'], list):
                df = pd.DataFrame(data['data'])

                # Selecting and ordering columns
                df = df[['session','symbol', 'series', 'open', 'dayHigh', 'dayLow', 'lastPrice', 'previousClose', 'pchange', 'totalTradedVolume', 'totalTradedValue']]

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if no data is found

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Block deal data: {e}")
            return None

    def get_upcoming_results_calendar(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/companies-listing/corporate-filings-event-calendar'
        api_url = 'https://www.nseindia.com/api/event-calendar?'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()
            
            # Directly assume data is a list instead of checking 'data' key
            if isinstance(data, list):
                df = pd.DataFrame(data)

                # Selecting and ordering columns
                required_columns = ['symbol', 'company', 'purpose', 'bm_desc', 'date']
                df = df[required_columns]

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if data is not a list or is empty

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Event Calendar data: {e}")
            return None
        
    def get_shareholding_patterns(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern'
        api_url = 'https://www.nseindia.com/api/corporate-share-holdings-master?index=equities'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()
            
            # Directly assume data is a list instead of checking 'data' key
            if isinstance(data, list):
                df = pd.DataFrame(data)

                # Selecting and ordering columns
                required_columns = ['symbol', 'name', 'pr_and_prgrp', 'public_val', 'employeeTrusts', 'revisedStatus', 'date', 'submissionDate', 'revisionDate', 'xbrl', 'broadcastDate', 'systemDate', 'timeDifference']
                df = df[required_columns]

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if data is not a list or is empty

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Shareholding Patterns data: {e}")
            return None
        
    def get_gifty_nifty(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/'
        api_url = 'https://www.nseindia.com/api/NextApi/apiClient?functionName=getGiftNifty'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()

            # Extract Gift Nifty and USDINR data
            if isinstance(data, dict) and "data" in data:
                gift_nifty_data = data["data"].get("giftNifty", {})
                usd_inr_data = data["data"].get("usdInr", {})

                # Convert to DataFrame
                df = pd.DataFrame([{
                    "symbol": gift_nifty_data.get("symbol"),
                    "lastprice": gift_nifty_data.get("lastprice"),
                    "daychange": gift_nifty_data.get("daychange"),
                    "perchange": gift_nifty_data.get("perchange"),
                    "contractstraded": gift_nifty_data.get("contractstraded"),
                    "timestmp": gift_nifty_data.get("timestmp"),
                    "expirydate": gift_nifty_data.get("expirydate"),
                    "usdInr_symbol": usd_inr_data.get("symbol"),  # USDINR Symbol
                    "usdInr_ltp": usd_inr_data.get("ltp"),  # USDINR Last Traded Price
                    "usdInr_updated_time": usd_inr_data.get("updated_time"),  # USDINR Last Updated Time
                    "usdInr_expiry_dt": usd_inr_data.get("expiry_dt"),  # USDINR Expiry Date
                }])

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if data is missing

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Gift Nifty and USDINR data: {e}")
            return None
    
    def market_watch_all_indices(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/market-data/index-performances'
        api_url = 'https://www.nseindia.com/api/allIndices'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()
            
            if 'data' in data and isinstance(data['data'], list):
                df = pd.DataFrame(data['data'])

                # Selecting and ordering columns
                columns = ['key', 'index', 'indexSymbol', 'last', 'variation', 'percentChange', 'open', 'high', 'low',
                        'previousClose', 'yearHigh', 'yearLow', 'pe', 'pb', 'dy', 'declines', 'advances', 'unchanged',
                        'perChange30d', 'perChange365d', 'previousDayVal', 'oneWeekAgoVal', 'oneMonthAgoVal', 'oneYearAgoVal']
                
                df = df[columns]

                # **Fix NaN values** to avoid JSON conversion issues
                df = df.fillna(0)  # Replace NaN with 0
                df = df.replace({float('inf'): 0, float('-inf'): 0})  # Replace infinite values with 0

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if no data is found

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching all indices data: {e}")
            return None
        
    def get_live_option_chain(self, symbol: str, expiry_date: str = None, oi_mode: str = "full", indices: bool = False):
        symbol = symbol.replace(' ', '%20').replace('&', '%26')
        self.rotate_user_agent()
        
        ref_url = f'https://www.nseindia.com/get-quotes/derivatives?symbol={symbol}'
        ref = requests.get(ref_url, headers=self.headers)
        
        url = f"https://www.nseindia.com/api/option-chain-{'indices' if indices else 'equities'}?symbol={symbol}"
        
        try:
            payload = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10).json()
            
            if expiry_date:
                exp_date = pd.to_datetime(expiry_date, format='%d-%m-%Y')
                expiry_date = exp_date.strftime('%d-%b-%Y')

            # Define column names with Underlying_Value as the last column
            if oi_mode == 'compact':
                col_names = ['Fetch_Time', 'Symbol', 'Expiry_Date', 'CALLS_OI', 'CALLS_Chng_in_OI', 'CALLS_Volume', 'CALLS_IV',
                            'CALLS_LTP', 'CALLS_Net_Chng', 'Strike_Price', 'PUTS_OI', 'PUTS_Chng_in_OI', 'PUTS_Volume',
                            'PUTS_IV', 'PUTS_LTP', 'PUTS_Net_Chng', 'Underlying_Value']
            else:
                col_names = ['Fetch_Time', 'Symbol', 'Expiry_Date', 'CALLS_OI', 'CALLS_Chng_in_OI', 'CALLS_Volume', 'CALLS_IV',
                            'CALLS_LTP', 'CALLS_Net_Chng', 'CALLS_Bid_Qty', 'CALLS_Bid_Price', 'CALLS_Ask_Price',
                            'CALLS_Ask_Qty', 'Strike_Price', 'PUTS_Bid_Qty', 'PUTS_Bid_Price', 'PUTS_Ask_Price', 'PUTS_Ask_Qty',
                            'PUTS_Net_Chng', 'PUTS_LTP', 'PUTS_IV', 'PUTS_Volume', 'PUTS_Chng_in_OI', 'PUTS_OI', 'Underlying_Value']

            # Define dtypes to avoid inference issues
            dtypes = {
                'Fetch_Time': 'object',
                'Symbol': 'object',
                'Expiry_Date': 'object',
                'Strike_Price': 'float64',
                'CALLS_OI': 'int64', 'CALLS_Chng_in_OI': 'int64', 'CALLS_Volume': 'int64', 'CALLS_IV': 'float64',
                'CALLS_LTP': 'float64', 'CALLS_Net_Chng': 'float64',
                'PUTS_OI': 'int64', 'PUTS_Chng_in_OI': 'int64', 'PUTS_Volume': 'int64', 'PUTS_IV': 'float64',
                'PUTS_LTP': 'float64', 'PUTS_Net_Chng': 'float64',
                'Underlying_Value': 'float64'
            }
            if oi_mode == 'full':
                dtypes.update({
                    'CALLS_Bid_Qty': 'int64', 'CALLS_Bid_Price': 'float64', 'CALLS_Ask_Price': 'float64', 'CALLS_Ask_Qty': 'int64',
                    'PUTS_Bid_Qty': 'int64', 'PUTS_Bid_Price': 'float64', 'PUTS_Ask_Price': 'float64', 'PUTS_Ask_Qty': 'int64'
                })

            # Check if payload has data
            if not payload.get('records') or not payload['records'].get('data'):
                return pd.DataFrame(columns=col_names).astype(dtypes)

            # Collect rows in a list instead of concatenating in loop
            rows = []
            for record in payload['records']['data']:
                if not expiry_date or (record['expiryDate'] == expiry_date):
                    oi_row = {
                        'Fetch_Time': payload['records']['timestamp'],
                        'Symbol': symbol,
                        'Expiry_Date': record['expiryDate'],
                        'Strike_Price': record['strikePrice'],
                        'CALLS_OI': record.get('CE', {}).get('openInterest', 0),
                        'CALLS_Chng_in_OI': record.get('CE', {}).get('changeinOpenInterest', 0),
                        'CALLS_Volume': record.get('CE', {}).get('totalTradedVolume', 0),
                        'CALLS_IV': record.get('CE', {}).get('impliedVolatility', 0),
                        'CALLS_LTP': record.get('CE', {}).get('lastPrice', 0),
                        'CALLS_Net_Chng': record.get('CE', {}).get('change', 0),
                        'PUTS_OI': record.get('PE', {}).get('openInterest', 0),
                        'PUTS_Chng_in_OI': record.get('PE', {}).get('changeinOpenInterest', 0),
                        'PUTS_Volume': record.get('PE', {}).get('totalTradedVolume', 0),
                        'PUTS_IV': record.get('PE', {}).get('impliedVolatility', 0),
                        'PUTS_LTP': record.get('PE', {}).get('lastPrice', 0),
                        'PUTS_Net_Chng': record.get('PE', {}).get('change', 0),
                        'Underlying_Value': record.get('PE', {}).get('underlyingValue', 0)  # Added as last field
                    }
                    if oi_mode == 'full':
                        oi_row.update({
                            'CALLS_Bid_Qty': record.get('CE', {}).get('bidQty', 0),
                            'CALLS_Bid_Price': record.get('CE', {}).get('bidprice', 0),
                            'CALLS_Ask_Price': record.get('CE', {}).get('askPrice', 0),
                            'CALLS_Ask_Qty': record.get('CE', {}).get('askQty', 0),
                            'PUTS_Bid_Qty': record.get('PE', {}).get('bidQty', 0),
                            'PUTS_Bid_Price': record.get('PE', {}).get('bidprice', 0),
                            'PUTS_Ask_Price': record.get('PE', {}).get('askPrice', 0),
                            'PUTS_Ask_Qty': record.get('PE', {}).get('askQty', 0)
                        })

                    rows.append(oi_row)

            # Create DataFrame once with all rows
            if rows:
                oi_data = pd.DataFrame(rows, columns=col_names).astype(dtypes)  # Explicitly set column order
            else:
                oi_data = pd.DataFrame(columns=col_names).astype(dtypes)

            return oi_data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame(columns=col_names)
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            return pd.DataFrame(columns=col_names)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return pd.DataFrame(columns=col_names)
        
    def get_corporate_announcement(self, from_date=None, to_date=None):
        """
        Fetch corporate announcements from NSE India within a given date range.
        If no date range is provided, defaults to today's date.

        Parameters:
            from_date (str): Start date in DD-MM-YYYY format (default: today)
            to_date (str): End date in DD-MM-YYYY format (default: today)

        Returns:
            pd.DataFrame or None: DataFrame containing announcements, or None if empty/error
        """
        # --- Default date handling ---
        today_str = datetime.now().strftime("%d-%m-%Y")
        from_date = from_date or today_str
        to_date = to_date or today_str

        # --- Rotate user-agent for reliability ---
        self.rotate_user_agent()

        # --- NSE URLs ---
        ref_url = "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
        api_url = (
            f"https://www.nseindia.com/api/corporate-announcements?"
            f"index=equities&from_date={from_date}&to_date={to_date}&reqXbrl=false"
        )

        try:
            # Step 1: Get session cookies
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()

            # Step 2: API request with valid session cookies
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()

            # Step 3: Convert JSON to DataFrame
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)

                # Expected NSE JSON keys
                columns = ['symbol', 'sm_name','smIndustry', 'desc', 'attchmntText', 'attchmntFile', 'fileSize', 'an_dt']
                df = df[[col for col in columns if col in df.columns]]

                # Data cleaning
                df = df.fillna("").replace({float('inf'): "", float('-inf'): ""})

                return df if not df.empty else None
            else:
                print(f"No announcements found for {from_date} to {to_date}")
                return None

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"❌ Error fetching corporate announcements: {e}")
            return None
        
    def get_active_contracts(self, symbol: str, expiry_date: str = None):
        self.rotate_user_agent()
        
        ref_url = f'https://www.nseindia.com/get-quotes/derivatives?symbol={symbol}'
        ref = requests.get(ref_url, headers=self.headers)
        
        url = f"https://www.nseindia.com/api/quote-derivative?symbol={symbol}"
        
        try:
            payload = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10).json()
            
            if expiry_date:
                exp_date = pd.to_datetime(expiry_date, format='%d-%m-%Y')
                expiry_date = exp_date.strftime('%d-%b-%Y')
            
            # Filter only Stock Options data
            stocks_data = [
                stock for stock in payload.get("stocks", [])
                if stock["metadata"]["instrumentType"] == "Stock Options"
            ]
            
            # If expiry_date is specified, filter by expiry date as well
            if expiry_date:
                stocks_data = [
                    stock for stock in stocks_data
                    if stock["metadata"]["expiryDate"] == expiry_date
                ]
            
            # Prepare table data
            table_data = []
            for stock in stocks_data:
                metadata = stock["metadata"]
                marketDeptOrderBook = stock["marketDeptOrderBook"]
                trade_info = stock["marketDeptOrderBook"]["tradeInfo"]
                table_data.append({
                    "Instrument Type": metadata["instrumentType"],
                    "Expiry Date": metadata["expiryDate"],
                    "Option Type": metadata["optionType"],
                    "Strike Price": metadata["strikePrice"],
                    "Open": metadata.get("openPrice", 0),
                    "High": metadata.get("highPrice", 0),
                    "Low": metadata.get("lowPrice", 0),
                    "closePrice":metadata.get("closePrice", 0),
                    "Prev Close": metadata.get("prevClose", 0),
                    "Last": metadata.get("lastPrice", 0),
                    "Change": metadata.get("change", 0),
                    "%Change": metadata.get("pChange", 0),
                    "Volume (Contracts)": metadata.get("numberOfContractsTraded", 0),
                    "Value (₹ Lakhs)": metadata.get("totalTurnover", 0),
                    "totalBuyQuantity": marketDeptOrderBook.get("totalBuyQuantity", 0),
                    "totalSellQuantity": marketDeptOrderBook.get("totalSellQuantity", 0),
                    "OI": trade_info.get("openInterest", 0),
                    "Chng in OI": trade_info.get("changeinOpenInterest", 0),
                    "% Chng in OI": trade_info.get("pchangeinOpenInterest", 0),
                    "VWAP": trade_info.get("vmap", 0)
                })
            
            return table_data
            
        except Exception as e:
            print(f"Error fetching Stock active contracts data: {str(e)}")
            return None
        

    def get_nifty_active_contracts(self, symbol: str, expiry_date: str = None):
        self.rotate_user_agent()
        
        ref_url = f'https://www.nseindia.com/get-quotes/derivatives?symbol={symbol}'
        ref = requests.get(ref_url, headers=self.headers)
        
        url = f"https://www.nseindia.com/api/quote-derivative?symbol={symbol}"
        
        try:
            payload = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10).json()
            
            if expiry_date:
                exp_date = pd.to_datetime(expiry_date, format='%d-%m-%Y')
                expiry_date = exp_date.strftime('%d-%b-%Y')
            
            # Filter only Stock Options data
            stocks_data = [
                stock for stock in payload.get("stocks", [])
                if stock["metadata"]["instrumentType"] == "Index Options"
            ]
            
            # If expiry_date is specified, filter by expiry date as well
            if expiry_date:
                stocks_data = [
                    stock for stock in stocks_data
                    if stock["metadata"]["expiryDate"] == expiry_date
                ]
            
            # Prepare table data
            table_data = []
            for stock in stocks_data:
                metadata = stock["metadata"]
                marketDeptOrderBook = stock["marketDeptOrderBook"]
                trade_info = stock["marketDeptOrderBook"]["tradeInfo"]
                table_data.append({
                    "Instrument Type": metadata["instrumentType"],
                    "Expiry Date": metadata["expiryDate"],
                    "Option Type": metadata["optionType"],
                    "Strike Price": metadata["strikePrice"],
                    "Open": metadata.get("openPrice", 0),
                    "High": metadata.get("highPrice", 0),
                    "Low": metadata.get("lowPrice", 0),
                    "closePrice":metadata.get("closePrice", 0),
                    "Prev Close": metadata.get("prevClose", 0),
                    "Last": metadata.get("lastPrice", 0),
                    "Change": metadata.get("change", 0),
                    "%Change": metadata.get("pChange", 0),
                    "Volume (Contracts)": metadata.get("numberOfContractsTraded", 0),
                    "Value (₹ Lakhs)": metadata.get("totalTurnover", 0),
                    "totalBuyQuantity": marketDeptOrderBook.get("totalBuyQuantity", 0),
                    "totalSellQuantity": marketDeptOrderBook.get("totalSellQuantity", 0),
                    "OI": trade_info.get("openInterest", 0),
                    "Chng in OI": trade_info.get("changeinOpenInterest", 0),
                    "% Chng in OI": trade_info.get("pchangeinOpenInterest", 0),
                    "VWAP": trade_info.get("vmap", 0)
                })
            
            return table_data
            
        except Exception as e:
            print(f"Error fetching nifty active contracts data: {str(e)}")
            return None

    def current_ipo(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/market-data/all-upcoming-issues-ipo'
        api_url = 'https://www.nseindia.com/api/ipo-current-issue'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()

            if isinstance(data, list):
                # Create DataFrame from the JSON data
                df = pd.DataFrame(data)

                # Define columns to match the JSON structure
                columns = ['symbol', 'companyName', 'series', 'issueStartDate', 'issueEndDate', 'status', 
                           'issueSize', 'issuePrice', 'noOfSharesOffered', 'noOfsharesBid', 'noOfTime']
                
                # Ensure DataFrame has the correct columns
                df = df[columns]

                # Fix NaN values to avoid issues
                df = df.fillna(0)  # Replace NaN with 0
                df = df.replace({float('inf'): 0, float('-inf'): 0})  # Replace infinite values with 0

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if no data is found

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching IPO data: {e}")
            return None
        
    def ipo_preopen(self):
        self.rotate_user_agent()  # Rotating User-Agent

        ref_url = 'https://www.nseindia.com/market-data/new-stock-exchange-listings-today'
        api_url = 'https://www.nseindia.com/api/special-preopen-listing'

        try:
            # Get reference cookies from the main page
            ref_response = self.session.get(ref_url, headers=self.headers, timeout=10)
            ref_response.raise_for_status()  # Ensure request was successful

            # Make API call using cookies from the previous request
            response = self.session.get(api_url, headers=self.headers, cookies=ref_response.cookies.get_dict(), timeout=10)
            response.raise_for_status()  # Ensure request was successful

            # Convert response to JSON
            data = response.json()

            if 'data' in data and isinstance(data['data'], list):
                # Create a list to store flattened data
                flattened_data = []
                
                for item in data['data']:
                    # Extract preopenBook fields
                    preopen_book = item.get('preopenBook', {})
                    preopen = preopen_book.get('preopen', [{}])[0] if preopen_book.get('preopen') else {}
                    ato = preopen_book.get('ato', {})

                    # Flatten the data into a single dictionary
                    flattened_item = {
                        'symbol': item.get('symbol', ''),
                        'series': item.get('series', ''),
                        'prevClose': item.get('prevClose', ''),
                        'iep': item.get('iep', ''),
                        'change': item.get('change', ''),
                        'perChange': item.get('perChange', ''),
                        'ieq': item.get('ieq', ''),
                        'ieVal': item.get('ieVal', ''),
                        'buyOrderCancCnt': item.get('buyOrderCancCnt', ''),
                        'buyOrderCancVol': item.get('buyOrderCancVol', ''),
                        'sellOrderCancCnt': item.get('sellOrderCancCnt', ''),
                        'sellOrderCancVol': item.get('sellOrderCancVol', ''),
                        'isin': item.get('isin', ''),
                        'status': item.get('status', ''),
                        # New fields from preopenBook
                        'preopen_buyQty': preopen.get('buyQty', 0),
                        'preopen_sellQty': preopen.get('sellQty', 0),
                        'ato_totalBuyQuantity': ato.get('totalBuyQuantity', 0),
                        'ato_totalSellQuantity': ato.get('totalSellQuantity', 0),
                        'totalBuyQuantity': preopen_book.get('totalBuyQuantity', 0),
                        'totalSellQuantity': preopen_book.get('totalSellQuantity', 0),
                        'totTradedQty': preopen_book.get('totTradedQty', 0),
                        'lastUpdateTime': preopen_book.get('lastUpdateTime', '')
                    }
                    flattened_data.append(flattened_item)

                # Create DataFrame from the flattened data
                df = pd.DataFrame(flattened_data)

                # Fix NaN values to avoid issues
                df = df.fillna(0)  # Replace NaN with 0
                df = df.replace({float('inf'): 0, float('-inf'): 0})  # Replace infinite values with 0

                return df if not df.empty else None  # Return DataFrame if not empty
            return None  # Return None if no data is found

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Special Pre-Open data: {e}")
            return None

    def get_press_releases(self, from_date_str: str = None, to_date_str: str = None, filter: str = None):
        self.rotate_user_agent()

        # Default date range (yesterday to today if not provided)
        try:
            if from_date_str is None:
                from_date = datetime.now() - timedelta(days=1)
                from_date_str = from_date.strftime("%d-%m-%Y")
            else:
                datetime.strptime(from_date_str, "%d-%m-%Y")  # Validate date format

            if to_date_str is None:
                to_date = datetime.now()
                to_date_str = to_date.strftime("%d-%m-%Y")
            else:
                datetime.strptime(to_date_str, "%d-%m-%Y")  # Validate date format
        except ValueError as e:
            print(f"Invalid date format: {e}")
            return pd.DataFrame(columns=["DATE", "DEPARTMENT", "SUBJECT", "ATTACHMENT URL", "LAST UPDATED"])

        # Reference URL for cookies
        ref_url = 'https://www.nseindia.com/resources/exchange-communication-press-releases'
        try:
            ref = requests.get(ref_url, headers=self.headers, timeout=10)
            ref.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch reference URL: {e}")
            return pd.DataFrame(columns=["DATE", "DEPARTMENT", "SUBJECT", "ATTACHMENT URL", "LAST UPDATED"])

        try:
            # API URL for press releases
            url = f"https://www.nseindia.com/api/press-release-cms20?fromDate={from_date_str}&toDate={to_date_str}"
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()
            json_data = response.json()

            # Handle case when response is not a list
            if not isinstance(json_data, list):
                print("No press releases found")
                return pd.DataFrame(columns=["DATE", "DEPARTMENT", "SUBJECT", "ATTACHMENT URL", "LAST UPDATED"])

            press_releases = []
            for item in json_data:
                if not isinstance(item, dict) or 'content' not in item:
                    continue  # Skip invalid items

                content = item['content']

                # Clean HTML from subject
                subject_raw = content.get('body', '')
                subject_clean = subject_raw  # Default to raw text as fallback
                if subject_raw and isinstance(subject_raw, str):
                    # Check if content resembles HTML (basic heuristic)
                    if '<' in subject_raw and '>' in subject_raw:
                        try:
                            with warnings.catch_warnings():
                                warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
                                soup = BeautifulSoup(subject_raw, "html.parser")
                                subject_clean = soup.get_text(separator=' ').strip()
                        except Exception as e:
                            print(f"Failed to parse HTML for subject: {e}")
                    else:
                        # Treat as plain text and strip whitespace
                        subject_clean = subject_raw.strip()

                # Format 'changed' field
                changed_raw = item.get('changed', '')
                try:
                    last_updated_ts = datetime.strptime(changed_raw, "%a, %m/%d/%Y - %H:%M")
                    last_updated_str = last_updated_ts.strftime("%a %d-%b-%Y %I:%M %p")
                except ValueError:
                    last_updated_str = changed_raw  # Fallback to raw string

                press_releases.append({
                    "date": content.get('field_date', ''),
                    "subject": subject_clean,
                    "department": content.get('field_type', ''),
                    "attachment_url": content.get('field_file_attachement', {}).get('url') if content.get('field_file_attachement') else None,
                    "changed": last_updated_str
                })

            if not press_releases:
                print("No press releases data available")
                return pd.DataFrame(columns=["DATE", "DEPARTMENT", "SUBJECT", "ATTACHMENT URL", "LAST UPDATED"])

            # Create DataFrame
            df = pd.DataFrame(press_releases)

            # Apply filtering
            if filter is not None:
                df = df[df['department'].str.contains(filter, case=False, na=False)]

            # Rename and reorder columns
            column_mapping = {
                "date": "DATE",
                "subject": "SUBJECT",
                "department": "DEPARTMENT",
                "attachment_url": "ATTACHMENT URL",
                "changed": "LAST UPDATED"
            }
            df = df.rename(columns=column_mapping)
            df = df[["DATE", "DEPARTMENT", "SUBJECT", "ATTACHMENT URL", "LAST UPDATED"]]

            print(f"Final number of records in DataFrame: {len(df)}")
            return df

        except (requests.RequestException, ValueError, TypeError) as e:
            print(f"Error fetching press releases: {e}")
            return pd.DataFrame(columns=["DATE", "DEPARTMENT", "SUBJECT", "ATTACHMENT URL", "LAST UPDATED"])

    def get_nse_circulars(self, from_date_str: str = None, to_date_str: str = None, filter: str = None):
        self.rotate_user_agent()

        # Default date range (yesterday to today if not provided)
        if from_date_str is None:
            from_date = datetime.now() - timedelta(days=1)
            from_date_str = from_date.strftime("%d-%m-%Y")
        if to_date_str is None:
            to_date = datetime.now()
            to_date_str = to_date.strftime("%d-%m-%Y")

        # Reference URL for cookies
        ref_url = 'https://www.nseindia.com/resources/exchange-communication-circulars'
        try:
            ref = requests.get(ref_url, headers=self.headers)
        except requests.RequestException as e:
            print(f"Failed to get reference cookies: {str(e)}")
            return pd.DataFrame(columns=["Date", "Circulars No", "Category", "Department", "Subject", "Attachment"])

        try:
            # API URL for circulars
            url = f"https://www.nseindia.com/api/circulars?&fromDate={from_date_str}&toDate={to_date_str}"
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()
            json_data = response.json().get("data", [])

            # Handle empty or unexpected data
            if not isinstance(json_data, list) or not json_data:
                # print("❌ No NSE Circular data available")
                return pd.DataFrame(columns=["Date", "Circulars No", "Category", "Department", "Subject", "Attachment"])

            circulars = []
            for item in json_data:
                circulars.append({
                    "date": item.get("cirDisplayDate", ''),
                    "circulars": item.get("circDisplayNo", ''),
                    "category": item.get("circCategory", ''),
                    "department": item.get("circDepartment", ''),
                    "subject": item.get("sub", ''),
                    "attachment": item.get("circFilelink", ''),
                })

            # Create DataFrame
            df = pd.DataFrame(circulars)

            # Apply filtering
            if filter is not None:
                df = df[df['department'].str.contains(filter, case=False, na=False)]

            # Rename and reorder columns
            column_mapping = {
                "date": "Date",
                "circulars": "Circulars No",
                "category": "Category",
                "department": "Department",
                "subject": "Subject",
                "attachment": "Attachment",
            }
            df = df.rename(columns=column_mapping)
            df = df[["Date", "Circulars No", "Category", "Department", "Subject", "Attachment"]]

            print(f"Final number of records in DataFrame: {len(df)}")
            return df

        except (requests.RequestException, ValueError, TypeError) as e:
            # print("No circulars available")
            return pd.DataFrame(columns=["Date", "Circulars No", "Category", "Department", "Subject", "Attachment"])
