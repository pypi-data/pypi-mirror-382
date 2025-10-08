import httpx
from mcp.server.fastmcp import FastMCP
import argparse

mcp = FastMCP("WeatherServer")

API_KEY = None

@mcp.tool()
async def get_weather(city: str) -> str:
    """
    查询天气函数，根据输入的城市的英文名称，查询对应城市天气
    :param city: 城市的英文名称，例如：beijing, shanghai, suzhou
    :return: 城市天气
    """
    if API_KEY is None:
        return "API key is not set"

    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "q": city,
        "key": API_KEY,
        "lang": "zh"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            city = data.get('location', {}).get('name', 'Unknown')
            province = data.get('location', {}).get('region', '')
            country = data.get('location', {}).get('country', '')
            temp = data.get('current', {}).get('temp_c', '')
            humidity = data.get('current', {}).get('humidity', '')
            wind_seed = data.get('current', {}).get('wind_kph', '')
            weather = data.get('current', {}).get('condition', {}).get('text', '')
            return (
                f"{city}, {province}, {country}\n"
                f"温度： {temp}\n"
                f"湿度： {humidity}%\n"
                f"风速： {wind_seed}km/h\n"
                f"天气： {weather}\n"
            )
        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Request error occurred: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Weather Server")
    parser.add_argument("--api_key", type=str, required=True, help="Your weather API key")
    args = parser.parse_args()
    global API_KEY
    API_KEY = args.api_key
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()