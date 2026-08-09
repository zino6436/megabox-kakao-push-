"""
카카오 토큰 최초 발급 스크립트 (1회만 실행)
외부 라이브러리 불필요 — 표준 라이브러리만 사용
"""
import urllib.request
import urllib.parse
import json
import webbrowser

REST_API_KEY = input("카카오 REST API 키 입력: ").strip()
CLIENT_SECRET = input("Client Secret 입력 (없으면 엔터): ").strip()
REDIRECT_URI = "https://example.com"

auth_url = (
    f"https://kauth.kakao.com/oauth/authorize"
    f"?client_id={REST_API_KEY}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
    f"&response_type=code"
)

print("\n브라우저가 열립니다.")
print("① 카카오 로그인 완료")
print("② 브라우저가 example.com 페이지로 이동 (오류 페이지 정상)")
print("③ 브라우저 주소창에서 https://example.com?code=... URL 전체 복사")
print("④ 아래에 붙여넣기\n")
webbrowser.open(auth_url)

while True:
    redirected = input("리다이렉트된 URL 붙여넣기: ").strip()
    if "code=" in redirected:
        break
    print("  ❌ URL에 'code='가 없습니다. example.com으로 이동된 주소창 URL을 복사해주세요.\n")

code = urllib.parse.parse_qs(urllib.parse.urlparse(redirected).query).get("code", [None])[0]
print(f"\n인증 코드 확인됨: {code[:10]}...")

token_params = {
    "grant_type": "authorization_code",
    "client_id": REST_API_KEY,
    "redirect_uri": REDIRECT_URI,
    "code": code,
}
if CLIENT_SECRET:
    token_params["client_secret"] = CLIENT_SECRET
data = urllib.parse.urlencode(token_params).encode()

req = urllib.request.Request(
    "https://kauth.kakao.com/oauth/token",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
except urllib.error.HTTPError as e:
    print(f"\n오류 코드: {e.code}")
    print(f"오류 내용: {e.read().decode()}")
    exit(1)

if "error" in result:
    print(f"\n오류: {result}")
else:
    print("\n✅ 토큰 발급 성공!")
    print(f"\nGitHub Secrets에 아래 두 값을 등록하세요:")
    print(f"\n  KAKAO_REST_API_KEY  = {REST_API_KEY}")
    print(f"  KAKAO_REFRESH_TOKEN = {result['refresh_token']}")
