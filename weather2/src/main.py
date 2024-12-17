import flet as ft
import requests
import sqlite3

# 気象庁API URL
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
WEATHER_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# SQLiteデータベースのセットアップ
def setup_database():
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id TEXT,
            region_name TEXT,
            area_name TEXT,
            weather TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS regions (
            region_id TEXT PRIMARY KEY,
            region_name TEXT
        )
        """
    )
    conn.commit()
    conn.close()

# JSONデータを取得する関数
def fetch_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return {}

# 地域データをデータベースに保存する関数
def save_regions_to_db(regions):
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    for region_id, region_info in regions.items():
        cursor.execute(
            """
            INSERT OR REPLACE INTO regions (region_id, region_name)
            VALUES (?, ?)
            """,
            (region_id, region_info["name"])
        )
    conn.commit()
    conn.close()

# データベースから地域データを取得する関数
def get_regions_from_db():
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT region_id, region_name FROM regions")
    regions = {row[0]: {"name": row[1]} for row in cursor.fetchall()}
    conn.close()
    return regions

# 天気情報をデータベースに保存する関数
def save_weather_to_db(region_id, region_name, area_name, weather):
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO weather (region_id, region_name, area_name, weather)
        VALUES (?, ?, ?, ?)
        """,
        (region_id, region_name, area_name, weather)
    )
    conn.commit()
    conn.close()

# 天気情報をデータベースから取得する関数
def get_weather_from_db(region_id):
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT area_name, weather FROM weather
        WHERE region_id = ?
        ORDER BY timestamp DESC
        """,
        (region_id,)
    )
    weather_data = cursor.fetchall()
    conn.close()
    return weather_data

# 天気情報をUIに表示する関数
def display_weather(region_id, regions, weather_display, page):
    if not region_id:
        return

    weather_display.controls.clear()

    # データベースから天気情報を取得
    weather_data = get_weather_from_db(region_id)
    if not weather_data:
        # データベースに天気データがない場合、APIから取得
        region_name = regions[region_id]["name"]
        weather_display.controls.append(ft.Text(f"{region_name}の天気予報を取得中..."))
        page.update()

        forecast_data = fetch_json_data(WEATHER_URL_TEMPLATE.format(area_code=region_id))
        if forecast_data:
            for forecast in forecast_data[0]["timeSeries"][0]["areas"]:
                area_name = forecast["area"]["name"]
                weathers = forecast["weathers"]
                weather = ", ".join(weathers)

                # データベースに保存
                save_weather_to_db(region_id, region_name, area_name, weather)

                # UIに表示
                weather_display.controls.append(ft.Text(f"{area_name}: {weather}"))
        else:
            weather_display.controls.append(ft.Text("天気データを取得できませんでした。", color="red"))
    else:
        # データベースから取得した天気情報を表示
        for area_name, weather in weather_data:
            weather_display.controls.append(ft.Text(f"{area_name}: {weather}"))

    page.update()


# アプリケーションのUIを構築する関数
def main(page: ft.Page):
    page.title = "地域別天気予報"
    page.scroll = "auto"

    # ヘッダー
    page.add(ft.Text("日本気象庁 地域別天気予報", style="headlineMedium"))

    # ローディングメッセージ
    loading_message = ft.Text("データを取得中...")
    page.add(loading_message)

    # 地域データを取得してデータベースに保存
    region_data = fetch_json_data(AREA_URL)
    regions = region_data.get("offices", {})
    if regions:
        save_regions_to_db(regions)

    # ローディングメッセージを削除
    page.controls.remove(loading_message)

    # データベースから地域データを取得
    regions = get_regions_from_db()

    # 天気表示用コンテナ
    weather_display = ft.Column()

    # 地域選択用ドロップダウン
    dropdown = ft.Dropdown(
        hint_text="地域を選択してください",
        on_change=lambda e: display_weather(e.control.value, regions, weather_display, page)
    )

    for region_id, region_info in regions.items():
        dropdown.options.append(ft.dropdown.Option(region_id, region_info["name"]))

    # UIにコンポーネントを追加
    page.add(dropdown)
    page.add(weather_display)

# アプリケーションを実行
if __name__ == "__main__":
    setup_database()
    ft.app(target=main)
