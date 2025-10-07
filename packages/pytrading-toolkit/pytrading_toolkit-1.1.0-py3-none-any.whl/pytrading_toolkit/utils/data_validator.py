#!/usr/bin/env python3
"""
데이터 무결성 검증 모듈
거래 데이터의 유효성 검증
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data: Any = None

class DataValidator:
    """데이터 검증 클래스"""
    
    def __init__(self):
        self.price_pattern = re.compile(r'^\d+\.?\d*$')
        self.symbol_pattern = re.compile(r'^[A-Z]{2,10}USDT?$')
        self.order_id_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    def validate_price(self, price: Union[str, float, int]) -> ValidationResult:
        """가격 데이터 검증"""
        errors = []
        warnings = []
        
        try:
            # 타입 변환
            if isinstance(price, str):
                price_str = price.strip()
                if not price_str:
                    errors.append("가격이 비어있습니다")
                    return ValidationResult(False, errors, warnings)
                
                try:
                    price_float = float(price_str)
                except ValueError:
                    errors.append(f"가격 형식이 잘못되었습니다: {price_str}")
                    return ValidationResult(False, errors, warnings)
            else:
                price_float = float(price)
            
            # 범위 검증
            if price_float <= 0:
                errors.append(f"가격은 0보다 커야 합니다: {price_float}")
            elif price_float > 1000000:  # 100만 이상은 의심
                warnings.append(f"가격이 매우 높습니다: {price_float}")
            
            # 소수점 자릿수 검증 (최대 8자리)
            if isinstance(price, str) and '.' in price:
                decimal_places = len(price.split('.')[1])
                if decimal_places > 8:
                    warnings.append(f"소수점 자릿수가 많습니다: {decimal_places}자리")
            
            return ValidationResult(len(errors) == 0, errors, warnings, price_float)
            
        except Exception as e:
            errors.append(f"가격 검증 중 오류: {e}")
            return ValidationResult(False, errors, warnings)
    
    def validate_quantity(self, quantity: Union[str, float, int]) -> ValidationResult:
        """수량 데이터 검증"""
        errors = []
        warnings = []
        
        try:
            # 타입 변환
            if isinstance(quantity, str):
                quantity_str = quantity.strip()
                if not quantity_str:
                    errors.append("수량이 비어있습니다")
                    return ValidationResult(False, errors, warnings)
                
                try:
                    quantity_float = float(quantity_str)
                except ValueError:
                    errors.append(f"수량 형식이 잘못되었습니다: {quantity_str}")
                    return ValidationResult(False, errors, warnings)
            else:
                quantity_float = float(quantity)
            
            # 범위 검증
            if quantity_float <= 0:
                errors.append(f"수량은 0보다 커야 합니다: {quantity_float}")
            elif quantity_float > 1000:  # 1000 이상은 의심
                warnings.append(f"수량이 매우 큽니다: {quantity_float}")
            
            # 소수점 자릿수 검증 (최대 8자리)
            if isinstance(quantity, str) and '.' in quantity:
                decimal_places = len(quantity.split('.')[1])
                if decimal_places > 8:
                    warnings.append(f"소수점 자릿수가 많습니다: {decimal_places}자리")
            
            return ValidationResult(len(errors) == 0, errors, warnings, quantity_float)
            
        except Exception as e:
            errors.append(f"수량 검증 중 오류: {e}")
            return ValidationResult(False, errors, warnings)
    
    def validate_symbol(self, symbol: str) -> ValidationResult:
        """심볼 데이터 검증"""
        errors = []
        warnings = []
        
        try:
            if not symbol:
                errors.append("심볼이 비어있습니다")
                return ValidationResult(False, errors, warnings)
            
            symbol = symbol.strip().upper()
            
            # 형식 검증
            if not self.symbol_pattern.match(symbol):
                errors.append(f"심볼 형식이 잘못되었습니다: {symbol}")
                return ValidationResult(False, errors, warnings)
            
            # 길이 검증
            if len(symbol) < 3 or len(symbol) > 12:
                warnings.append(f"심볼 길이가 비정상적입니다: {len(symbol)}자")
            
            return ValidationResult(True, errors, warnings, symbol)
            
        except Exception as e:
            errors.append(f"심볼 검증 중 오류: {e}")
            return ValidationResult(False, errors, warnings)
    
    def validate_order_id(self, order_id: str) -> ValidationResult:
        """주문 ID 검증"""
        errors = []
        warnings = []
        
        try:
            if not order_id:
                errors.append("주문 ID가 비어있습니다")
                return ValidationResult(False, errors, warnings)
            
            order_id = order_id.strip()
            
            # 형식 검증
            if not self.order_id_pattern.match(order_id):
                errors.append(f"주문 ID 형식이 잘못되었습니다: {order_id}")
                return ValidationResult(False, errors, warnings)
            
            # 길이 검증
            if len(order_id) < 5 or len(order_id) > 50:
                warnings.append(f"주문 ID 길이가 비정상적입니다: {len(order_id)}자")
            
            return ValidationResult(True, errors, warnings, order_id)
            
        except Exception as e:
            errors.append(f"주문 ID 검증 중 오류: {e}")
            return ValidationResult(False, errors, warnings)
    
    def validate_candle_data(self, candle: Dict[str, Any]) -> ValidationResult:
        """캔들 데이터 검증"""
        errors = []
        warnings = []
        
        try:
            if not isinstance(candle, dict):
                errors.append("캔들 데이터가 딕셔너리가 아닙니다")
                return ValidationResult(False, errors, warnings)
            
            # 필수 필드 검증
            required_fields = ['open', 'high', 'low', 'close', 'volume']
            for field in required_fields:
                if field not in candle:
                    errors.append(f"필수 필드 누락: {field}")
                elif candle[field] is None:
                    errors.append(f"필수 필드가 None: {field}")
            
            if errors:
                return ValidationResult(False, errors, warnings)
            
            # 가격 데이터 검증
            price_fields = ['open', 'high', 'low', 'close']
            for field in price_fields:
                price_result = self.validate_price(candle[field])
                if not price_result.is_valid:
                    errors.extend([f"{field}: {err}" for err in price_result.errors])
                warnings.extend([f"{field}: {warn}" for warn in price_result.warnings])
            
            # 수량 데이터 검증
            volume_result = self.validate_quantity(candle['volume'])
            if not volume_result.is_valid:
                errors.extend([f"volume: {err}" for err in volume_result.errors])
            warnings.extend([f"volume: {warn}" for warn in volume_result.warnings])
            
            # OHLC 논리 검증
            if all(field in candle for field in price_fields):
                open_price = float(candle['open'])
                high_price = float(candle['high'])
                low_price = float(candle['low'])
                close_price = float(candle['close'])
                
                if high_price < max(open_price, close_price):
                    errors.append("고가가 시가나 종가보다 낮습니다")
                
                if low_price > min(open_price, close_price):
                    errors.append("저가가 시가나 종가보다 높습니다")
                
                if high_price < low_price:
                    errors.append("고가가 저가보다 낮습니다")
            
            return ValidationResult(len(errors) == 0, errors, warnings, candle)
            
        except Exception as e:
            errors.append(f"캔들 데이터 검증 중 오류: {e}")
            return ValidationResult(False, errors, warnings)
    
    def validate_order_data(self, order: Dict[str, Any]) -> ValidationResult:
        """주문 데이터 검증"""
        errors = []
        warnings = []
        
        try:
            if not isinstance(order, dict):
                errors.append("주문 데이터가 딕셔너리가 아닙니다")
                return ValidationResult(False, errors, warnings)
            
            # 필수 필드 검증
            required_fields = ['symbol', 'side', 'orderType', 'qty']
            for field in required_fields:
                if field not in order:
                    errors.append(f"필수 필드 누락: {field}")
                elif order[field] is None:
                    errors.append(f"필수 필드가 None: {field}")
            
            if errors:
                return ValidationResult(False, errors, warnings)
            
            # 심볼 검증
            symbol_result = self.validate_symbol(order['symbol'])
            if not symbol_result.is_valid:
                errors.extend([f"symbol: {err}" for err in symbol_result.errors])
            warnings.extend([f"symbol: {warn}" for warn in symbol_result.warnings])
            
            # 수량 검증
            qty_result = self.validate_quantity(order['qty'])
            if not qty_result.is_valid:
                errors.extend([f"qty: {err}" for err in qty_result.errors])
            warnings.extend([f"qty: {warn}" for warn in qty_result.warnings])
            
            # 가격 검증 (지정가 주문인 경우)
            if order.get('orderType') == 'Limit' and 'price' in order:
                price_result = self.validate_price(order['price'])
                if not price_result.is_valid:
                    errors.extend([f"price: {err}" for err in price_result.errors])
                warnings.extend([f"price: {warn}" for warn in price_result.warnings])
            
            # 주문 ID 검증 (있는 경우)
            if 'orderId' in order and order['orderId']:
                order_id_result = self.validate_order_id(order['orderId'])
                if not order_id_result.is_valid:
                    errors.extend([f"orderId: {err}" for err in order_id_result.errors])
                warnings.extend([f"orderId: {warn}" for warn in order_id_result.warnings])
            
            return ValidationResult(len(errors) == 0, errors, warnings, order)
            
        except Exception as e:
            errors.append(f"주문 데이터 검증 중 오류: {e}")
            return ValidationResult(False, errors, warnings)
    
    def validate_balance_data(self, balance: Dict[str, Any]) -> ValidationResult:
        """잔고 데이터 검증"""
        errors = []
        warnings = []
        
        try:
            if not isinstance(balance, dict):
                errors.append("잔고 데이터가 딕셔너리가 아닙니다")
                return ValidationResult(False, errors, warnings)
            
            # 기본 구조 검증
            if 'list' not in balance:
                errors.append("잔고 데이터에 'list' 필드가 없습니다")
                return ValidationResult(False, errors, warnings)
            
            if not isinstance(balance['list'], list):
                errors.append("잔고 데이터의 'list'가 배열이 아닙니다")
                return ValidationResult(False, errors, warnings)
            
            if not balance['list']:
                warnings.append("잔고 데이터가 비어있습니다")
                return ValidationResult(True, errors, warnings, balance)
            
            # 각 계정 검증
            for i, account in enumerate(balance['list']):
                if not isinstance(account, dict):
                    errors.append(f"계정 {i}이 딕셔너리가 아닙니다")
                    continue
                
                if 'coin' not in account:
                    errors.append(f"계정 {i}에 'coin' 필드가 없습니다")
                    continue
                
                if not isinstance(account['coin'], list):
                    errors.append(f"계정 {i}의 'coin'이 배열이 아닙니다")
                    continue
                
                # 각 코인 검증
                for j, coin in enumerate(account['coin']):
                    if not isinstance(coin, dict):
                        errors.append(f"계정 {i}의 코인 {j}이 딕셔너리가 아닙니다")
                        continue
                    
                    required_coin_fields = ['coin', 'walletBalance']
                    for field in required_coin_fields:
                        if field not in coin:
                            errors.append(f"계정 {i}의 코인 {j}에 '{field}' 필드가 없습니다")
                        elif coin[field] is None:
                            errors.append(f"계정 {i}의 코인 {j}의 '{field}'이 None입니다")
                    
                    # 잔고 검증
                    if 'walletBalance' in coin and coin['walletBalance'] is not None:
                        balance_result = self.validate_quantity(coin['walletBalance'])
                        if not balance_result.is_valid:
                            errors.extend([f"계정 {i}의 코인 {j}의 walletBalance: {err}" for err in balance_result.errors])
            
            return ValidationResult(len(errors) == 0, errors, warnings, balance)
            
        except Exception as e:
            errors.append(f"잔고 데이터 검증 중 오류: {e}")
            return ValidationResult(False, errors, warnings)
    
    def validate_api_response(self, response: Dict[str, Any], expected_fields: List[str] = None) -> ValidationResult:
        """API 응답 검증"""
        errors = []
        warnings = []
        
        try:
            if not isinstance(response, dict):
                errors.append("API 응답이 딕셔너리가 아닙니다")
                return ValidationResult(False, errors, warnings)
            
            # 기본 응답 구조 검증
            if 'retCode' not in response:
                errors.append("API 응답에 'retCode' 필드가 없습니다")
            else:
                ret_code = response['retCode']
                if ret_code != 0:
                    error_msg = response.get('retMsg', 'Unknown error')
                    errors.append(f"API 오류 (코드: {ret_code}): {error_msg}")
            
            # 예상 필드 검증
            if expected_fields:
                for field in expected_fields:
                    if field not in response:
                        warnings.append(f"예상 필드 누락: {field}")
            
            return ValidationResult(len(errors) == 0, errors, warnings, response)
            
        except Exception as e:
            errors.append(f"API 응답 검증 중 오류: {e}")
            return ValidationResult(False, errors, warnings)
    
    def print_validation_result(self, result: ValidationResult, context: str = ""):
        """검증 결과 출력"""
        try:
            if context:
                print(f"🔍 {context} 검증 결과")
            else:
                print("🔍 검증 결과")
            print("=" * 40)
            
            if result.is_valid:
                print("✅ 검증 통과")
            else:
                print("❌ 검증 실패")
            
            if result.errors:
                print("\n🚨 오류:")
                for error in result.errors:
                    print(f"  - {error}")
            
            if result.warnings:
                print("\n⚠️ 경고:")
                for warning in result.warnings:
                    print(f"  - {warning}")
            
            print("=" * 40)
            
        except Exception as e:
            logger.error(f"검증 결과 출력 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 데이터 검증 테스트")
    
    validator = DataValidator()
    
    # 가격 검증 테스트
    print("\n1. 가격 검증 테스트")
    test_prices = ["50000", "50000.123", "0", "-100", "abc", "999999999"]
    for price in test_prices:
        result = validator.validate_price(price)
        validator.print_validation_result(result, f"가격 '{price}'")
    
    # 심볼 검증 테스트
    print("\n2. 심볼 검증 테스트")
    test_symbols = ["BTCUSDT", "ETHUSDT", "btcusdt", "BTC", "INVALID", ""]
    for symbol in test_symbols:
        result = validator.validate_symbol(symbol)
        validator.print_validation_result(result, f"심볼 '{symbol}'")
    
    # 캔들 데이터 검증 테스트
    print("\n3. 캔들 데이터 검증 테스트")
    test_candle = {
        "open": "50000",
        "high": "51000",
        "low": "49000",
        "close": "50500",
        "volume": "100.5"
    }
    result = validator.validate_candle_data(test_candle)
    validator.print_validation_result(result, "캔들 데이터")
