import flet as ft
import requests

# 気象庁API URL
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
WEATHER_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# JSONデータを取得する関数
def fetch_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがある場合例外を発生
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return {}

# 地域ごとの天気情報を取得する関数
def fetch_weather_forecast(area_code):
    url = WEATHER_URL_TEMPLATE.format(area_code=area_code)
    return fetch_json_data(url)

# アプリケーションのUIを構築する関数
def main(page: ft.Page):
    page.title = "地域別天気予報"
    page.scroll = "auto"

    # ヘッダー
    page.add(ft.Text("日本気象庁 地域別天気予報", style="headlineMedium"))

    # リストを表示するコンテナ
    list_view = ft.ListView(expand=True, spacing=10, padding=10)

    # 選択された地域の天気を表示するコンテナ
    weather_display = ft.Column()

    # 地域データを取得
    page.add(ft.Text("データを取得中..."))
    region_data = fetch_json_data(AREA_URL)
    regions = region_data.get("offices", {})
    page.controls.pop()  # ローディングメッセージを削除

    # 地域を選択するドロップダウン
    dropdown = ft.Dropdown(
        hint_text="地域を選択してください",
        on_change=lambda e: display_weather(e.control.value)
    )

    # ドロップダウンに地域を追加
    if regions:
        for region_id, region_info in regions.items():
            dropdown.options.append(ft.dropdown.Option(region_id, region_info["name"]))
    else:
        list_view.controls.append(ft.Text("データを取得できませんでした。", color="red"))

    # 天気を表示する関数
    def display_weather(region_id):
        if not region_id:
            return
        weather_display.controls.clear()  # 前回の天気情報を削除
        weather_display.controls.append(ft.Text(f"{regions[region_id]['name']}の天気予報を取得中..."))
        page.update()

        # 天気データを取得
        forecast_data = fetch_weather_forecast(region_id)
        if forecast_data:
            # 天気データを表示
            for forecast in forecast_data[0]["timeSeries"][0]["areas"]:
                area_name = forecast["area"]["name"]
                weathers = forecast["weathers"]
                weather_display.controls.append(ft.Text(f"{area_name}: {', '.join(weathers)}"))
        else:
            weather_display.controls.append(ft.Text("天気データを取得できませんでした。", color="red"))

        page.update()

    # UIにコンポーネントを追加
    page.add(dropdown)
    page.add(weather_display)

# アプリケーションを実行
ft.app(target=main)
