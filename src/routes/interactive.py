import logging

from fastapi import APIRouter, Depends, status

from src.core.settings import Settings
from src.models.prompts import ImagesPrompts
from src.utils.decryption import decrypt_data
from src.models.inputs import InteractiveInput
from src.services.mj_interactive_bot import MidJourneyInteractive

logger = logging.getLogger(__name__)

interactive_router = APIRouter(tags=["interactive"], prefix="/interactive")

@interactive_router.get("/generate_images", status_code=status.HTTP_200_OK)
async def generate_images(
    body: InteractiveInput
):
    
    cookies = None
    if body.encrypted_cookies is not None and body.key is not None:
        cookies = decrypt_data(body.encrypted_cookies, body.key)

    browser_settings = {
        "cookies": cookies,
        "args": [
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-dev-shm-usage",
            "--disable-features=TranslateUI,IsolateOrigins,site-per-process",
            "--disable-hang-monitor",
            "--disable-ipc-flooding-protection",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-sync",
            "--disable-gpu",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--no-sandbox",
            "--no-first-run",
            "--no-default-browser-check",
            "--start-maximized",
            "--disable-site-isolation-trials",
            "--allow-running-insecure-content",
            "--disable-infobars",
            "--ignore-certificate-errors",
            "--enable-features=NetworkService"
        ]
    }

    with MidJourneyInteractive(
        settings=Settings(),
        browser_settings=browser_settings,
        directory_name=body.prompts_data.directory_name
    ) as mj_interactive:
        for img_prompt in body.prompts_data.img_prompts:
            await mj_interactive.proccess_img_prompt(img_prompt=img_prompt.prompt, img_prompt_num=img_prompt.prompt_num)

    return "IMAGES GENERATED AND SAVED ON DIRECTORY"