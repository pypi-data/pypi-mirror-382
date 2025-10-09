# KOSPI-KOSDAQ SSE Remote Server

## 개요
이 프로젝트는 기존 KOSPI-KOSDAQ MCP 서버를 SSE(Server-Sent Events) 방식의 원격 서버로 변환한 것입니다. 실시간 주식 데이터를 웹 기반 클라이언트에 제공합니다.

## 주요 기능
- **SSE 실시간 통신**: 서버에서 클라이언트로 실시간 데이터 푸시
- **RESTful API**: 주식 데이터 조회를 위한 HTTP 엔드포인트
- **WebSocket 지원**: SSE 대안으로 WebSocket 연결 제공
- **자동 재연결**: 연결 끊김 시 자동 재연결 지원
- **CORS 지원**: 크로스 오리진 요청 허용

## 빠른 시작

### 1. 서버 실행
```bash
# 실행 스크립트 사용
./run_sse_server.sh

# 또는 직접 실행
python -m uvicorn sse_remote_server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 웹 클라이언트 열기
브라우저에서 `client.html` 파일을 열고 "연결" 버튼을 클릭합니다.

### 3. Python 클라이언트 실행
```bash
python sse_client_example.py
```

## 프로젝트 구조
```
kospi-kosdaq-stock-server/
├── sse_remote_server.py      # SSE 서버 메인 코드
├── sse_client_example.py     # Python 클라이언트 예제
├── client.html               # 웹 클라이언트 UI
├── requirements_sse.txt      # SSE 서버 의존성
├── run_sse_server.sh        # 서버 실행 스크립트
├── Dockerfile.sse           # Docker 이미지 빌드
├── docker-compose.yml       # Docker Compose 설정
└── README_SSE.md           # 이 문서
```

## API 문서
자세한 API 문서는 서버 실행 후 http://localhost:8000/docs 에서 확인할 수 있습니다.
