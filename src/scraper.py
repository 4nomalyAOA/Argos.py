import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import phonenumbers
from urllib.robotparser import RobotFileParser
import tools
from bs4 import Comment
import antiBotBypassing
import asyncio
import AI_analyzer
from tqdm import tqdm
from phonenumbers import geocoder, carrier
import random

def show_banner():
    """Showing the name and infos about the project"""
    banner = r"""--[[
         _                   _           _              _            _              _    _        _   
        / /\                /\ \        /\ \           /\ \         / /\           /\ \ /\ \     /\_\ 
       / /  \              /  \ \      /  \ \         /  \ \       / /  \         /  \ \\ \ \   / / / 
      / / /\ \            / /\ \ \    / /\ \_\       / /\ \ \     / / /\ \__     / /\ \ \\ \ \_/ / /  
     / / /\ \ \          / / /\ \_\  / / /\/_/      / / /\ \ \   / / /\ \___\   / / /\ \_\\ \___/ /   
    / / /  \ \ \        / / /_/ / / / / / ______   / / /  \ \_\  \ \ \ \/___/  / / /_/ / / \ \ \_/    
   / / /___/ /\ \      / / /__\/ / / / / /\_____\ / / /   / / /   \ \ \       / / /__\/ /   \ \ \     
  / / /_____/ /\ \    / / /_____/ / / /  \/____ // / /   / / /_    \ \ \     / / /_____/     \ \ \   
 / /_________/\ \ \  / / /\ \ \  / / /_____/ / // / /___/ / //_/\__/ / /_   / / /             \ \ \   
/ / /_       __\ \_\/ / /  \ \ \/ / /______\/ // / /____\/ / \ \/___/ //\_\/ / /               \ \_\  
\_\___\     /____/_/\/_/    \_\/\/___________/ \/_________/   \_____\/ \/_/\/_/                 \/_/ 
                                    Made by Anomaly404, from KernelPanic◊!
                        This was made by an inde dev in python 3.12.16 with Visual Studio Code   
     To report any bugs or if you want to work on this project, contact me with github or discord, @4nomaly_404
                                                                                            
--]]"""

    print("\033[92m" + banner + "\033[0m")
    
    
def extract_headings(soup):
    """Extracts all headings from H1 to H6 cleanly"""
    headings = {}
    for level in range(1, 7):
        tags = soup.find_all(f'h{level}') #Search for all types of headings with a f-string
        if tags:
            print(f"\n--- H{level} Headings ---")
            for tag in tags:
                print(f"- {tag.text.strip()}")
            headings[f"h{level}"] = [tag.text.strip() for tag in tags]
    return headings

def extract_para(soup):
    """Extracting all the paragraphs"""
    paragraphes = []
    pars = soup.find_all('p') #searching for paragraphs
    
    if pars: 
        for p in pars:
            para = p.get_text().strip() #getting the paragraph's text
            print(f"\n[+] Paragraph found: {para}")
            paragraphes.append(para) #adding the paragraph to the list
    else:
        print("\n[-] No paragraphs found")
    return paragraphes

def extract_lists(soup):
    """Extract all the lists"""
    lists = []
    raw_lists = soup.find_all(['li'])
    
    if raw_lists: #almost the same code as above, getting the paragraphs, their text and adding them to a list
        for li in raw_lists:
            txt = li.get_text().strip()
            if txt:
                print(f"\n[+] List found: {txt}")
                lists.append(txt)
    else:
        print("\n[-] No lists found")
    return lists
    

def extract_forms(soup):
    """Extracts forms and their corresponding input tags"""
    forms = soup.find_all('form')
    if not forms:
        print("\n[-] No forms found on this page.")
        return False
    
    forms_list = []
    
    for form in tqdm(forms, desc = "Searching for forms..."):
        action = form.get('action', 'No action attribute').strip()
        method = form.get('method', 'GET').strip() 
        tqdm.write(f"\n[+] Form found [Method: {method.upper()}, Action: {action}]")
        inputs_data = []
        inputs = form.find_all('input')
        for i in tqdm(inputs, desc = "Searching for inputs..."):
            input_type = i.get('type', 'text')
            input_name = i.get('name', 'N/A')
            tqdm.write(f"  - Input Tag -> Type: {input_type}, Name: {input_name}")
            inputs_data.append({ #moving the infos in a list
                "Input type": input_type,
                "Input name": input_name,
            })
        form_data = { #move the lists in a dictionairy
            "Action": action,
            "Method": method.upper(),
            "Inputs data": inputs_data
        }
        forms_list.append(form_data)
    return forms_list

def extract_contacts(text):
    """Extracts email addresses and phone numbers from the page"""
    #Yeah, I found this regex on the internet
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    emails_result = list(set(emails)) if emails else "None"
    tqdm.write(f"\n[+] Emails found: {emails_result}")
    
    contacts = {}
    
    phones = []
    
    seen_numbers = set()
    
    for match in tqdm(phonenumbers.PhoneNumberMatcher(text, region=None), desc = "Searching for phonenumbers"):
        #You should be able to detect almost all the types of phone numbers
        if phonenumbers.is_valid_number(match.number):
            
            formatted = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
            if formatted not in seen_numbers:
            
                num = phonenumbers.parse(formatted)
                seen_numbers.add(formatted)
            
                phone_info = {
                    'number': formatted,
                    'country': geocoder.description_for_number(num, "en"),
                    'operator': carrier.name_for_number(num, "en")
                }
            
                phones.append(phone_info)

    phones_result = phones if phones else "None"
    tqdm.write(f"\n[+] Phone numbers found: {phones_result}")
    
    contacts['emails'] = list(set(emails)) #putting all the emails and phonenumbers in this dictionairy
    contacts['phones_infos'] = phones
    
    return contacts

async def check_robots(scraper_tools, url):
    """Checks for robots.txt"""
    robots_url = urljoin(url, "/robots.txt") #Create the full url with the domain + the /robots.txt
    async with httpx.AsyncClient(proxy = scraper_tools.proxy_url, timeout=10) as client:
        try:
            res = await client.get(robots_url, timeout=5)
            if res.status_code == 200: #page found
                print(f"\n[+] robots.txt found at: {robots_url}")
                return robots_url
            else:
                print("\n[-] No robots.txt found for this website.")
                return None
        except Exception as e:
            print(f"\n[-] Failed to fetch robots.txt: {e}")
            return None 

async def check_sitemap(scraper_tools, url):
    """Check for sitemap.xml"""
    sitemap_url = urljoin(url, "/sitemap.xml")
    async with httpx.AsyncClient(proxy = scraper_tools.proxy_url, timeout=10) as client:
        try:
            res2 = await client.get(sitemap_url, timeout=5) #searching with the proxy
            if res2.status_code == 200:
                print(f"\n[+] sitemap.xml found at: {sitemap_url}")
                return sitemap_url #return the Url
            else:
                print("\n[-] No sitemap.xml found for this website.")
                return None
        except Exception as e:
                print(f"\n[-] Failed to fetch sitemap.xml: {e}")
                return None

async def process_robots(robots_url, scraper_tools):
    """Download the robot file"""
    user_agent = '*'
    rp = await scraper_tools.load_parser(robots_url)
    
    text_download = ""
    while text_download.lower() != 'y' and text_download.lower() != 'n':
        text_download = input("\n[?] Can I download the text from the robots.txt [y/N] ?")
    
        if text_download.lower() == "y": #Y or y are working with .lower()
            await scraper_tools.download_text("robots.txt", robots_url)
        elif text_download.lower() == "n":
            print("\n[-] No robot text")
        else:
            print("\n[-] No valid input entered")
        
    delay = rp.crawl_delay(user_agent) #Test with all the user agent
    print(f"\n[+] Reponse delay of the page: {delay}")

async def process_sitemaps(scraper_tools, sitemap_url):
    """Analyze the sitemap"""
    async with httpx.AsyncClient(proxy = scraper_tools.proxy_url, timeout=10) as client: #opening the browser
        try:
            response = await client.get(sitemap_url, timeout=10) #get the page with the proxy and the navigator
            response.raise_for_status()
        
        except Exception as e:
            print(f"\n[-] Failed to fetch sitemap: {e}")
            return None

        soup = BeautifulSoup(response.text, 'xml')
        urls = soup.find_all('loc')
        lastmod_elements = soup.find_all('lastmod')
        lastmod = [l.text.strip() for l in lastmod_elements if l.text]
        sitemap = soup.find_all('sitemap')
        #search for all the interesting infos on the sitemap
        if sitemap:
            print(f"\n[+] Others sitemaps found: {[s.text.strip() for s in sitemap]}")
        else:
            print(f"\n[-] No others sitemaps urls found")
        if lastmod:
            last_date = lastmod[0]
            
            print(f"\n[+] Last modification on this page: {lastmod}")
            print(f"\n[+] Found {len(lastmod)} lastmod entries (Latest updates: {last_date})")
            
        else:
            print("\n[-] No date of last modification found on this page")
        if urls:
            print(f"\n[+] URL(s) found on this page: {[loc.text.strip() for loc in urls]}") 
            return urls
        else:
            print("\n[-] No URLs found on this page")
            return []
    
def ask_url_limit(args):
    """Ask the limit of urls found to process"""
    if not args.depth:
        limit = input("\n[?] What's the number max of URL(s) from the sitemap that I can scrap ? (default:10):")
        limit = int(limit) if limit.strip().isdigit() else 10 #check if it's really a number and transform the input into a number
    else:
        limit = args.depth
        return limit
   
async def orchestrator(scraper_tools, sitemap_url, robots_url, visited_pages, queue, args):
    """Orchestrates all the others fonctions working with Robots.txt and sitemap.xml"""
    if robots_url:
        await process_robots(robots_url, scraper_tools)
    if sitemap_url:
        urls = await process_sitemaps(scraper_tools, sitemap_url)
        if urls:
            limit = ask_url_limit(args) #defines a limit so you don't scrap thousands of urls
            await test_url(scraper_tools, urls, robots_url, limit,  visited_pages, queue)

async def test_url(scraper_tools, urls, robots_url, limit, visited_pages, queue):
    """Test the url(s) found in the sitemap.xml"""
    if not robots_url:
            print("\n[-] No robots.txt — skipping permission check")
            return False
        
    added = 0    
    user_agent = '*' #all the user agents
    rp = await scraper_tools.load_parser(robots_url)
    url_list = [loc.text.strip() for loc in urls] #extracting every url text for every url tag found
    
    
    for i, url in enumerate(tqdm(url_list, desc = "Processing...", colour = 'green')):
        if added >= limit:
            tqdm.write(f"\n[-] Limit of {limit} URLs reached")
            break
        
        if url in visited_pages or url.startswith('javascript:'):
            continue
        
        autorisation = rp.can_fetch(user_agent, url)
        if autorisation:
            print(f"\n[+] We can fetch this URL: {url}")
            await queue.put(url)
            print("URL added to the queue") 
            added += 1
            
        else:
            print(f"\n[-] We can't fetch this URL: {url}")
        

def comments(soup):
    """Search for comments left by the dev"""
    comments_list = []
    comment_tags = soup.find_all(string = lambda text: isinstance(text, Comment))
    
    for comment in tqdm(comment_tags, desc = "Searching for comments..."): #inspect every part of the html to find a comment
        comment_text = str(comment).strip()
        if comment_text and "<" not in comment_text and len(comment_text) < 150:
            
            tqdm.write(f"\n[+] HTML comment found : {comment_text}")
            comments_list.append(comment_text)
            
        comment.extract()
    return comments_list

def find_URL(soup):
    """Search for URL(s) on the page"""
    urls_list = []
    for u in tqdm(soup.find_all('a'), desc = "Searching for URLs..."): #extracting href attribute from anchor tags
        href_pres = u.get('href') #extrating only the url
        if href_pres:
            urls_list.append(href_pres)
            tqdm.write(f"\n[+] URLs on the page: {href_pres}")
    return urls_list

async def test2_url(scraper_tools, robots_url, urls_list, limit, domain, visited_pages, queue):
    """Another version of test_url but for the urls found on the page"""
    if not robots_url or not urls_list:
            print("\n[-] No robots.txt — skipping permission check or no URL(s) found on the page")
            return False
    added = 0
    user_agent = '*'
    rp = await scraper_tools.load_parser(robots_url)
    
    for i, url in enumerate(tqdm(urls_list, desc = "Processing...", colour = "green")):
        if added >= limit: 
            tqdm.write(f"\n[-] Limit of {limit} URLs reached")
            break
        
        urll = urljoin(domain, url)
        
        if urll in visited_pages or urll.startswith('javascript:'):
            continue
        
        autorisation = rp.can_fetch(user_agent, urll) #Try to fetch the the url
        if autorisation:
            print(f"\n[+] We can fetch this URL: {urll}")
            await queue.put(urll)
            print("\n[+] URL added to the queue") 
            added += 1
            
        else:
            print(f"\n[-] We can't fetch this URL: {urll}")
            

def orchestrator_2():
    """To orchestrate the two others functions"""
    dicti = tools.find_file()
    if dicti:
        proxy = use_proxy(dicti) #dicti is the dictionairy containing all the informations to connect to the proxy
        return proxy
    else:
        return None

def use_proxy(dicti):
    """The user can use his own proxy"""
    protocol = dicti['protocol']
    address = dicti['address']
    port = dicti['port']
    username = dicti['username']
    passwd = dicti['password']
    
    if username and passwd:
        proxy_url = f"{protocol}://{username}:{passwd}@{address}:{port}" #create the Url
        return proxy_url
    else:
        proxy_url = f"{protocol}://{address}:{port}"
        return proxy_url

async def process_url(url, scraper_tools, proxy_url, tor_process, visited_pages, queue, args):
    """Orchestrates the scraping pipeline for one URL ◊"""
    print(f"\n==================== ANALYZING ◊: {url} ====================")
    
    if url in visited_pages:
        print("\n[-] Page already visited")
        return
    
    #--Initialising the proxy part--
    if not tor_process:
        await antiBotBypassing.change_ip()
    await asyncio.sleep(10)

    #--Getting the content--
    infos = await antiBotBypassing.localizer(proxy_url) #Get the infos about the IP
    soup = await antiBotBypassing.camoufox_bypassing(url, infos, proxy_url)

    if not soup:
        print(f"\n[-] Error, could not reach {url}")
        return

    text_content = soup.get_text()

    title = soup.find('title')
    print("\n[+] Page Title:", title.text.strip() if title else "No title found")
    

    #--Creating the data dictionairy and adding all the infos--
    
    data = {} #This is THE dictionairy containing all the infos
    data["Url"] = url
    
    data["Title"] = title.text.strip() if title else None
    data["Headings"] = extract_headings(soup)
    
    meta = soup.find('meta', attrs={'name': 'description'})
    content = meta.get('content') if meta else None
    data["Meta description"] = content
    
    data["Paragraphs"] = extract_para(soup)
    data["Lists"] = extract_lists(soup)
    
    
    images = soup.find_all('img')
    download_choice = ""
    
    #--Asking for the downloading choice--
    if images:
        if not args.images:
            while download_choice.lower() != 'y' and download_choice.lower() != 'n':
                download_choice = input("\n[?] Do you want to download the images from this page? [y/N]: ")
            
                if download_choice.lower() == 'y':
                    folder_name = input("\n[?] Enter directory name to save images: ")
                    await scraper_tools.download_images(folder_name, images, url)
                
                elif download_choice.lower() == 'n':
                    data['Images'] = tools.display_images_src(images)
                
                else:
                    print("\n[-] No valid input entered")
                    
        else:
            folder_name = args.images
            await scraper_tools.download_images(folder_name, images, url)
            

    data["Forms"] = extract_forms(soup)
    data["Contacts"] = extract_contacts(text_content)

    robots_url = await check_robots(scraper_tools, url)
    data["Robots.txt presence"] = bool(robots_url) #Get just True or False
    
    if robots_url:
        data["Robots.txt link"] = robots_url
        
    sitemap_url = await check_sitemap(scraper_tools, url)
    
    data["Sitemap.xml presence"] = bool(sitemap_url)
    if sitemap_url:
        data["Sitemap.xml link"] = sitemap_url

    await orchestrator(scraper_tools, sitemap_url, robots_url, visited_pages, queue, args)
    
    if not args.depth:
        await test2_url(scraper_tools, robots_url, find_URL(soup), ask_url_limit(), url, visited_pages, queue)
    else:
        await test2_url(scraper_tools, robots_url, find_URL(soup), args.depth, url, visited_pages, queue)

    data["Comments"] = comments(soup)

    data["Site type"] = tools.site_type_detector2000(soup)

    response_h1 = await scraper_tools.get_headers(url)
    
    if response_h1:
        data["Server infos"] = tools.analyze_server_info(response_h1)
        data["Security headers"] = tools.analyze_security_headers(response_h1)
    
    if not args.json:
        name = input("\n[?] What name do you want to give the JSON file?")
    else:
        name = args.json
    
    #--Exporting the data--

    tools.export_JSON(data, name) #export the JSON with the database: data
    
    #--Asking if the user want to export the data to an AI--
    ai = ""
    if not args.ai_model:
        while ai.lower() != 'n' and ai.lower() != 'y':
            ai = input("\n[?] Do you want to export the data to an AI using your API ? [y/N]")
    
            if ai.lower() == 'y':
                provider = AI_analyzer.ask_ai_choice()
        
                if provider:
                    content = await AI_analyzer.send_ai(data, provider)
                    AI_analyzer.content_saver(content)

            elif ai.lower() == 'n':
                continue
        
            else:
                print("\n[-] No valid input entered")
    
    else:
        provider = args.ai_model
        content = await AI_analyzer.send_ai(data, provider)
        AI_analyzer.content_saver(content)
            
    visited_pages.add(url)
            

async def main(args):
    """The main thing, making everything work"""
    show_banner()
    tor_process = None
    
    try:
        queue = asyncio.Queue()
        visited_pages = set()
        
        if not args.url:
            raw_urls = input("\n[?] Enter one or multiple URLs separated by commas: ")
            urls = set([u.strip() for u in raw_urls.split(',') if u.strip()]) #The list of urls
            
            for url in tqdm(urls, desc="Adding the Url(s) to the queue..."):
                queue.put_nowait(url)
        else:
            urls = set([u.strip() for u in args.url.split(',') if u.strip()])
            for url in tqdm(urls, desc="Adding the Url(s) to the queue..."):
                queue.put_nowait(url)
                    
        tor_process = None
        proxy_url = "socks5h://127.0.0.1:9050" #The default value of the proxy 
    
        if not args.tor or not args.proxy:
            tor_bool = input("\n[?] Do you want to use your own proxy or the tor proxy ? [Y/Tor]")
            
            if tor_bool.lower() == 'y':
                proxy_url = orchestrator_2()
                
            elif tor_bool.lower() == 'tor':
                tor_process = antiBotBypassing.tor_proxy() #Initiating the proxy
                
            else:
                print("\n[-] Error, no valid option entered, Tor is going to be used...")
                tor_process = antiBotBypassing.tor_proxy()
    
            if proxy_url is None:
                tor_process = antiBotBypassing.tor_proxy()
                proxy_url = "socks5h://127.0.0.1:9050"
        
        try: 
            scraper_tools = tools.ScrapingTools(proxy_port="9050")
            
            bar = tqdm(desc = "Global progression", colour = "green")

            while not queue.empty():
                url = await queue.get()
                await process_url(url, scraper_tools, proxy_url, tor_process, visited_pages, queue)
                tqdm.write("\n[+] Waiting some seconds before next URL")
                
                queue.task_done() #remove the task
                
                bar.update(1)
                
                await asyncio.sleep(random.uniform(4, 9))
            
            bar.close()
            
        except KeyboardInterrupt:
            print("\n[-] User stopped programm with Control + C")
        except SystemExit:  
            print("\n[-] Shortcut detected, exiting the programm...")
        finally:
            if tor_process != None:
                tor_process.kill()
            print("\n[+] Task finished")       
        return tor_process
    finally:
        if tor_process:
            tor_process.kill()
    
    
if __name__ == "__main__":
    asyncio.run(main())

