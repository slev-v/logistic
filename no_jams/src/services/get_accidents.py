import requests
import json
import re

from datetime import datetime


def from_api_to_data(data):
    if data["type"] == "Дорожные работы":
        data["type"] = "roadwork"
    elif data["type"] == "ДТП":
        data["type"] = "accident"
    elif data["type"] == "Перекрытие движения":
        data["type"] = "clozure"
    else:
        data["type"] = "other"

    cur_time = datetime.now().strftime("%H:%M")

    report = {
        "incident_type": data["type"],
        "time": cur_time,
        "latitude": data["coordinates"][0],
        "longitude": data["coordinates"][1],
        "severity": "medium",
        "description": data["description"],
        "source": "api",
        "status": "new",
    }

    res = [data["id"], report]

    return res


def get_accidents(redis):
    # Текущий момент времени в нужном формате
    timestamp = datetime.now().strftime("%Y.%m.%d.%H.%M.%S")

    # Формируем URL с текущим таймштампом
    urls = [
        f"https://core-road-events-renderer.maps.yandex.net/1.1/tiles?l=trje&lang=ru_RU&x=2492&y=1475&z=12&scale=1&v={timestamp}&callback=x_2492_y_1475_z_12_l_trje__t",
        f"https://core-road-events-renderer.maps.yandex.net/1.1/tiles?l=trje&lang=ru_RU&x=312&y=184&z=9&scale=1&v={timestamp}&callback=x_312_y_184_z_9_l_trje__t",
        f"https://core-road-events-renderer.maps.yandex.net/1.1/tiles?l=trje&lang=ru_RU&x=310&y=184&z=9&scale=1&v={timestamp}&callback=x_310_y_184_z_9_l_trje__t",
        f"https://core-road-events-renderer.maps.yandex.net/1.1/tiles?l=trje&lang=ru_RU&x=311&y=184&z=9&scale=1&v={timestamp}&callback=x_311_y_184_z_9_l_trje__t",
    ]

    # Заголовки
    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en;q=0.9,ru;q=0.8,en-US;q=0.7",
        "dnt": "1",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }

    responses = []
    for url in urls:
        response = requests.get(url, headers=headers)
        responses.append(response)
        print(response.text)
    results = []
    results_schema = []

    for response in responses:
        if response.status_code == 200:
            data = re.sub(r"/\*\*/x_.*?\(", "", response.text).rstrip(");")

            try:
                parsed_data = json.loads(data)
                events = parsed_data["data"]["features"]

                event_list = [
                    {
                        "id": event["properties"]["HotspotMetaData"]["id"][1:],
                        "type": event["properties"]["hintContent"],
                        "description": event["properties"]["description"],
                        "coordinates": event["geometry"]["coordinates"],
                    }
                    for event in events
                ]

                for event in event_list:
                    results_schema.append(from_api_to_data(event))
                    if event["type"] == "Дорожные работы":
                        event["type"] = "roadwork"
                    elif event["type"] == "ДТП":
                        event["type"] = "accident"
                    elif event["type"] == "Перекрытие движения":
                        event["type"] = "clozure"
                    else:
                        event["type"] = "other"
                    results.append(event)
            except json.JSONDecodeError:
                print("Ошибка декодирования JSON")
            except KeyError:
                print("Ошибка ключа")
        else:
            print(f"Ошибка: {response.status_code}")
    return results_schema
