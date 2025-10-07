#!/usr/bin/env python3
"""
바이비트 거래 모듈
공통 거래 로직을 패키지에서 제공
"""

import os
import requests
import hashlib
import hmac
import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

# 에러 처리 도구들
from ..utils.error_handler import ErrorHandler, retry_on_error
from ..utils.data_validator import DataValidator

logger = logging.getLogger(__name__)

class BybitTrader:
    """바이비트 거래 클래스"""
    
    def __init__(self, config_loader, test_mode: bool = True, telegram_notifier=None):
        self.config_loader = config_loader
        self.test_mode = test_mode
        self.api_key = None
        self.api_secret = None
        self.base_url = "https://api.bybit.com"
        
        # 에러 처리 도구들 초기화
        self.error_handler = ErrorHandler(telegram_notifier)
        self.data_validator = DataValidator()
        
        # 설정에서 API 키 로드
        self._load_api_keys()
    
    def _load_api_keys(self):
        """API 키 로드"""
        try:
            config = self.config_loader.load_config()
            api_keys = config.get('api_keys', {})
            self.api_key = api_keys.get('api_key')
            self.api_secret = api_keys.get('api_secret')
            
            if not self.test_mode and (not self.api_key or not self.api_secret):
                raise ValueError("바이비트 API 키가 설정되지 않았습니다")
                
        except Exception as e:
            logger.error(f"API 키 로드 실패: {e}")
            if not self.test_mode:
                raise
    
    def _generate_signature(self, params: str, timestamp: str) -> str:
        """API 서명 생성"""
        if not self.api_secret:
            return ""
        
        message = timestamp + self.api_key + "5000" + params
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self, params: str = "") -> Dict[str, str]:
        """API 헤더 생성"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(params, timestamp)
        
        return {
            'X-BAPI-API-KEY': self.api_key or '',
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '5000',
            'Content-Type': 'application/json'
        }
    
    @retry_on_error(context="잔고 조회")
    def get_account_balance(self) -> Dict[str, Any]:
        """계정 잔고 조회"""
        if self.test_mode:
            return self._get_mock_balance()
        
        try:
            url = f"{self.base_url}/v5/account/wallet-balance"
            params = "accountType=UNIFIED"
            headers = self._get_headers(params)
            
            response = requests.get(url, headers=headers, params={"accountType": "UNIFIED"})
            response.raise_for_status()
            
            data = response.json()
            
            # API 응답 검증
            validation_result = self.data_validator.validate_api_response(data, ['result'])
            if not validation_result.is_valid:
                self.error_handler.log_error(Exception(f"API 응답 검증 실패: {validation_result.errors}"), "잔고 조회")
                return {}
            
            result = data.get('result', {})
            
            # 잔고 데이터 검증
            balance_validation = self.data_validator.validate_balance_data(result)
            if not balance_validation.is_valid:
                self.error_handler.log_error(Exception(f"잔고 데이터 검증 실패: {balance_validation.errors}"), "잔고 조회")
                return {}
            
            return result
            
        except Exception as e:
            self.error_handler.log_error(e, "잔고 조회")
            return {}
    
    def _get_mock_balance(self) -> Dict[str, Any]:
        """모의 잔고 반환"""
        return {
            "list": [
                {
                    "accountType": "UNIFIED",
                    "accountId": "test_account",
                    "coin": [
                        {
                            "coin": "USDT",
                            "walletBalance": "10000.00000000",
                            "availableToWithdraw": "10000.00000000",
                            "availableToBorrow": "0.00000000"
                        },
                        {
                            "coin": "BTC",
                            "walletBalance": "0.00000000",
                            "availableToWithdraw": "0.00000000",
                            "availableToBorrow": "0.00000000"
                        }
                    ]
                }
            ]
        }
    
    @retry_on_error(context="주문 생성")
    def place_order(self, symbol: str, side: str, order_type: str, qty: str, 
                   price: Optional[str] = None, time_in_force: str = "GTC") -> Dict[str, Any]:
        """주문 생성"""
        if self.test_mode:
            return self._place_mock_order(symbol, side, order_type, qty, price)
        
        try:
            # 주문 데이터 검증
            order_data = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": qty,
                "timeInForce": time_in_force
            }
            
            if price and order_type == "Limit":
                order_data["price"] = price
            
            # 주문 데이터 유효성 검증
            validation_result = self.data_validator.validate_order_data(order_data)
            if not validation_result.is_valid:
                self.error_handler.log_error(Exception(f"주문 데이터 검증 실패: {validation_result.errors}"), "주문 생성")
                return {"retCode": -1, "retMsg": f"주문 데이터 검증 실패: {', '.join(validation_result.errors)}"}
            
            url = f"{self.base_url}/v5/order/create"
            params = json.dumps(order_data)
            headers = self._get_headers(params)
            
            response = requests.post(url, headers=headers, data=params)
            response.raise_for_status()
            
            result = response.json()
            
            # API 응답 검증
            api_validation = self.data_validator.validate_api_response(result, ['result'])
            if not api_validation.is_valid:
                self.error_handler.log_error(Exception(f"주문 API 응답 검증 실패: {api_validation.errors}"), "주문 생성")
                return {"retCode": -1, "retMsg": f"API 응답 검증 실패: {', '.join(api_validation.errors)}"}
            
            return result
            
        except Exception as e:
            self.error_handler.log_error(e, "주문 생성")
            return {"retCode": -1, "retMsg": str(e)}
    
    def _place_mock_order(self, symbol: str, side: str, order_type: str, 
                         qty: str, price: Optional[str] = None) -> Dict[str, Any]:
        """모의 주문 생성"""
        order_id = f"mock_{int(time.time() * 1000)}"
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "orderId": order_id,
                "orderLinkId": f"mock_link_{order_id}",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": qty,
                "price": price or "0",
                "timeInForce": "GTC",
                "orderStatus": "New",
                "createdTime": str(int(time.time() * 1000))
            }
        }
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """주문 상태 조회"""
        if self.test_mode:
            return self._get_mock_order_status(order_id)
        
        try:
            url = f"{self.base_url}/v5/order/realtime"
            params = f"category=linear&orderId={order_id}"
            headers = self._get_headers(params)
            
            response = requests.get(url, headers=headers, params={"category": "linear", "orderId": order_id})
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"주문 상태 조회 실패: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def _get_mock_order_status(self, order_id: str) -> Dict[str, Any]:
        """모의 주문 상태 반환"""
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "list": [
                    {
                        "orderId": order_id,
                        "orderStatus": "Filled",
                        "symbol": "BTCUSDT",
                        "side": "Buy",
                        "orderType": "Market",
                        "qty": "0.001",
                        "price": "50000.00",
                        "avgPrice": "50000.00",
                        "cumExecQty": "0.001",
                        "cumExecValue": "50.00",
                        "timeInForce": "GTC",
                        "createdTime": str(int(time.time() * 1000) - 60000),
                        "updatedTime": str(int(time.time() * 1000))
                    }
                ]
            }
        }
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """주문 취소"""
        if self.test_mode:
            return self._cancel_mock_order(order_id)
        
        try:
            url = f"{self.base_url}/v5/order/cancel"
            
            cancel_data = {
                "category": "linear",
                "orderId": order_id
            }
            
            params = json.dumps(cancel_data)
            headers = self._get_headers(params)
            
            response = requests.post(url, headers=headers, data=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"주문 취소 실패: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def _cancel_mock_order(self, order_id: str) -> Dict[str, Any]:
        """모의 주문 취소"""
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "orderId": order_id,
                "orderStatus": "Cancelled"
            }
        }
    
    def get_kline_data(self, symbol: str, interval: str = "1", limit: int = 200) -> List[Dict[str, Any]]:
        """K라인 데이터 조회"""
        try:
            url = f"{self.base_url}/v5/market/kline"
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('result', {}).get('list', [])
            
        except Exception as e:
            logger.error(f"K라인 데이터 조회 실패: {e}")
            return []
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """현재 가격 조회"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                "category": "linear",
                "symbol": symbol
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            result = data.get('result', {}).get('list', [])
            
            if result:
                return float(result[0].get('lastPrice', 0))
            
            return None
            
        except Exception as e:
            logger.error(f"가격 조회 실패: {e}")
            return None
    
    def place_market_order(self, symbol: str, side: str, qty: str) -> Dict[str, Any]:
        """시장가 주문"""
        return self.place_order(symbol, side, "Market", qty)
    
    def place_limit_order(self, symbol: str, side: str, qty: str, price: str, 
                         time_in_force: str = "GTC") -> Dict[str, Any]:
        """지정가 주문"""
        return self.place_order(symbol, side, "Limit", qty, price, time_in_force)
    
    def place_stop_limit_order(self, symbol: str, side: str, qty: str, price: str, 
                              stop_price: str, time_in_force: str = "GTC") -> Dict[str, Any]:
        """스탑 지정가 주문"""
        if self.test_mode:
            return self._place_mock_stop_limit_order(symbol, side, qty, price, stop_price)
        
        try:
            url = f"{self.base_url}/v5/order/create"
            
            order_data = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": "StopLimit",
                "qty": qty,
                "price": price,
                "stopPrice": stop_price,
                "timeInForce": time_in_force
            }
            
            params = json.dumps(order_data)
            headers = self._get_headers(params)
            
            response = requests.post(url, headers=headers, data=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"스탑 지정가 주문 생성 실패: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def _place_mock_stop_limit_order(self, symbol: str, side: str, qty: str, 
                                   price: str, stop_price: str) -> Dict[str, Any]:
        """모의 스탑 지정가 주문 생성"""
        order_id = f"mock_stop_{int(time.time() * 1000)}"
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "orderId": order_id,
                "orderLinkId": f"mock_stop_link_{order_id}",
                "symbol": symbol,
                "side": side,
                "orderType": "StopLimit",
                "qty": qty,
                "price": price,
                "stopPrice": stop_price,
                "timeInForce": "GTC",
                "orderStatus": "New",
                "createdTime": str(int(time.time() * 1000))
            }
        }
    
    def is_order_filled(self, order_id: str) -> bool:
        """주문 체결 여부 확인"""
        try:
            order_info = self.get_order_status(order_id)
            if order_info and order_info.get('retCode') == 0:
                result = order_info.get('result', {})
                orders = result.get('list', [])
                if orders:
                    status = orders[0].get('orderStatus', '')
                    return status in ['Filled', 'PartiallyFilled']
            return False
        except Exception as e:
            logger.error(f"주문 체결 확인 실패: {e}")
            return False
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """미체결 주문 조회"""
        if self.test_mode:
            return self._get_mock_open_orders(symbol)
        
        try:
            url = f"{self.base_url}/v5/order/realtime"
            params = {"category": "linear"}
            if symbol:
                params["symbol"] = symbol
            
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            headers = self._get_headers(param_str)
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('retCode') == 0:
                return data.get('result', {}).get('list', [])
            return []
            
        except Exception as e:
            logger.error(f"미체결 주문 조회 실패: {e}")
            return []
    
    def _get_mock_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """모의 미체결 주문 반환"""
        return [
            {
                "orderId": f"mock_open_{int(time.time() * 1000)}",
                "symbol": symbol or "BTCUSDT",
                "side": "Buy",
                "orderType": "Limit",
                "qty": "0.001",
                "price": "45000.00",
                "orderStatus": "New",
                "createdTime": str(int(time.time() * 1000) - 300000)
            }
        ]
