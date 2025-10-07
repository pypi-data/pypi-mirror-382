"""
메트릭 전송 시스템 - 배치 처리 및 압축
"""
import gzip
import json
import logging
import queue
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class MetricsTransmitter:
    """메트릭을 배치로 수집하고 압축하여 전송하는 클래스"""

    def __init__(self, config: Any):
        """
        메트릭 전송기 초기화

        Args:
            config: 에이전트 설정
        """
        self.config = config
        self.api_url = config.api_url
        self.api_token = config.api_token
        self.agent_id = config.agent_id

        # 배치 설정
        self.batch_size = getattr(config, 'metrics_batch_size', 10)  # 한 번에 전송할 메트릭 수
        self.batch_interval = getattr(config, 'metrics_batch_interval', 60)  # 배치 전송 간격 (초)
        self.compression_enabled = getattr(config, 'metrics_compression', True)  # 압축 사용 여부

        # 메트릭 큐
        self.metrics_queue = deque(maxlen=1000)  # 최대 1000개 메트릭 저장
        self.failed_queue = deque(maxlen=100)  # 실패한 메트릭 재전송 큐

        # 통계
        self.stats = {
            'total_sent': 0,
            'total_failed': 0,
            'total_compressed_bytes': 0,
            'total_uncompressed_bytes': 0,
            'last_sent_time': None,
            'last_error': None
        }

        # 스레드 관리
        self.running = False
        self.transmit_thread = None
        self.lock = threading.Lock()

    def add_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        메트릭을 큐에 추가

        Args:
            metrics: 전송할 메트릭 데이터
        """
        with self.lock:
            # 타임스탬프 추가
            if 'timestamp' not in metrics:
                metrics['timestamp'] = datetime.utcnow().isoformat()

            # 에이전트 ID 추가
            metrics['agent_id'] = self.agent_id

            self.metrics_queue.append(metrics)
            logger.debug(f"메트릭 추가됨. 큐 크기: {len(self.metrics_queue)}")

    def _compress_data(self, data: str) -> bytes:
        """
        데이터를 gzip으로 압축

        Args:
            data: 압축할 JSON 문자열

        Returns:
            압축된 바이트 데이터
        """
        return gzip.compress(data.encode('utf-8'))

    def _prepare_batch(self) -> Optional[List[Dict[str, Any]]]:
        """
        전송할 배치 준비

        Returns:
            배치 메트릭 리스트 또는 None
        """
        batch = []

        with self.lock:
            # 실패한 메트릭 우선 처리
            while self.failed_queue and len(batch) < self.batch_size:
                batch.append(self.failed_queue.popleft())

            # 새 메트릭 추가
            while self.metrics_queue and len(batch) < self.batch_size:
                batch.append(self.metrics_queue.popleft())

        return batch if batch else None

    def _send_batch(self, batch: List[Dict[str, Any]]) -> bool:
        """
        메트릭 배치를 서버로 전송

        Args:
            batch: 전송할 메트릭 리스트

        Returns:
            성공 여부
        """
        try:
            # 배치 데이터 준비
            batch_data = {
                'agent_id': self.agent_id,
                'batch_size': len(batch),
                'metrics': batch,
                'compressed': self.compression_enabled
            }

            # JSON 직렬화
            json_data = json.dumps(batch_data)
            self.stats['total_uncompressed_bytes'] += len(json_data)

            # 헤더 설정
            headers = {
                'Authorization': f'Bearer {self.api_token}'
            }

            # 압축 처리
            if self.compression_enabled:
                compressed_data = self._compress_data(json_data)
                self.stats['total_compressed_bytes'] += len(compressed_data)

                headers['Content-Type'] = 'application/gzip'
                headers['X-Content-Encoding'] = 'gzip'

                compression_ratio = (1 - len(compressed_data) / len(json_data)) * 100
                logger.debug(f"압축률: {compression_ratio:.1f}% "
                           f"({len(json_data)} → {len(compressed_data)} bytes)")

                payload = compressed_data
            else:
                headers['Content-Type'] = 'application/json'
                payload = json_data

            # 전송
            response = requests.post(
                f"{self.api_url}/api/v1/metrics/batch",
                data=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                self.stats['total_sent'] += len(batch)
                self.stats['last_sent_time'] = datetime.utcnow()
                logger.info(f"메트릭 배치 전송 성공: {len(batch)}개")
                return True
            else:
                logger.error(f"메트릭 배치 전송 실패: HTTP {response.status_code}")
                self.stats['last_error'] = f"HTTP {response.status_code}"
                return False

        except requests.exceptions.Timeout:
            logger.error("메트릭 전송 타임아웃")
            self.stats['last_error'] = "Timeout"
            return False

        except requests.exceptions.ConnectionError:
            logger.error("서버 연결 실패")
            self.stats['last_error'] = "Connection error"
            return False

        except Exception as e:
            logger.error(f"메트릭 전송 오류: {e}")
            self.stats['last_error'] = str(e)
            return False

    def _transmit_loop(self) -> None:
        """메트릭 전송 루프"""
        logger.info("메트릭 전송 루프 시작")
        last_transmit_time = time.time()

        while self.running:
            try:
                current_time = time.time()

                # 배치 간격이 지났거나 큐가 가득 찬 경우 전송
                should_transmit = (
                    (current_time - last_transmit_time >= self.batch_interval) or
                    (len(self.metrics_queue) >= self.batch_size)
                )

                if should_transmit:
                    batch = self._prepare_batch()

                    if batch:
                        success = self._send_batch(batch)

                        if not success:
                            # 실패한 메트릭을 재전송 큐에 추가
                            with self.lock:
                                for metric in batch:
                                    if len(self.failed_queue) < self.failed_queue.maxlen:
                                        self.failed_queue.append(metric)
                            self.stats['total_failed'] += len(batch)

                    last_transmit_time = current_time

                # 짧은 대기
                time.sleep(1)

            except Exception as e:
                logger.error(f"전송 루프 오류: {e}")
                time.sleep(5)

        logger.info("메트릭 전송 루프 종료")

    def start(self) -> None:
        """메트릭 전송기 시작"""
        if self.running:
            return

        self.running = True
        self.transmit_thread = threading.Thread(target=self._transmit_loop)
        self.transmit_thread.daemon = True
        self.transmit_thread.start()
        logger.info("메트릭 전송기 시작됨")

    def stop(self) -> None:
        """메트릭 전송기 정지"""
        if not self.running:
            return

        self.running = False

        if self.transmit_thread:
            self.transmit_thread.join(timeout=5)

        # 남은 메트릭 전송 시도
        self._flush()

        logger.info("메트릭 전송기 정지됨")

    def _flush(self) -> None:
        """남은 모든 메트릭 전송"""
        while True:
            batch = self._prepare_batch()
            if not batch:
                break

            self._send_batch(batch)

    def get_stats(self) -> Dict[str, Any]:
        """
        전송 통계 반환

        Returns:
            통계 정보
        """
        with self.lock:
            stats = self.stats.copy()
            stats['queue_size'] = len(self.metrics_queue)
            stats['failed_queue_size'] = len(self.failed_queue)

            if stats['total_uncompressed_bytes'] > 0:
                stats['compression_ratio'] = (
                    1 - stats['total_compressed_bytes'] / stats['total_uncompressed_bytes']
                ) * 100
            else:
                stats['compression_ratio'] = 0

        return stats


class MetricsAggregator:
    """메트릭을 집계하여 전송 크기를 줄이는 클래스"""

    def __init__(self, window_size: int = 60):
        """
        메트릭 집계기 초기화

        Args:
            window_size: 집계 윈도우 크기 (초)
        """
        self.window_size = window_size
        self.metrics_window = deque()
        self.lock = threading.Lock()

    def add_sample(self, metrics: Dict[str, Any]) -> None:
        """
        메트릭 샘플 추가

        Args:
            metrics: 메트릭 데이터
        """
        with self.lock:
            # 타임스탬프 추가
            metrics['_timestamp'] = time.time()
            self.metrics_window.append(metrics)

            # 오래된 샘플 제거
            cutoff_time = time.time() - self.window_size
            while self.metrics_window and self.metrics_window[0]['_timestamp'] < cutoff_time:
                self.metrics_window.popleft()

    def get_aggregated(self) -> Optional[Dict[str, Any]]:
        """
        집계된 메트릭 반환

        Returns:
            집계된 메트릭 또는 None
        """
        with self.lock:
            if not self.metrics_window:
                return None

            # CPU 집계
            cpu_values = [m.get('cpu', {}).get('usage_percent', 0)
                         for m in self.metrics_window if 'cpu' in m]

            # 메모리 집계
            memory_values = [m.get('memory', {}).get('percent', 0)
                            for m in self.metrics_window if 'memory' in m]

            # 디스크 집계
            disk_values = [m.get('disk', {}).get('percent', 0)
                          for m in self.metrics_window if 'disk' in m]

            aggregated = {
                'window_size': self.window_size,
                'sample_count': len(self.metrics_window),
                'start_time': self.metrics_window[0]['_timestamp'],
                'end_time': self.metrics_window[-1]['_timestamp'],
                'cpu': {
                    'avg': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    'min': min(cpu_values) if cpu_values else 0,
                    'max': max(cpu_values) if cpu_values else 0
                },
                'memory': {
                    'avg': sum(memory_values) / len(memory_values) if memory_values else 0,
                    'min': min(memory_values) if memory_values else 0,
                    'max': max(memory_values) if memory_values else 0
                },
                'disk': {
                    'avg': sum(disk_values) / len(disk_values) if disk_values else 0,
                    'min': min(disk_values) if disk_values else 0,
                    'max': max(disk_values) if disk_values else 0
                }
            }

            # 네트워크 데이터는 델타 계산
            network_samples = [m.get('network', {}) for m in self.metrics_window if 'network' in m]
            if len(network_samples) >= 2:
                first_net = network_samples[0]
                last_net = network_samples[-1]

                aggregated['network'] = {
                    'bytes_sent_delta': (last_net.get('bytes_sent', 0) -
                                        first_net.get('bytes_sent', 0)),
                    'bytes_recv_delta': (last_net.get('bytes_recv', 0) -
                                        first_net.get('bytes_recv', 0))
                }

            return aggregated