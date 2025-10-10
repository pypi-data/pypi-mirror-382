import asyncio
import base64
import re
from typing import Optional, Tuple
import httpx
from playwright.async_api import Page, Response


class YandexCaptchaSolver:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_base_url = "https://api.sctg.xyz"

    async def solve(self, page: Page) -> bool:
        if not (page.url.startswith("https://yandex.ru/showcaptcha") or page.url.startswith("https://yandex.by/showcaptcha")):
            return True

        cached_body_1 = None
        cached_body_2 = None

        for attempt in range(3):
            try:
                is_retry = attempt > 0
                success, new_body_1, new_body_2 = await self._solve_captcha_once(page, is_retry, cached_body_1, cached_body_2)

                if success:
                    return True

                cached_body_1 = new_body_1
                cached_body_2 = new_body_2

                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error: {e}")

        return False

    async def _solve_captcha_once(self, page: Page, is_retry: bool = False, cached_body_1: Optional[str] = None, cached_body_2: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        if cached_body_1 and cached_body_2:
            body_1, body_2 = cached_body_1, cached_body_2
            auto_solved = False
        else:
            body_1, body_2, auto_solved = await self._capture_captcha_images(page, is_retry)

        if auto_solved:
            return True, None, None

        if not body_1 or not body_2:
            return False, None, None

        task_id = await self._submit_captcha(body_1, body_2)

        if not task_id:
            return False, None, None

        coordinates = await self._get_captcha_solution(task_id)

        if not coordinates:
            return False, None, None

        is_solved, new_body_1, new_body_2 = await self._click_coordinates(page, coordinates)

        return is_solved, new_body_1, new_body_2

    async def _capture_captcha_images(self, page: Page, is_retry: bool = False) -> Tuple[Optional[str], Optional[str], bool]:
        body_1 = None
        body_2 = None
        auto_solved = False

        async def handle_response(response: Response):
            nonlocal body_1, body_2

            url = response.url

            if "ext.captcha.yandex.net/image" in url and "data=img" in url:
                body = await response.body()
                body_1 = base64.b64encode(body).decode('utf-8')

            elif "ext.captcha.yandex.net/image" in url and "data=task" in url:
                body = await response.body()
                body_2 = base64.b64encode(body).decode('utf-8')

        page.on("response", handle_response)

        if not is_retry:
            button = page.locator('input[id="js-button"]')
            await button.click()

        for _ in range(40):
            await asyncio.sleep(1)

            if not (page.url.startswith("https://yandex.ru/showcaptcha") or page.url.startswith("https://yandex.by/showcaptcha")):
                page.remove_listener("response", handle_response)
                auto_solved = True
                return None, None, auto_solved

            if body_1 and body_2:
                break

        page.remove_listener("response", handle_response)

        return body_1, body_2, auto_solved

    async def _submit_captcha(self, body_1: str, body_2: str) -> Optional[str]:
        url = f"{self.api_base_url}/in.php"

        payload = {
            "key": self.api_token,
            "method": "yandeximg",
            "body_2": body_2,
            "body_1": body_1
        }

        headers = {"content-type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers, timeout=30)
            result = response.text

            if result.startswith("OK|"):
                task_id = result.split("|")[1]
                return task_id
            else:
                return None

    async def _get_captcha_solution(self, task_id: str) -> Optional[list]:
        url = f"{self.api_base_url}/res.php"
        params = {
            "key": self.api_token,
            "id": task_id
        }

        for _ in range(15):
            await asyncio.sleep(1)

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30)
                result = response.text

                if result.startswith("OK|"):
                    coordinates_str = result.split("|")[1]
                    coordinates = self._parse_coordinates(coordinates_str)
                    return coordinates

                elif result == "CAPCHA_NOT_READY":
                    continue

                else:
                    return None

        return None

    def _parse_coordinates(self, coords_str: str) -> list:
        pattern = r'x=(\d+),y=(\d+)'
        matches = re.findall(pattern, coords_str)

        coordinates = []
        for x, y in matches:
            coordinates.append({"x": int(x), "y": int(y)})

        return coordinates

    async def _click_coordinates(self, page: Page, coordinates: list) -> Tuple[bool, Optional[str], Optional[str]]:
        captcha_element = page.locator('div[class="AdvancedCaptcha-View"]')

        box = await captcha_element.bounding_box()
        if not box:
            return False, None, None

        for coord in coordinates:
            x = box['x'] + coord['x']
            y = box['y'] + coord['y']

            await page.mouse.click(x, y)
            await asyncio.sleep(0.5)

        captcha_solved = False
        new_body_1 = None
        new_body_2 = None

        async def handle_response(response: Response):
            nonlocal new_body_1, new_body_2
            url = response.url

            if "ext.captcha.yandex.net/image" in url and "data=img" in url:
                body = await response.body()
                new_body_1 = base64.b64encode(body).decode('utf-8')

            elif "ext.captcha.yandex.net/image" in url and "data=task" in url:
                body = await response.body()
                new_body_2 = base64.b64encode(body).decode('utf-8')

        page.on("response", handle_response)

        submit_button = page.locator('div[class="CaptchaButton-ProgressWrapper"]')
        await submit_button.click()

        for _ in range(50):
            await asyncio.sleep(0.1)

            if not (page.url.startswith("https://yandex.ru/showcaptcha") or page.url.startswith("https://yandex.by/showcaptcha")):
                captcha_solved = True
                break

            if new_body_1 and new_body_2:
                break

        page.remove_listener("response", handle_response)

        return captcha_solved, new_body_1, new_body_2
