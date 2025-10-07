#!/usr/bin/env python3
"""
포지션 관리 모듈
공통 포지션 관리 로직을 패키지에서 제공
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PositionSide(Enum):
    """포지션 방향"""
    LONG = "long"
    SHORT = "short"
    NONE = "none"

class PositionStatus(Enum):
    """포지션 상태"""
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"

@dataclass
class Position:
    """포지션 정보"""
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    status: PositionStatus
    entry_time: datetime
    last_update: datetime
    
    def update_price(self, new_price: float):
        """가격 업데이트"""
        self.current_price = new_price
        self.last_update = datetime.now(timezone.utc)
        
        # 미실현 손익 계산
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = (new_price - self.entry_price) * self.size
        elif self.side == PositionSide.SHORT:
            self.unrealized_pnl = (self.entry_price - new_price) * self.size
        else:
            self.unrealized_pnl = 0.0
        
        # 미실현 손익 비율 계산
        if self.entry_price > 0:
            self.unrealized_pnl_percent = (self.unrealized_pnl / (self.entry_price * self.size)) * 100
        else:
            self.unrealized_pnl_percent = 0.0

class PositionManager:
    """포지션 관리 클래스"""
    
    def __init__(self, trader, config_loader):
        self.trader = trader
        self.config_loader = config_loader
        self.positions: Dict[str, Position] = {}
        
        # 리스크 관리 설정
        self.max_position_size = 0.1  # 최대 포지션 크기 (10%)
        self.stop_loss_percent = 5.0  # 손절 비율 (5%)
        self.take_profit_percent = 10.0  # 익절 비율 (10%)
        self.max_daily_loss = 0.05  # 일일 최대 손실 (5%)
        
        # 일일 손실 추적
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now(timezone.utc).date()
    
    def update_position(self, symbol: str, side: PositionSide, size: float, 
                       entry_price: float, current_price: float) -> Position:
        """포지션 업데이트"""
        try:
            if symbol in self.positions:
                # 기존 포지션 업데이트
                position = self.positions[symbol]
                position.side = side
                position.size = size
                position.entry_price = entry_price
                position.current_price = current_price
                position.status = PositionStatus.OPEN
                position.update_price(current_price)
            else:
                # 새 포지션 생성
                position = Position(
                    symbol=symbol,
                    side=side,
                    size=size,
                    entry_price=entry_price,
                    current_price=current_price,
                    unrealized_pnl=0.0,
                    unrealized_pnl_percent=0.0,
                    status=PositionStatus.OPEN,
                    entry_time=datetime.now(timezone.utc),
                    last_update=datetime.now(timezone.utc)
                )
                position.update_price(current_price)
                self.positions[symbol] = position
            
            logger.info(f"포지션 업데이트: {symbol} {side.value} {size} @ {entry_price}")
            return position
            
        except Exception as e:
            logger.error(f"포지션 업데이트 실패: {e}")
            return None
    
    def close_position(self, symbol: str, exit_price: float) -> Optional[Position]:
        """포지션 청산"""
        try:
            if symbol not in self.positions:
                logger.warning(f"청산할 포지션이 없습니다: {symbol}")
                return None
            
            position = self.positions[symbol]
            
            # 실현 손익 계산
            if position.side == PositionSide.LONG:
                realized_pnl = (exit_price - position.entry_price) * position.size
            elif position.side == PositionSide.SHORT:
                realized_pnl = (position.entry_price - exit_price) * position.size
            else:
                realized_pnl = 0.0
            
            # 일일 손실 업데이트
            self.daily_pnl += realized_pnl
            
            # 포지션 상태 업데이트
            position.status = PositionStatus.CLOSED
            position.current_price = exit_price
            position.update_price(exit_price)
            
            logger.info(f"포지션 청산: {symbol} {position.side.value} {position.size} @ {exit_price} (손익: {realized_pnl:.2f})")
            
            # 포지션 제거
            del self.positions[symbol]
            
            return position
            
        except Exception as e:
            logger.error(f"포지션 청산 실패: {e}")
            return None
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """손절 조건 확인"""
        try:
            if symbol not in self.positions:
                return False
            
            position = self.positions[symbol]
            position.update_price(current_price)
            
            # 손절 조건 확인
            if position.unrealized_pnl_percent <= -self.stop_loss_percent:
                logger.warning(f"손절 조건 충족: {symbol} {position.unrealized_pnl_percent:.2f}%")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"손절 조건 확인 실패: {e}")
            return False
    
    def check_take_profit(self, symbol: str, current_price: float) -> bool:
        """익절 조건 확인"""
        try:
            if symbol not in self.positions:
                return False
            
            position = self.positions[symbol]
            position.update_price(current_price)
            
            # 익절 조건 확인
            if position.unrealized_pnl_percent >= self.take_profit_percent:
                logger.info(f"익절 조건 충족: {symbol} {position.unrealized_pnl_percent:.2f}%")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"익절 조건 확인 실패: {e}")
            return False
    
    def check_daily_loss_limit(self) -> bool:
        """일일 손실 한도 확인"""
        try:
            # 날짜가 바뀌면 일일 손실 리셋
            current_date = datetime.now(timezone.utc).date()
            if current_date != self.last_reset_date:
                self.daily_pnl = 0.0
                self.last_reset_date = current_date
            
            # 일일 손실 한도 확인
            if self.daily_pnl <= -self.max_daily_loss:
                logger.error(f"일일 손실 한도 초과: {self.daily_pnl:.2f}%")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"일일 손실 한도 확인 실패: {e}")
            return False
    
    def get_position_size(self, symbol: str) -> float:
        """포지션 크기 조회"""
        try:
            if symbol in self.positions:
                return self.positions[symbol].size
            return 0.0
        except Exception as e:
            logger.error(f"포지션 크기 조회 실패: {e}")
            return 0.0
    
    def get_position_side(self, symbol: str) -> PositionSide:
        """포지션 방향 조회"""
        try:
            if symbol in self.positions:
                return self.positions[symbol].side
            return PositionSide.NONE
        except Exception as e:
            logger.error(f"포지션 방향 조회 실패: {e}")
            return PositionSide.NONE
    
    def get_all_positions(self) -> List[Position]:
        """모든 포지션 조회"""
        try:
            return list(self.positions.values())
        except Exception as e:
            logger.error(f"포지션 목록 조회 실패: {e}")
            return []
    
    def get_total_unrealized_pnl(self) -> float:
        """총 미실현 손익"""
        try:
            total_pnl = 0.0
            for position in self.positions.values():
                total_pnl += position.unrealized_pnl
            return total_pnl
        except Exception as e:
            logger.error(f"총 미실현 손익 계산 실패: {e}")
            return 0.0
    
    def should_close_all_positions(self) -> bool:
        """모든 포지션 청산 여부 확인"""
        try:
            # 일일 손실 한도 초과시 모든 포지션 청산
            if self.check_daily_loss_limit():
                return True
            
            # 총 미실현 손익이 일일 손실 한도 초과시 청산
            total_pnl = self.get_total_unrealized_pnl()
            if total_pnl <= -self.max_daily_loss:
                logger.error(f"총 미실현 손익이 일일 한도 초과: {total_pnl:.2f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"포지션 청산 여부 확인 실패: {e}")
            return False
    
    def print_position_status(self):
        """포지션 상태 출력"""
        try:
            print("=" * 60)
            print("📊 포지션 상태")
            print("=" * 60)
            
            if not self.positions:
                print("📋 열린 포지션이 없습니다")
                return
            
            total_pnl = 0.0
            for symbol, position in self.positions.items():
                print(f"🔹 {symbol}")
                print(f"   방향: {position.side.value.upper()}")
                print(f"   크기: {position.size}")
                print(f"   진입가: {position.entry_price:.2f}")
                print(f"   현재가: {position.current_price:.2f}")
                print(f"   미실현 손익: {position.unrealized_pnl:.2f} ({position.unrealized_pnl_percent:.2f}%)")
                print(f"   상태: {position.status.value}")
                print()
                total_pnl += position.unrealized_pnl
            
            print(f"💰 총 미실현 손익: {total_pnl:.2f}")
            print(f"📅 일일 손익: {self.daily_pnl:.2f}")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"포지션 상태 출력 실패: {e}")
    
    def set_risk_parameters(self, max_position_size: float = None, 
                           stop_loss_percent: float = None, 
                           take_profit_percent: float = None,
                           max_daily_loss: float = None):
        """리스크 매개변수 설정"""
        try:
            if max_position_size is not None:
                self.max_position_size = max_position_size
            if stop_loss_percent is not None:
                self.stop_loss_percent = stop_loss_percent
            if take_profit_percent is not None:
                self.take_profit_percent = take_profit_percent
            if max_daily_loss is not None:
                self.max_daily_loss = max_daily_loss
            
            logger.info(f"리스크 매개변수 업데이트: max_size={self.max_position_size}, "
                       f"stop_loss={self.stop_loss_percent}%, "
                       f"take_profit={self.take_profit_percent}%, "
                       f"max_daily_loss={self.max_daily_loss}%")
            
        except Exception as e:
            logger.error(f"리스크 매개변수 설정 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    print("🧪 포지션 관리 테스트")
    
    # 더미 트레이더와 설정 로더
    class DummyTrader:
        pass
    
    class DummyConfigLoader:
        pass
    
    trader = DummyTrader()
    config_loader = DummyConfigLoader()
    
    position_manager = PositionManager(trader, config_loader)
    
    # 테스트 포지션 생성
    position_manager.update_position("BTCUSDT", PositionSide.LONG, 0.001, 50000, 51000)
    position_manager.print_position_status()
    
    # 손절/익절 테스트
    print("손절 조건 테스트:", position_manager.check_stop_loss("BTCUSDT", 47000))
    print("익절 조건 테스트:", position_manager.check_take_profit("BTCUSDT", 55000))
