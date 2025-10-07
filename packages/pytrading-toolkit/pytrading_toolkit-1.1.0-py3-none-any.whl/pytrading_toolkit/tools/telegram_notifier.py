"""
공통 텔레그램 알림 모듈
업비트와 바이비트 시스템에서 공통으로 사용
"""

import requests
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """공통 텔레그램 알림 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 텔레그램 설정 딕셔너리
                - enabled: bool
                - bot_token: str
                - chat_id: str
                - notifications: dict
        """
        self.enabled = config.get('enabled', False)
        self.bot_token = config.get('bot_token', '')
        self.chat_id = config.get('chat_id', '')
        self.notifications = config.get('notifications', {})
        
        # 설정 검증
        if self.enabled and (not self.bot_token or not self.chat_id):
            logger.warning("텔레그램 설정이 불완전합니다")
            self.enabled = False
        
        logger.info(f"텔레그램 알림 초기화: {'활성' if self.enabled else '비활성'}")
    
    def send_message(self, message: str) -> bool:
        """기본 메시지 전송"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            logger.debug("텔레그램 메시지 전송 성공")
            return True
            
        except Exception as e:
            logger.error(f"텔레그램 메시지 전송 실패: {e}")
            return False
    
    def send_system_status(self, system_name: str, status_info: Dict[str, Any]) -> bool:
        """시스템 상태 알림"""
        if not self.notifications.get('system_start', True):
            return False
        
        try:
            message = f"🚀 <b>{system_name} 거래 시스템 시작</b>\n\n"
            
            for key, value in status_info.items():
                message += f"• {key}: {value}\n"
            
            message += f"\n⏰ 시작 시간: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"시스템 상태 알림 실패: {e}")
            return False
    
    def send_trade_signal(self, signal_type: str, side: str, price: float, 
                         amount: float, balance_info: str = "", 
                         currency_pair: str = "BTC") -> bool:
        """거래 신호 알림"""
        if not self.notifications.get('trade_signals', True):
            return False
        
        try:
            if signal_type == "entry":
                emoji = "📈" if side == "buy" or side == "long" else "📉"
                title = f"{emoji} <b>{side.upper()} 진입 신호</b>"
            else:  # exit
                emoji = "📉" if side == "sell" or side == "short" else "📈"
                title = f"{emoji} <b>{side.upper()} 청산 신호</b>"
            
            message = f"{title}\n\n"
            message += f"• 가격: {price:,.2f}\n"
            message += f"• 수량: {amount:.8f} {currency_pair}\n"
            
            if balance_info:
                message += f"• {balance_info}\n"
            
            message += f"\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"거래 신호 알림 실패: {e}")
            return False
    
    def send_order_placed(self, side: str, signal_type: str, price: float, 
                         amount: float, order_id: str,
                         currency_pair: str = "BTC") -> bool:
        """주문 실행 알림"""
        if not self.notifications.get('order_execution', True):
            return False
        
        try:
            if signal_type == "entry":
                emoji = "💰" if side in ["buy", "long"] else "💸"
                title = f"{emoji} <b>{side.upper()} 진입 주문</b>"
            else:
                emoji = "💸" if side in ["sell", "short"] else "💰"
                title = f"{emoji} <b>{side.upper()} 청산 주문</b>"
            
            message = f"{title}\n\n"
            message += f"• 가격: {price:,.2f}\n"
            message += f"• 수량: {amount:.8f} {currency_pair}\n"
            message += f"• 주문 ID: <code>{order_id}</code>\n"
            message += f"\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"주문 실행 알림 실패: {e}")
            return False
    
    def send_order_executed(self, side: str, signal_type: str, price: float, 
                           amount: float, order_id: str, pnl: Optional[float] = None,
                           currency_pair: str = "BTC") -> bool:
        """주문 체결 알림"""
        if not self.notifications.get('order_execution', True):
            return False
        
        try:
            emoji = "🎉"
            title = f"{emoji} <b>{side.upper()} 주문 체결</b>"
            
            message = f"{title}\n\n"
            message += f"• 체결가: {price:,.2f}\n"
            message += f"• 체결량: {amount:.8f} {currency_pair}\n"
            message += f"• 주문 ID: <code>{order_id}</code>\n"
            
            if pnl is not None:
                pnl_emoji = "💰" if pnl > 0 else "💸"
                message += f"• 손익: {pnl_emoji} {pnl:+.2f}\n"
            
            message += f"\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"주문 체결 알림 실패: {e}")
            return False
    
    def send_position_update(self, position_info: Dict[str, Any],
                           currency_pair: str = "BTC") -> bool:
        """포지션 업데이트 알림"""
        if not self.notifications.get('position_updates', True):
            return False
        
        try:
            message = "📊 <b>포지션 현황</b>\n\n"
            
            # 롱 포지션 (업비트는 매수, 바이비트는 롱)
            long_size = position_info.get('long_size', 0) or position_info.get('btc_balance', 0)
            long_value = position_info.get('long_value', 0)
            
            # 숏 포지션 (바이비트만)
            short_size = position_info.get('short_size', 0)
            short_value = position_info.get('short_value', 0)
            
            # 미실현 손익
            unrealized_pnl = position_info.get('unrealized_pnl', 0)
            
            if long_size > 0:
                if long_value > 0:
                    message += f"📈 롱: {long_size:.8f} {currency_pair} ({long_value:.2f})\n"
                else:
                    message += f"📈 보유: {long_size:.8f} {currency_pair}\n"
            
            if short_size > 0:
                message += f"📉 숏: {short_size:.8f} {currency_pair} ({short_value:.2f})\n"
            
            if long_size == 0 and short_size == 0:
                message += "• 포지션 없음\n"
            
            if unrealized_pnl != 0:
                pnl_emoji = "💰" if unrealized_pnl > 0 else "💸"
                message += f"\n• 미실현 손익: {pnl_emoji} {unrealized_pnl:+.2f}\n"
            
            message += f"\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"포지션 업데이트 알림 실패: {e}")
            return False
    
    def send_error(self, error_type: str, error_message: str, 
                   function_name: str = "") -> bool:
        """에러 알림"""
        if not self.notifications.get('errors', True):
            return False
        
        try:
            message = f"⚠️ <b>시스템 오류</b>\n\n"
            message += f"• 오류 유형: {error_type}\n"
            
            if function_name:
                message += f"• 발생 위치: {function_name}\n"
            
            message += f"• 상세 내용: {error_message}\n"
            message += f"\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"에러 알림 실패: {e}")
            return False
    
    def send_critical_error(self, title: str, error_message: str) -> bool:
        """중요 에러 알림"""
        try:
            message = f"🚨 <b>{title}</b>\n\n"
            message += f"{error_message}\n"
            message += f"\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"중요 에러 알림 실패: {e}")
            return False
    
    def send_daily_summary(self, summary_data: Dict[str, Any]) -> bool:
        """일일 요약 알림"""
        try:
            message = "📊 <b>일일 거래 요약</b>\n\n"
            
            for key, value in summary_data.items():
                message += f"• {key}: {value}\n"
            
            message += f"\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"일일 요약 알림 실패: {e}")
            return False
