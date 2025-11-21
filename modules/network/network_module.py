import logging
import requests
import time
import os
from core.event_manager import EventManager, EventType
from typing import Dict, Any, Optional, Callable
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
from modules.base_module import BaseModule

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_IMG_DIR = os.path.join(PROJECT_ROOT, "assets", "img")

class NetworkModule(BaseModule):

    def __init__(self, config):
        super().__init__(config)
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.lock = Lock()

        self._last_mmr_update = 0
        self._mmr_future: Optional[Future] = None
        self._mmr_result_cache = None
    
    def get_name(self) -> str:
        return "network"
    
    def initialize(self):
        logger.info("Initializing network module")
        
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            max_retries=self.config.MAX_RETRIES
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        if self.config.USE_THREAD_POOL:
            self.executor = ThreadPoolExecutor(
                max_workers=self.config.MAX_WORKERS
            )
        
        self._initialized = True
        logger.info("Network module initialized")
    
    def update(self):
        now = time.time()
        interval = getattr(self.config, "VALORANT_UPDATE_INTERVAL", 86400)
        enabled = getattr(self.config, "VALORANT_ENABLED", False)
        if enabled and (now - self._last_mmr_update >= interval) and self._mmr_future is None:
            region = self.config.VALORANT_REGION
            platform = self.config.VALORANT_PLATFORM
            username = self.config.VALORANT_USERNAME
            tag = self.config.VALORANT_TAG
            api_key = self.config.VALORANT_API_KEY

            # Launch in background thread
            self._mmr_future = self.executor.submit(
                self.fetch_valorant_mmr, region, platform, username, tag, api_key
            )
            self._last_mmr_update = now

        # Check if background fetch completed
        if self._mmr_future is not None and self._mmr_future.done():
            result = self._mmr_future.result()
            if result:
                # Parse and handle result in main thread
                parsed = self.parse_valorant_mmr_data(result)
                self.handle_valorant_mmr(parsed)
                self._mmr_result_cache = parsed  # Optional: cache for quick access elsewhere
            self._mmr_future = None  # Allow next fetch in future
    
    
    def request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        try:
            kwargs.setdefault('timeout', self.config.TIMEOUT)
            
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            return None
    
    def request_async(self, method: str, url: str, 
                     callback: Optional[Callable] = None, **kwargs):
        def _request_worker():
            data = self.request(method, url, **kwargs)
            if callback:
                callback(data)
        
        if self.executor:
            self.executor.submit(_request_worker)
        else:
            thread = Thread(target=_request_worker, daemon=True)
            thread.start()
    
    
    def get(self, url: str, **kwargs) -> Optional[Dict]:
        return self.request('GET', url, **kwargs)
    
    def get_async(self, url: str, callback: Optional[Callable] = None, **kwargs):
        self.request_async('GET', url, callback=callback, **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[Dict]:
        return self.request('POST', url, **kwargs)
    
    def post_async(self, url: str, callback: Optional[Callable] = None, **kwargs):
        self.request_async('POST', url, callback=callback, **kwargs)
    
    def put(self, url: str, **kwargs) -> Optional[Dict]:
        return self.request('PUT', url, **kwargs)
    
    def put_async(self, url: str, callback: Optional[Callable] = None, **kwargs):
        self.request_async('PUT', url, callback=callback, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Optional[Dict]:
        return self.request('DELETE', url, **kwargs)
    
    def delete_async(self, url: str, callback: Optional[Callable] = None, **kwargs):
        self.request_async('DELETE', url, callback=callback, **kwargs)
    
    def patch(self, url: str, **kwargs) -> Optional[Dict]:
        return self.request('PATCH', url, **kwargs)
    
    def patch_async(self, url: str, callback: Optional[Callable] = None, **kwargs):
        self.request_async('PATCH', url, callback=callback, **kwargs)
    
    def set_header(self, key: str, value: str):
        self.session.headers[key] = value
    
    def set_headers(self, headers: Dict[str, str]):
        self.session.headers.update(headers)
    
    def clear_headers(self):
        self.session.headers.clear()

    def fetch_valorant_mmr(self, region, platform, username, tag, api_key):
        url = f"https://api.henrikdev.xyz/valorant/v3/mmr/{region}/{platform}/{username}/{tag}"
        headers = {"Authorization": api_key}
        response = self.get(url, headers=headers)
        if not response or response.get("status") != 200:
            return None
        return response["data"]

    def parse_valorant_mmr_data(self, mmr_data):
        account = mmr_data.get('account', {})
        current = mmr_data.get('current', {})
        tier = current.get('tier', {})
        rr = current.get('rr')
        last_change = current.get('last_change')
        elo = current.get('elo')

        username = account.get('name')
        tag = account.get('tag')
        tier_id = tier.get('id')
        tier_name = tier.get('name', 'Unrated')

        summary = {
            "user": f"{username}#{tag}",
            "rank": tier_name,
            "rr": rr,
            "last_change": last_change,
            "elo": elo
        }

        logger.info(summary)

        return summary
    
    def handle_valorant_mmr(self, parsed):
        logger.info(
            f"Valorant rank for {parsed['user']}: {parsed['rank']} ({parsed['rr']} RR, ELO: {parsed['elo']}, Δ: {parsed['last_change']})"
        )
        if self.event_manager:
            image_rel_path = "asc_3.png"
            image_path = os.path.join("assets", "img", image_rel_path)
            self.event_manager.emit(
                EventType.DISPLAY_VALORANT_INFO,
                data={
                    'account_info': parsed,
                    'rank_icon': image_path,
                    'duration': 5.0
                },
                source='network'
            )

    
    def shutdown(self):
        logger.info("Shutting down network module")
        
        if self.executor:
            self.executor.shutdown(wait=True)
        
        if self.session:
            self.session.close()
        
        logger.info("Network module shut down")
