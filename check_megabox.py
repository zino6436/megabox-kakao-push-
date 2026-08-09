import requests
import json
import os
from datetime import datetime
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

MEGABOX_URL = 'https://www.megabox.co.kr/on/oh/ohb/SimpleBooking/selectBokdList.do'

HEADERS = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://www.megabox.co.kr',
    'Pragma': 'no-cache',
    'Referer': 'https://www.megabox.co.kr/on/oh/ohb/SimpleBooking/simpleBookingPage.do',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

# 남양주 현대 스페이스원 돌비시네마 (brchNo: 0019)
PAYLOAD = {
    "arrMovieNo": "",
    "playDe": datetime.now().strftime("%Y%m%d"),
    "brchNoListCnt": 1,
    "brchNo1": "0019",
    "brchNo2": "", "brchNo3": "", "brchNo4": "", "brchNo5": "",
    "areaCd1": "DBC",
    "areaCd2": "", "areaCd3": "", "areaCd4": "", "areaCd5": "",
    "spclbYn1": "Y",
    "spclbYn2": "", "spclbYn3": "", "spclbYn4": "", "spclbYn5": "",
    "theabKindCd1": "DBC",
    "theabKindCd2": "", "theabKindCd3": "", "theabKindCd4": "", "theabKindCd5": "",
    "brchAll": "",
    "brchSpcl": "DBC",
    "movieNo1": "", "movieNo2": "", "movieNo3": "",
    "sellChnlCd": ""
}

STATE_FILE = "state.json"


def get_available_dates():
    resp = requests.post(MEGABOX_URL, json=PAYLOAD, headers=HEADERS, verify=False, timeout=15)
    resp.encoding = 'utf-8-sig'
    data = resp.json()
    items = data.get("movieFormDeList", [])
    today = datetime.now().strftime("%Y%m%d")
    dates = {item.get("playDe", "") for item in items if item.get("playDe", "") >= today}
    return dates


def get_kakao_access_token():
    resp = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": os.environ["KAKAO_REST_API_KEY"],
            "refresh_token": os.environ["KAKAO_REFRESH_TOKEN"],
        },
        timeout=10
    )
    result = resp.json()
    if "error" in result:
        raise RuntimeError(f"카카오 토큰 갱신 실패: {result}")

    # 새 refresh_token이 발급된 경우 (만료 30일 미만 남았을 때) 파일에 저장
    new_refresh = result.get("refresh_token")
    if new_refresh:
        with open("new_refresh_token.txt", "w") as f:
            f.write(new_refresh)
        print("::warning::새 Refresh Token 발급됨. GitHub Secret KAKAO_REFRESH_TOKEN을 업데이트하세요.")

    return result["access_token"]


def send_kakao_message(access_token, new_dates):
    date_str = "\n".join(
        f"  📅 {d[:4]}.{d[4:6]}.{d[6:]}" for d in sorted(new_dates)
    )
    text = (
        f"🎬 메가박스 남양주 현대 스페이스원\n"
        f"돌비시네마 예매 오픈!\n\n"
        f"{date_str}\n\n"
        f"지금 바로 예매하세요!"
    )

    template = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://www.megabox.co.kr/booking/seat",
            "mobile_web_url": "https://www.megabox.co.kr/booking/seat"
        },
        "button_title": "예매하러 가기"
    }

    resp = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers={"Authorization": f"Bearer {access_token}"},
        data={"template_object": json.dumps(template, ensure_ascii=False)},
        timeout=10
    )
    result = resp.json()
    if result.get("result_code") == 0:
        print("카카오톡 알림 전송 성공")
    else:
        print(f"카카오톡 전송 실패: {result}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return set(json.load(f).get("dates", []))
    return set()


def save_state(dates):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"dates": sorted(dates), "updated_at": datetime.now().isoformat()},
            f, ensure_ascii=False, indent=2
        )


def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 예매 확인 시작")

    current_dates = get_available_dates()
    print(f"현재 예매 가능 날짜: {sorted(current_dates) or '없음'}")

    previous_dates = load_state()
    new_dates = current_dates - previous_dates

    if new_dates:
        print(f"새 날짜 발견: {sorted(new_dates)}")
        access_token = get_kakao_access_token()
        send_kakao_message(access_token, new_dates)
    else:
        print("새 날짜 없음")

    save_state(current_dates)
    print("완료")


if __name__ == "__main__":
    main()
