"""
카카오 토큰 최초 발급 스크립트 (1회만 실행)
실행 전: pip install requests
"""
import requests
import webbrowser

REST_API_KEY = input("카카오 REST API 키 입력: ").strip()
REDIRECT_URI = "https://example.com"  # 앱 설정에 등록한 Redirect URI와 동일해야 함

# 1단계: 인증 URL 열기
auth_url = (
    f"https://kauth.kakao.com/oauth/authorize"
    f"?client_id={REST_API_KEY}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
)
print(f"\n브라우저가 열립니다. 카카오 로그인 후 리다이렉트된 URL을 복사하세요.")
print(f"URL: {auth_url}\n")
webbrowser.open(auth_url)

# 2단계: 리다이렉트 URL에서 code 추출
redirected = input("리다이렉트된 전체 URL 붙여넣기: ").strip()
code = redirected.split("code=")[1].split("&")[0]
print(f"\n인증 코드: {code}")

# 3단계: 토큰 발급
resp = requests.post(
    "https://kauth.kakao.com/oauth/token",
    data={
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
)
result = resp.json()

if "error" in result:
    print(f"\n오류: {result}")
else:
    print("\n✅ 토큰 발급 성공!")
    print(f"\nGitHub Secrets에 아래 값들을 등록하세요:")
    print(f"  KAKAO_REST_API_KEY  = {REST_API_KEY}")
    print(f"  KAKAO_REFRESH_TOKEN = {result['refresh_token']}")
