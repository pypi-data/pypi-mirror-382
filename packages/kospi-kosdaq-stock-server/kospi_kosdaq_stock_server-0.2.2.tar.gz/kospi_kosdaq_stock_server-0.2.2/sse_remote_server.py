"""
SSE (Server-Sent Events) Remote Server for KOSPI-KOSDAQ MCP
This server wraps the MCP server functionality and exposes it via SSE endpoints
"""

import json
import logging
import asyncio
from typing import Dict, Any, Union, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import uuid
import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import pykrx directly instead of from MCP server
try:
    from pykrx import stock
except ImportError:
    import subprocess
    import sys
    print("Installing pykrx...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pykrx"])
    from pykrx import stock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variable to store ticker information in memory
TICKER_MAP: Dict[str, str] = {}

# Store active SSE connections
active_connections: Dict[str, asyncio.Queue] = {}

# Pydantic models for request/response
class LoadTickersRequest(BaseModel):
    """Request model for loading tickers"""
    refresh: bool = Field(default=False, description="Force refresh ticker data")

class StockDataRequest(BaseModel):
    """Request model for stock data retrieval"""
    fromdate: Union[str, int] = Field(..., description="Start date (YYYYMMDD)")
    todate: Union[str, int] = Field(..., description="End date (YYYYMMDD)")
    ticker: Union[str, int] = Field(..., description="Stock ticker symbol")
    adjusted: Optional[bool] = Field(default=True, description="Use adjusted prices")

class SSEMessage(BaseModel):
    """SSE message format"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event: str
    data: Any
    retry: Optional[int] = None

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle"""
    logger.info("Starting SSE Remote Server for KOSPI-KOSDAQ MCP")
    # Load tickers on startup
    try:
        await load_tickers_async()
        logger.info(f"Loaded {len(TICKER_MAP)} tickers on startup")
    except Exception as e:
        logger.error(f"Failed to load tickers on startup: {e}")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down SSE Remote Server")
    # Close all active connections
    for connection_id in list(active_connections.keys()):
        queue = active_connections.pop(connection_id)
        await queue.put(None)  # Signal to close

# Create FastAPI app
app = FastAPI(
    title="KOSPI-KOSDAQ SSE Remote Server",
    description="Server-Sent Events API for Korean stock market data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def validate_date(date_str: Union[str, int]) -> str:
    """Validate and convert date format"""
    try:
        if isinstance(date_str, int):
            date_str = str(date_str)
        if '-' in date_str:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
            return parsed_date.strftime('%Y%m%d')
        datetime.strptime(date_str, '%Y%m%d')
        return date_str
    except ValueError:
        raise ValueError(f"Date must be in YYYYMMDD format. Input value: {date_str}")

def validate_ticker(ticker_str: Union[str, int]) -> str:
    """Validate ticker format"""
    if isinstance(ticker_str, int):
        ticker_str = str(ticker_str)
    # Ensure ticker is 6 digits with leading zeros
    ticker_str = ticker_str.zfill(6)
    return ticker_str

async def load_tickers_async() -> Dict[str, str]:
    """Asynchronously load all ticker symbols and names"""
    global TICKER_MAP
    
    if TICKER_MAP:
        return TICKER_MAP
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _load_tickers_sync)
    TICKER_MAP.update(result)
    return TICKER_MAP

def _load_tickers_sync() -> Dict[str, str]:
    """Synchronously load tickers (called in executor)"""
    try:
        # Get today's date or nearest business day
        today = datetime.now().strftime('%Y%m%d')
        
        # Get KOSPI tickers
        kospi_tickers = stock.get_market_ticker_list(today, market="KOSPI")
        # Get KOSDAQ tickers
        kosdaq_tickers = stock.get_market_ticker_list(today, market="KOSDAQ")
        
        ticker_map = {}
        
        # Get names for KOSPI stocks
        for ticker in kospi_tickers:
            try:
                name = stock.get_market_ticker_name(ticker)
                ticker_map[ticker] = name
            except Exception as e:
                logger.warning(f"Failed to get name for ticker {ticker}: {e}")
                ticker_map[ticker] = ticker
        
        # Get names for KOSDAQ stocks
        for ticker in kosdaq_tickers:
            try:
                name = stock.get_market_ticker_name(ticker)
                ticker_map[ticker] = name
            except Exception as e:
                logger.warning(f"Failed to get name for ticker {ticker}: {e}")
                ticker_map[ticker] = ticker
        
        return ticker_map
    except Exception as e:
        logger.error(f"Failed to load tickers: {e}")
        raise

async def send_sse_message(queue: asyncio.Queue, message: SSEMessage):
    """Send SSE message to queue"""
    await queue.put(message)

async def sse_generator(connection_id: str, request: Request):
    """Generate SSE stream"""
    queue = asyncio.Queue()
    active_connections[connection_id] = queue
    
    try:
        # Send initial connection message
        yield f"event: connected\ndata: {json.dumps({'connection_id': connection_id})}\n\n"
        
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
                
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                
                if message is None:  # Shutdown signal
                    break
                    
                # Format SSE message
                sse_data = f"id: {message.id}\n"
                sse_data += f"event: {message.event}\n"
                sse_data += f"data: {json.dumps(message.data)}\n"
                if message.retry:
                    sse_data += f"retry: {message.retry}\n"
                sse_data += "\n"
                
                yield sse_data
                
            except asyncio.TimeoutError:
                # Send heartbeat
                yield f"event: heartbeat\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"
                
    except Exception as e:
        logger.error(f"SSE generator error: {e}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        
    finally:
        # Clean up connection
        if connection_id in active_connections:
            del active_connections[connection_id]

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "KOSPI-KOSDAQ SSE Remote Server",
        "version": "1.0.0",
        "endpoints": {
            "sse": "/sse/connect",
            "tickers": {
                "load": "/api/tickers/load",
                "list": "/api/tickers/list",
                "search": "/api/tickers/search"
            },
            "stock_data": {
                "ohlcv": "/api/stock/ohlcv",
                "market_cap": "/api/stock/market_cap",
                "fundamental": "/api/stock/fundamental",
                "trading_volume": "/api/stock/trading_volume"
            }
        },
        "active_connections": len(active_connections)
    }

@app.get("/sse/connect")
async def sse_connect(request: Request):
    """Establish SSE connection"""
    connection_id = str(uuid.uuid4())
    logger.info(f"New SSE connection: {connection_id}")
    
    return StreamingResponse(
        sse_generator(connection_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

@app.post("/api/tickers/load")
async def load_tickers(request: LoadTickersRequest):
    """Load or refresh ticker data"""
    global TICKER_MAP
    
    try:
        if request.refresh:
            TICKER_MAP = {}
        
        tickers = await load_tickers_async()
        
        # Send update to all SSE connections
        message = SSEMessage(
            event="tickers_loaded",
            data={"count": len(tickers), "refresh": request.refresh}
        )
        
        for queue in active_connections.values():
            await send_sse_message(queue, message)
        
        return {
            "success": True,
            "count": len(tickers),
            "message": f"Loaded {len(tickers)} tickers"
        }
        
    except Exception as e:
        logger.error(f"Failed to load tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tickers/list")
async def list_tickers(limit: int = 100, offset: int = 0):
    """List all loaded tickers with pagination"""
    if not TICKER_MAP:
        return {
            "tickers": [],
            "total": 0,
            "message": "No tickers loaded. Please load tickers first."
        }
    
    ticker_list = list(TICKER_MAP.items())
    paginated = ticker_list[offset:offset + limit]
    
    return {
        "tickers": [{"ticker": t, "name": n} for t, n in paginated],
        "total": len(TICKER_MAP),
        "limit": limit,
        "offset": offset
    }

@app.get("/api/tickers/search")
async def search_tickers(query: str):
    """Search tickers by name or code"""
    if not TICKER_MAP:
        return {
            "results": [],
            "message": "No tickers loaded. Please load tickers first."
        }
    
    query_lower = query.lower()
    results = []
    
    for ticker, name in TICKER_MAP.items():
        if query_lower in ticker.lower() or query_lower in name.lower():
            results.append({"ticker": ticker, "name": name})
    
    return {
        "results": results[:50],  # Limit to 50 results
        "count": len(results),
        "query": query
    }

@app.post("/api/stock/ohlcv")
async def get_stock_ohlcv_endpoint(request: StockDataRequest):
    """Get OHLCV data via SSE"""
    try:
        fromdate = validate_date(request.fromdate)
        todate = validate_date(request.todate)
        ticker = validate_ticker(request.ticker)
        
        logger.info(f"Getting OHLCV data for {ticker} from {fromdate} to {todate}")
        
        # Send processing message to SSE connections
        processing_msg = SSEMessage(
            event="processing",
            data={
                "type": "ohlcv",
                "ticker": ticker,
                "fromdate": fromdate,
                "todate": todate
            }
        )
        
        for queue in active_connections.values():
            await send_sse_message(queue, processing_msg)
        
        # Get data in executor using lambda
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(
            None, 
            lambda: stock.get_market_ohlcv_by_date(
                fromdate, 
                todate, 
                ticker,
                'd',  # frequency: 'd' for daily
                request.adjusted  # adjusted parameter
            )
        )
        
        # Check if dataframe is empty
        if df is None or df.empty:
            logger.warning(f"No data found for ticker {ticker}")
            return {
                "success": False,
                "ticker": ticker,
                "fromdate": fromdate,
                "todate": todate,
                "data": {},
                "message": "No data found for the specified period"
            }
        
        # Convert to dict
        result = df.to_dict(orient='index')
        sorted_items = sorted(
            ((k.strftime('%Y-%m-%d'), v) for k, v in result.items()),
            reverse=True
        )
        result = dict(sorted_items)
        
        # Send result to SSE connections
        result_msg = SSEMessage(
            event="stock_data",
            data={
                "type": "ohlcv",
                "ticker": ticker,
                "data": result
            }
        )
        
        for queue in active_connections.values():
            await send_sse_message(queue, result_msg)
        
        return {
            "success": True,
            "ticker": ticker,
            "fromdate": fromdate,
            "todate": todate,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting OHLCV data: {str(e)}\n{traceback.format_exc()}")
        
        error_msg = SSEMessage(
            event="error",
            data={"type": "ohlcv", "error": str(e)}
        )
        
        for queue in active_connections.values():
            await send_sse_message(queue, error_msg)
        
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stock/market_cap")
async def get_stock_market_cap_endpoint(request: StockDataRequest):
    """Get market cap data"""
    try:
        fromdate = validate_date(request.fromdate)
        todate = validate_date(request.todate)
        ticker = validate_ticker(request.ticker)
        
        logger.info(f"Getting market cap data for {ticker} from {fromdate} to {todate}")
        
        # Get data in executor using lambda
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(
            None,
            lambda: stock.get_market_cap_by_date(
                fromdate,
                todate,
                ticker,
                'd'  # frequency: 'd' for daily
            )
        )
        
        # Check if dataframe is empty
        if df is None or df.empty:
            return {
                "success": False,
                "ticker": ticker,
                "data": {},
                "message": "No data found for the specified period"
            }
        
        # Convert to dict
        result = df.to_dict(orient='index')
        sorted_items = sorted(
            ((k.strftime('%Y-%m-%d'), v) for k, v in result.items()),
            reverse=True
        )
        result = dict(sorted_items)
        
        # Send result to SSE connections
        result_msg = SSEMessage(
            event="stock_data",
            data={
                "type": "market_cap",
                "ticker": ticker,
                "data": result
            }
        )
        
        for queue in active_connections.values():
            await send_sse_message(queue, result_msg)
        
        return {
            "success": True,
            "ticker": ticker,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting market cap data: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stock/fundamental")
async def get_stock_fundamental_endpoint(request: StockDataRequest):
    """Get fundamental data"""
    try:
        fromdate = validate_date(request.fromdate)
        todate = validate_date(request.todate)
        ticker = validate_ticker(request.ticker)
        
        logger.info(f"Getting fundamental data for {ticker} from {fromdate} to {todate}")
        
        # Get data in executor using lambda
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(
            None,
            lambda: stock.get_market_fundamental_by_date(
                fromdate,
                todate,
                ticker,
                'd'  # frequency: 'd' for daily
            )
        )
        
        # Check if dataframe is empty
        if df is None or df.empty:
            return {
                "success": False,
                "ticker": ticker,
                "data": {},
                "message": "No data found for the specified period"
            }
        
        # Convert to dict
        result = df.to_dict(orient='index')
        sorted_items = sorted(
            ((k.strftime('%Y-%m-%d'), v) for k, v in result.items()),
            reverse=True
        )
        result = dict(sorted_items)
        
        # Send result to SSE connections
        result_msg = SSEMessage(
            event="stock_data",
            data={
                "type": "fundamental",
                "ticker": ticker,
                "data": result
            }
        )
        
        for queue in active_connections.values():
            await send_sse_message(queue, result_msg)
        
        return {
            "success": True,
            "ticker": ticker,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting fundamental data: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stock/trading_volume")
async def get_stock_trading_volume_endpoint(request: StockDataRequest):
    """Get trading volume by investor type"""
    try:
        fromdate = validate_date(request.fromdate)
        todate = validate_date(request.todate)
        ticker = validate_ticker(request.ticker)
        
        logger.info(f"Getting trading volume data for {ticker} from {fromdate} to {todate}")
        
        # Get data in executor using lambda
        loop = asyncio.get_event_loop()
        
        # get_market_trading_volume_by_date doesn't have freq parameter
        # but has detail parameter
        df = await loop.run_in_executor(
            None,
            lambda: stock.get_market_trading_volume_by_date(
                fromdate,
                todate,
                ticker,
                detail=True  # Get detailed data by investor type
            )
        )
        
        # Check if dataframe is empty
        if df is None or df.empty:
            return {
                "success": False,
                "ticker": ticker,
                "data": {},
                "message": "No data found for the specified period"
            }
        
        # Convert to dict
        result = df.to_dict(orient='index')
        sorted_items = sorted(
            ((k.strftime('%Y-%m-%d'), v) for k, v in result.items()),
            reverse=True
        )
        result = dict(sorted_items)
        
        # Send result to SSE connections
        result_msg = SSEMessage(
            event="stock_data",
            data={
                "type": "trading_volume",
                "ticker": ticker,
                "data": result
            }
        )
        
        for queue in active_connections.values():
            await send_sse_message(queue, result_msg)
        
        return {
            "success": True,
            "ticker": ticker,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting trading volume data: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tickers_loaded": len(TICKER_MAP),
        "active_connections": len(active_connections)
    }

# WebSocket alternative (optional)
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint as an alternative to SSE"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    logger.info(f"New WebSocket connection: {connection_id}")
    
    try:
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
            elif data.get("type") == "load_tickers":
                tickers = await load_tickers_async()
                await websocket.send_json({
                    "type": "tickers_loaded",
                    "count": len(tickers)
                })
                
            elif data.get("type") == "get_ohlcv":
                # Process OHLCV request
                request_data = data.get("data", {})
                fromdate = validate_date(request_data.get("fromdate"))
                todate = validate_date(request_data.get("todate"))
                ticker = validate_ticker(request_data.get("ticker"))
                adjusted = request_data.get("adjusted", True)
                
                loop = asyncio.get_event_loop()
                df = await loop.run_in_executor(
                    None,
                    lambda: stock.get_market_ohlcv_by_date(
                        fromdate,
                        todate,
                        ticker,
                        'd',  # frequency
                        adjusted
                    )
                )
                
                if df is not None and not df.empty:
                    result = df.to_dict(orient='index')
                    sorted_items = sorted(
                        ((k.strftime('%Y-%m-%d'), v) for k, v in result.items()),
                        reverse=True
                    )
                    result = dict(sorted_items)
                else:
                    result = {}
                
                await websocket.send_json({
                    "type": "ohlcv_data",
                    "ticker": ticker,
                    "data": result
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "sse_remote_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
