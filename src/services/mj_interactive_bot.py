import os
import time
import shutil
import psutil
import random
import logging
import asyncio
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal

# Webscraping discord
from selenium import webdriver
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

# Discord bot
import discord
from discord.ext import commands
from discord.message import Message

from src.core.settings import Settings
from src.core.logger import init_logger

init_logger(Settings())
logger = logging.getLogger(__name__)

def User():
    ua = UserAgent()
    return ua.random

class MidJourneyInteractive:
    def __init__(self, settings: Settings, browser_settings: Dict[str, Any], directory_path: str) -> None:
        
        self.current_img_prompt_status: Literal['start', 'generating', 'selecting','downloading', 'success', 'failed'] = 'start'
        self.last_status_update_time: float | int = datetime.timestamp(datetime.now())

        self.settings = settings
        self.secrets = self.settings.DISCORD_SECRET_CODES
        self.browser_settings = browser_settings
        self.directory_path = directory_path

        # Configure undetected-chromedriver options
        self.options = webdriver.ChromeOptions()
        
        # Configure browser options
        if self.browser_settings.get("headless", False):
            self.options.add_argument("--headless")
        
        # Add stealth mode arguments
        for arg in self.browser_settings.get("args", []):
            self.options.add_argument(arg)
        
        # Set window size with random variations to appear more human-like
        width = random.randint(1050, 1200)
        height = random.randint(800, 900)
        self.options.add_argument(f"--window-size={width},{height}")
        
        # Set custom user agent
        self.options.add_argument(f"user-agent={User()}")

        self.token = settings.MJ_BOT_KEY
        self.mj_bot_id = settings.MJ_BOT_ID
        self.target_guild_id = settings.DISCORD_GUILD_ID
        self.target_channel_id = settings.DISCORD_CHANNEL_ID
        self.discord_user_id = settings.DISCORD_USER_ID
        self.discord_email = settings.DISCORD_USER_EMAIL
        self.discord_password = settings.DISCORD_USER_PASSWORD

        self.current_prompt = None
        self.current_prompt_num = None

        
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        
        # Event handlers
        self.bot.event(self.on_message)
    
    def __enter__(self, version=135):
        # Initialize undetected-chromedriver
        self.driver = uc.Chrome(
            options=self.options,
            use_subprocess=True,
            version_main=version,
        )
        
        # Add cookies
        self._add_cookies()
        
        # Inject enhanced anti-detection scripts
        self._inject_anti_detection_script()
        
        return self
    
    def _inject_anti_detection_script(self):
        # Enhanced anti-detection script based on chromiumPreventions.js
        self.driver.execute_script("""
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => False,
            });
            
            // Override languages property
            Object.defineProperty(navigator, "languages", {
                get: function() {
                    return ["en-US", "en", "es"];
                }
            });
            
            // Override plugins property
            Object.defineProperty(navigator, "plugins", {
                get: () => {
                    // Create some fake plugins to make fingerprinting more difficult
                    const fakePlugins = [];
                    const pluginNames = [
                        "Chrome PDF Plugin", 
                        "Chrome PDF Viewer", 
                        "Native Client", 
                        "Shockwave Flash", 
                        "Microsoft Edge PDF Plugin"
                    ];
                    
                    // Add random number of plugins
                    const pluginCount = Math.floor(Math.random() * 3) + 2;
                    for (let i = 0; i < pluginCount; i++) {
                        const randomIndex = Math.floor(Math.random() * pluginNames.length);
                        fakePlugins.push(pluginNames[randomIndex]);
                    }
                    
                    return fakePlugins;
                },
            });
            
            // Override hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => {
                    return Math.floor(Math.random() * 8) + 2;
                }
            });
            
            // Override deviceMemory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => {
                    return Math.floor(Math.random() * 8) + 2;
                }
            });
            
            // Override userAgent to ensure consistency
            const userAgent = navigator.userAgent;
            Object.defineProperty(navigator, 'userAgent', {
                get: () => userAgent
            });
            
            // Override platform
            Object.defineProperty(navigator, 'platform', {
                get: () => {
                    const platforms = ['Win32', 'MacIntel', 'Linux x86_64'];
                    return platforms[Math.floor(Math.random() * platforms.length)];
                }
            });
            
            // Override connection property
            if (navigator.connection) {
                Object.defineProperty(navigator.connection, 'rtt', {
                    get: () => Math.floor(Math.random() * 100) + 50
                });
            }
            
            // Modify WebGL fingerprinting
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {
                    return "Intel Open Source Technology Center";
                }
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {
                    return "Mesa DRI Intel(R) Ivybridge Mobile";
                }
                return getParameter.apply(this, arguments);
            };
            
            // Override element dimensions to prevent detection
            const elementDescriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "offsetHeight");
            Object.defineProperty(HTMLDivElement.prototype, "offsetHeight", {
                ...elementDescriptor,
                get: function() {
                    if (this.id === "modernizr") {
                        return 1;
                    }
                    return elementDescriptor.get.apply(this);
                },
            });
            
            // Fix image dimensions for detection prevention
            ["height", "width"].forEach(property => {
                const imageDescriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, property);
                Object.defineProperty(HTMLImageElement.prototype, property, {
                    ...imageDescriptor,
                    get: function() {
                        // Return an arbitrary non-zero dimension if the image failed to load
                        if (this.complete && this.naturalHeight == 0) {
                            return 24;
                        }
                        // Otherwise, return the actual dimension
                        return imageDescriptor.get.apply(this);
                    },
                });
            });
            
            // Override permissions API if available
            if (navigator.permissions) {
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = function(parameters) {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({state: "granted"});
                    }
                    return originalQuery.apply(this, arguments);
                };
            }
            
            // Delete CDP-related properties
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // Override toString methods to prevent detection
            const originalFunction = Function.prototype.toString;
            Function.prototype.toString = function() {
                if (this === Function.prototype.toString) {
                    return originalFunction.call(originalFunction);
                }
                if (this === navigator.permissions.query) {
                    return "function query() { [native code] }";
                }
                return originalFunction.call(this);
            };
            
            // Override Chrome object if it exists
            if (window.chrome) {
                // Ensure chrome.runtime exists to prevent detection
                if (!window.chrome.runtime) {
                    window.chrome.runtime = {};
                }
                
                // Add sendMessage function
                window.chrome.runtime.sendMessage = function() {};
            }
            
            // Override Notification API
            window.Notification = {
                permission: 'default'
            };
        """)

    def _add_cookies(self):
        try:
            self.driver.get("https://discord.com/channels/@me")
        except Exception as e:
            print(f"Error connecting with proxy: {e}")
                
        # Add cookies after successful connection
        cookies: Optional[List[Dict[str, Any]]] = self.browser_settings.get("cookies", None)
        if cookies is None:
            print("No cookies found in browser settings.")
            return

        for cookie in cookies:
            if "discord" not in cookie["domain"]:
                print("Skipping cookie with non-discord domain \n")
                continue
            
            # Clean and validate sameSite attribute
            if "sameSite" in cookie:
                if cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                    cookie["sameSite"] = "None"  # Set default value
                    
            # Remove problematic attributes if present
            cookie_clean = {k: v for k, v in cookie.items() if k in [
                'name', 'value', 'domain', 'path', 'secure', 
                'httpOnly', 'expiry', 'sameSite'
            ]}
            
            try:
                self.driver.add_cookie(cookie_clean)
            except Exception as e:
                print(f"Failed to add cookie {cookie_clean.get('name')}: {e}")
            
        print(f"Added cookies: {len(cookies)}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting the context manager"""
        try:
            if self.driver:
                self.driver.close()
                self.driver.quit()
        except Exception as e:
            print(f"Error during driver cleanup: {e}")
        
    async def on_message(self, message: Message) -> None:

        conditions = [
            message.guild.id == self.target_guild_id,
            message.channel.id == self.target_channel_id,
            message.author.id == self.mj_bot_id,
            message.content.__contains__(self.current_prompt),
            message.content.__contains__(str(self.discord_user_id))
        ]
        if False in conditions:
            logger.error(f'[{message.guild.name}({message.guild.id})] {message.channel.name}({message.channel.id}) {message.author} ({message.author.id})')
            logger.error(str(conditions))
            return None
        
        if message.content.endswith("(fast)"):
            time.sleep(10)
            self.select_upscale_img(1)

        elif message.content.__contains__("Image #1"):
            time.sleep(1)
            self.update_prompt_status("downloading")
            img_url = message.attachments[0].url
            self.download_image(url=img_url)
            self.update_prompt_status("success")

    
    async def close(self):
        self.driver.quit()
        await self.bot.close()
    
    def download_image(self, url: str):
        file_path = os.path.join(self.directory_path, f'{self.current_prompt_num}.png')

        img_data = requests.get(url).content
        with open(file_path, 'wb') as handler:
            handler.write(img_data)
        
        logger.error(f"Image #{self.current_prompt_num} downloaded.")

    def find_element_with_inner_text(self, tag, attribute, attribute_value, inner_text):
        xpath = f"//{tag}[@{attribute}='{attribute_value}']//div[text()='{inner_text}']"
        try:
            web_element = self.driver.find_element(By.XPATH, xpath)
            return web_element
        except Exception as ex:
            logger.warning(f"Method: MidJourneyInteractive.find_element_with_inner_text. Error: {ex}")
            return None
    
    def find_send_message(self):
        xpath = '//button[@aria-label="Send Message"]'
        try:
            web_element = self.driver.find_element(By.XPATH, xpath)
            return web_element
        except Exception as ex:
            logger.warning(f"Method: MidJourneyInteractive.find_send_message. Error: {ex}")
            return None
    
    def select_upscale_img(self, img_select: int):
        try:
            self.driver.find_elements(
                By.XPATH,
                f"//button[@role='button']//div//div//div[text()='U{img_select}']"
            )[-1].click()
        except Exception as ex:
            logger.error(f"Method: MidJourneyInteractive.select_upscale_img. Error: {ex}")

    def update_prompt_status(self, status: Literal["generating", "downloading", "success", "failed"]) -> None:
        self.current_img_prompt_status = status
        self.last_status_update_time: float | int = datetime.timestamp(datetime.now())

    async def login_discord_as_user(self) -> None:
        self.driver.find_element(By.CSS_SELECTOR, "[type=button]").click()
        try:
            time.sleep(10)
            if not "redirect_to=%2F" in self.driver.current_url:
                return None

            email = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[name=email]")
                )
            )
            password = self.driver.find_element(By.CSS_SELECTOR, "[name=password]")
            email.send_keys(self.discord_email)
            password.send_keys(self.discord_password)
            self.driver.find_element(By.CSS_SELECTOR, "[type=submit]").click()

            time.sleep(10)

            autenticate = self.find_element_with_inner_text(
                tag="button",
                attribute="type",
                attribute_value="button",
                inner_text="Autenticar con código de respaldo"
            )
            if autenticate is None:
                self.find_element_with_inner_text(
                    tag="button",
                    attribute="type",
                    attribute_value="button",
                    inner_text="Verificar de otra forma"
                ).click()
                time.sleep(5)

                self.find_element_with_inner_text(
                    tag="div",
                    attribute="role",
                    attribute_value="button",
                    inner_text="Utilizar un código de respaldo"
                ).click()
            else:
                autenticate.click()

            code_input = self.driver.find_element(By.TAG_NAME, "input")
            code_input.send_keys(self.secrets.pop(0))
            self.driver.find_element(By.CSS_SELECTOR, "[type=submit]").click()
            time.sleep(15)

        except Exception as ex:
            logger.error(f"Method: MidJourneyInteractive.login_discord_as_user. Error: {ex}")
            await self.close()


    async def send_mj_message_as_user(self, message: str):
        self.driver.get(f"https://discord.com/channels/{self.target_guild_id}/{self.target_channel_id}")
        try:
            time.sleep(10)
            continue_onweb = self.find_element_with_inner_text(
                tag="button",
                attribute="type",
                attribute_value="button",
                inner_text="Continuar en navegador"
            )
            if continue_onweb is None:
                continue_onweb = self.find_element_with_inner_text(
                    tag="button",
                    attribute="type",
                    attribute_value="button",
                    inner_text="Continuar en el navegador"
                )

            if continue_onweb is not None:
                continue_onweb.click()
                time.sleep(5)

            if "redirect_to=%2F" in self.driver.current_url:
                await self.login_discord_as_user()
            
            textbox = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@role="textbox"]')
                )  # wait until loaded
            )

        except Exception as ex:
            logger.error(f"Method: MidJourneyInteractive.send_mj_message_as_user. Error: {ex}")
            await self.close()
            return
        
        send_message = self.find_send_message()
        if message.startswith("/imagine"):
            textbox.send_keys("/imagine")
            time.sleep(3)
            textbox.send_keys(Keys.SPACE)
            textbox.send_keys(message.replace("/imagine ", ""))

            if send_message is None:
                textbox.send_keys(Keys.ENTER)
            else:
                send_message.click()
        else:
            textbox.send_keys(message)
            if message.startswith('/'):
                time.sleep(1)
            
            if send_message is None:
                textbox.send_keys(Keys.ENTER)
            else:
                send_message.click()
        
        
    async def run(self):
        await self.bot.start(token=self.token)

    async def proccess_img_prompt(self, img_prompt: str, img_prompt_num: int) -> bool:
        try:
            self.current_prompt = img_prompt
            self.current_prompt_num = img_prompt_num

            await self.send_mj_message_as_user(message=f"/imagine {img_prompt}")
            self.update_prompt_status('generating')

            while True:
                await asyncio.sleep(15)
                logger.info(f"Checking for image generation status. Current status: {self.current_img_prompt_status}...")

                if self.current_img_prompt_status == 'success':
                    logger.info("Image generation completed successfully.")
                    return True
                
                elif self.current_img_prompt_status == 'failed':
                    logger.error("Image generation failed.")
                    raise Exception("Image generation failed.")
                
                elif self.last_status_update_time + 90 < datetime.timestamp(datetime.now()):
                    logger.error("Image generation timed out.")
                    self.update_prompt_status('failed')
                    raise Exception("Image generation timed out.")
            
        except Exception as ex:
            logger.error(f"Method: MidJourneyInteractive.proccess_img_prompt. Error: {ex}")
            return False
