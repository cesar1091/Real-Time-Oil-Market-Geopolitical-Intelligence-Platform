import pandas as pd
from scrapping.oil_prices_scraper import fetch_oil_prices

def test_fetch_oil_prices(mocker):
    # Mock yfinance download function
    mock_data = pd.DataFrame({
        ('Open', 'CL=F'): [70.0, 71.0],
        ('High', 'CL=F'): [72.0, 73.0],
        ('Low', 'CL=F'): [69.0, 70.5],
        ('Close', 'CL=F'): [71.5, 72.5],
        ('Volume', 'CL=F'): [100000, 150000],
        ('Open', 'BZ=F'): [65.0, 66.0],
        ('High', 'BZ=F'): [67.0, 68.0],
        ('Low', 'BZ=F'): [64.0, 65.5],
        ('Close', 'BZ=F'): [66.5, 67.5],
        ('Volume', 'BZ=F'): [80000, 120000],
        ('Open', 'NG=F'): [3.0, 3.1],
        ('High', 'NG=F'): [3.2, 3.3],
        ('Low', 'NG=F'): [2.9, 3.0],
        ('Close', 'NG=F'): [3.1, 3.2],
        ('Volume', 'NG=F'): [50000, 70000]
    }, index=pd.to_datetime(['2024-06-01 10:00:00', '2024-06-01 11:00:00']))

    mocker.patch('scrapping.oil_prices_scraper.yf.download', return_value=mock_data)

    oil_prices = fetch_oil_prices()
    
    assert len(oil_prices) == 6
    assert oil_prices[0]['ticker'] == 'CL=F'
    assert oil_prices[0]['datetime'] == '2024-06-01T10:00:00'
    assert oil_prices[0]['open'] == 70.0
    assert oil_prices[0]['high'] == 72.0
    assert oil_prices[0]['low'] == 69.0
    assert oil_prices[0]['close'] == 71.5
    assert oil_prices[0]['volume'] == 100000

def test_fetch_oil_prices_empty(mocker):
    mock_data = pd.DataFrame()
    mocker.patch('scrapping.oil_prices_scraper.yf.download', return_value=mock_data)

    oil_prices = fetch_oil_prices()
    
    assert oil_prices == []
    assert len(oil_prices) == 0

def test_fetch_oil_prices_exception(mocker):
    mocker.patch('scrapping.oil_prices_scraper.yf.download', side_effect=Exception("API error"))

    oil_prices = fetch_oil_prices()
    
    assert oil_prices == []
    assert len(oil_prices) == 0

