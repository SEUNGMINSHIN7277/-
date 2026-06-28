"""YouTube 업로드용 OAuth 토큰 발급 헬퍼.

사전 준비(사용자):
  1) Google Cloud 프로젝트 생성 → 'YouTube Data API v3' 사용 설정
  2) OAuth 동의 화면 구성(외부/테스트 사용자에 본인 추가)
  3) 사용자 인증 정보 → 'OAuth 클라이언트 ID'(데스크톱 앱) → client_secret json 다운로드

사용:
  python -m shorts_agent.auth_youtube client_secret.json youtube_token.json
  → 브라우저 동의 후 youtube_token.json 생성.
  → .env 의 YOUTUBE_TOKEN_FILE=youtube_token.json 로 지정.
"""
from __future__ import annotations

import sys

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main(argv=None) -> None:
    argv = argv or sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)
    client_secret = argv[0]
    out = argv[1] if len(argv) > 1 else "youtube_token.json"
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("google-auth-oauthlib 가 필요합니다: pip install google-auth-oauthlib")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
    try:
        creds = flow.run_local_server(port=0)  # 로컬 브라우저로 동의
    except Exception:
        # 헤드리스 환경 폴백(콘솔에 URL 출력 후 코드 입력)
        creds = flow.run_console()
    with open(out, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    print(f"✅ 토큰 저장: {out}\n.env 에 YOUTUBE_TOKEN_FILE={out} 를 설정하세요.")


if __name__ == "__main__":
    main()
