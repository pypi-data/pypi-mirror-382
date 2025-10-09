"""
SSE Client Example for KOSPI-KOSDAQ Remote Server
This demonstrates how to connect and interact with the SSE server
"""

import json
import asyncio
import aiohttp
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSEClient:
    """SSE Client for KOSPI-KOSDAQ Remote Server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.sse_connection = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def connect_sse(self):
        """Connect to SSE endpoint and listen for events"""
        url = f"{self.base_url}/sse/connect"
        
        async with self.session.get(url) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                
                if line.startswith('event:'):
                    event = line.split(':', 1)[1].strip()
                    
                elif line.startswith('data:'):
                    data = line.split(':', 1)[1].strip()
                    try:
                        data = json.loads(data)
                        await self.handle_sse_event(event, data)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse SSE data: {data}")
                        
    async def handle_sse_event(self, event: str, data: dict):
        """Handle SSE events"""
        logger.info(f"SSE Event: {event}")
        logger.info(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if event == "connected":
            logger.info(f"Connected with ID: {data.get('connection_id')}")
        elif event == "stock_data":
            data_type = data.get("type")
            ticker = data.get("ticker")
            logger.info(f"Received {data_type} data for ticker {ticker}")
        elif event == "error":
            logger.error(f"Error: {data.get('error')}")
            
    async def load_tickers(self, refresh: bool = False):
        """Load ticker data"""
        url = f"{self.base_url}/api/tickers/load"
        async with self.session.post(url, json={"refresh": refresh}) as response:
            result = await response.json()
            logger.info(f"Loaded {result.get('count')} tickers")
            return result
            
    async def search_tickers(self, query: str):
        """Search for tickers"""
        url = f"{self.base_url}/api/tickers/search"
        params = {"query": query}
        async with self.session.get(url, params=params) as response:
            result = await response.json()
            logger.info(f"Found {result.get('count')} results for '{query}'")
            return result
            
    async def get_ohlcv(self, ticker: str, fromdate: str, todate: str, adjusted: bool = True):
        """Get OHLCV data"""
        url = f"{self.base_url}/api/stock/ohlcv"
        data = {
            "ticker": ticker,
            "fromdate": fromdate,
            "todate": todate,
            "adjusted": adjusted
        }
        async with self.session.post(url, json=data) as response:
            result = await response.json()
            if result.get("success"):
                logger.info(f"Retrieved OHLCV data for {ticker}")
            return result
            
    async def get_market_cap(self, ticker: str, fromdate: str, todate: str):
        """Get market cap data"""
        url = f"{self.base_url}/api/stock/market_cap"
        data = {
            "ticker": ticker,
            "fromdate": fromdate,
            "todate": todate
        }
        async with self.session.post(url, json=data) as response:
            result = await response.json()
            if result.get("success"):
                logger.info(f"Retrieved market cap data for {ticker}")
            return result
            
    async def get_fundamental(self, ticker: str, fromdate: str, todate: str):
        """Get fundamental data"""
        url = f"{self.base_url}/api/stock/fundamental"
        data = {
            "ticker": ticker,
            "fromdate": fromdate,
            "todate": todate
        }
        async with self.session.post(url, json=data) as response:
            result = await response.json()
            if result.get("success"):
                logger.info(f"Retrieved fundamental data for {ticker}")
            return result
            
    async def get_trading_volume(self, ticker: str, fromdate: str, todate: str):
        """Get trading volume data"""
        url = f"{self.base_url}/api/stock/trading_volume"
        data = {
            "ticker": ticker,
            "fromdate": fromdate,
            "todate": todate
        }
        async with self.session.post(url, json=data) as response:
            result = await response.json()
            if result.get("success"):
                logger.info(f"Retrieved trading volume data for {ticker}")
            return result

async def main():
    """Example usage of SSE client"""
    
    # Create client
    async with SSEClient() as client:
        # Start SSE listener in background
        sse_task = asyncio.create_task(client.connect_sse())
        
        try:
            # Give SSE time to connect
            await asyncio.sleep(1)
            
            # Load tickers
            await client.load_tickers()
            await asyncio.sleep(1)
            
            # Search for Samsung
            search_result = await client.search_tickers("삼성전자")
            await asyncio.sleep(1)
            
            # Get OHLCV data for Samsung Electronics
            ohlcv = await client.get_ohlcv(
                ticker="005930",
                fromdate="20240101",
                todate="20240110"
            )
            
            # Get market cap
            market_cap = await client.get_market_cap(
                ticker="005930",
                fromdate="20240101",
                todate="20240110"
            )
            
            # Get fundamental data
            fundamental = await client.get_fundamental(
                ticker="005930",
                fromdate="20240101",
                todate="20240110"
            )
            
            # Get trading volume
            trading_volume = await client.get_trading_volume(
                ticker="005930",
                fromdate="20240101",
                todate="20240110"
            )
            
            # Keep listening for a bit more
            await asyncio.sleep(5)
            
        finally:
            # Cancel SSE listener
            sse_task.cancel()
            try:
                await sse_task
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    asyncio.run(main())
