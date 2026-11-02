from bs4 import BeautifulSoup
import stem.process
from stem.control import Controller
from stem.control import Signal
import aioipapi
from babel import Locale
import httpx
from camoufox.async_api import AsyncCamoufox as camoufox
import re
from tqdm import tqdm
import os
import random
import asyncio

def tor_proxy():
    """Creating a Tor proxy so anti-bot programms don't spot your ip as sus"""
    config = {
        "SocksPort": "9050", #port for the proxy
        "ControlPort": "9051",  #port for the control of the proxy
        "CookieAuthentication": "0"
    }
    try:
        
            tor_process = stem.process.launch_tor_with_config(config, take_ownership=True)
            print("\n[+] Tor connected to network") #Hopefully
            return tor_process
    except Exception as e:
        print(f"\n[-] Error during initializing the process: {e}")

async def localizer(proxy_url):
    """Getting some informations so the navigation context of navigation makes sense with the location of the IP"""
    proxy = proxy_url
    infos = {'locale': 'en_US', 'timezone': 'UTC'}
    ip = None
    country_code = None
    
    async with httpx.AsyncClient(proxy = proxy, timeout=10) as client:
        try :
            response = await client.get('https://api.ipify.org') #Getting the IP
            ip = response.text.strip()
        except Exception as e:
            print(f"\n[-] Error during the process of trying to get Tor's ip: {e}")

    if ip:
        try:
            ip_location = await aioipapi.location(ip) #Getting the location
            country_code = ip_location.get('countryCode')
            infos['country'] = ip_location.get('country')
            infos['city'] = ip_location.get('city')
        except Exception as e:
            print(f"\n[-] Error getting IP location: {e}")


    if country_code:
        local = Locale.parse(f"und_{country_code}")  
        lang = local.language #Getting the main language of the country
        locale = f"{lang}-{country_code}"
        infos['locale'] = locale 
    else:
        locale = f"en_US"
        infos['locale'] = locale 
    return infos


async def camoufox_bypassing(url, infos, proxy_url):
    """Create a navigator so anti-bots systems don't spot you"""
    
    storage_file = "session.json"
    storage_arg = storage_file if os.path.exists(storage_file) else None
    
    playwright_proxy = proxy_url
    if proxy_url and proxy_url.startswith("socks5h://"):
        playwright_proxy = proxy_url.replace("socks5h://", "socks5://")
            
    context_options = { #context of navigation
        "viewport": {"width": 1920, "height": 1080}, 
        "locale": infos['locale'],
        "timezone_id": infos['timezone'],
        "proxy": {"server": playwright_proxy} if playwright_proxy else None,
        "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9,en;q=0.8"
            }
    }

        
    if storage_arg:
        context_options['storage_state'] = storage_arg
        
    async with camoufox(headless = True) as browser:    
        context = await browser.new_context(**context_options)
        page = await context.new_page()
        soup = None
        try:
            await page.goto(url, timeout=30000)
            await asyncio.sleep(random.uniform(2, 5))
            if await find_captcha(page):
                #The following code is just used to open the browser so the user solves the the captcha, then the browser is re-opened in invisible mode 
                await browser.close()
                
                async with camoufox(headless = False) as browser:
                    context = await browser.new_context(**context_options) #re-creating the context
                    
                    page = await context.new_page()
                    await page.goto(url, timeout = 30000)
                    
                    input("\n[+] Solve the CAPTCHA, when you have finished, just press enter")
                    await asyncio.sleep(random.uniform(2, 5))
                    await page.wait_for_load_state('load', timeout = 10000)

                    html_content = await page.content()
                    title = await page.title()
                    
                    print(f"\n[+] Page title: {title}")
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    await context.storage_state(path=storage_file) #saving the data
                    
            else:                
                html_content = await page.content()
                title = await page.title()
            
                print(f"\n[+] Page title: {title}")
                soup = BeautifulSoup(html_content, 'html.parser')
        
        except Exception as e:
            print(f"\n[-] Error during getting the HTML content: {e}")
            
        finally:
            try: 
                await browser.close()
            except:
                pass
        return soup

    
async def change_ip():
    """Requests a new Tor circuit to rotate the exit IP"""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate() 
            controller.signal(Signal.NEWNYM) 
            print("\n[+] IP switched successfully (New Tor Circuit)")
    except Exception as e:
        print(f"\n[-] Error, couldn't change the IP: {e}")


async def find_captcha(page):
    """Search for captcha after the page loading"""
    CAPTCHA_CONFIG = {
        "BLOCKED_TITLES": [
            "Just a moment",
            "Attention Required",
            "Access Denied"
        ],
        "CHALLENGE_MARKERS": [
            "cf-browser-verification",
            "challenge-running"
        ],
        "IFRAME_KEYWORDS": [
            "hcaptcha",
            "recaptcha"
        ]
    }
    
    html_content = await page.content()
    
    for patterns in CAPTCHA_CONFIG.values():
           for pattern in patterns:
               if re.search(pattern, str(html_content), re.IGNORECASE): #check for matching patterns
                   print("\n[+] Captcha probably found")
                   return True
    return False
      