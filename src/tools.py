import os
import httpx
import json
import re
from urllib.parse import urljoin
from tqdm import tqdm
from urllib.robotparser import RobotFileParser

class ScrapingTools:
    """Useful class containing the proxy stuff and others utilities"""
    def __init__(self, proxy_port="9050"):
       self.proxy_url = f"socks5h://127.0.0.1:{proxy_port}"

    async def download_images(self, directory_name, img_tags, base_url):
        """Downloads all images found on the page"""
        async with httpx.AsyncClient(proxy = self.proxy_url, timeout=10) as client:
            if not os.path.exists(directory_name):
                os.makedirs(directory_name)
            else:
                print("\n[-] Directory already exists.")

            for i, img in enumerate(tqdm(img_tags, desc = "Downloading the images...")):
                #saving image by image in the directory
                src = img.get('src')
                if not src:
                    continue

                img_url = urljoin(base_url, src) 
                try:
                    res = await client.get(img_url, timeout=5)
                    file_name = img_url.split("/")[-1].split("?")[0] or f"image_{i}.jpg" #cleaning
                    path = os.path.join(directory_name, file_name)
                    with open(path, "wb") as f:
                        f.write(res.content)
                    tqdm.write(f"\n[+] Image saved: {file_name}")
                except Exception as e:
                    tqdm.write(f"\n[-] Could not download {img_url}: {e}")

    async def load_parser(self, robots_url):
        """Rp.read() tries to get the content without using the proxy, that's why this function exists"""
        rp = RobotFileParser()
        rp.set_url(robots_url)
        async with httpx.AsyncClient(proxy = self.proxy_url, timeout = 10) as client: #request with httpx and the proxy
            try:
                robots = await client.get(robots_url)
                if robots.status_code == 200:
                    rp.parse(robots.text.splitlines()) 
            except Exception as e:
                print(f"\n[-] Error, failed to load the robots.txt: {e}")
        return rp


    async def download_text(self, output, url):
        """Downloading the file"""
        async with httpx.AsyncClient(proxy = self.proxy_url, timeout=10) as client:
            try:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    with open(output, 'w', encoding='utf-8') as f: #open and create the file
                        f.write(response.text)
                    print("\n[+] Text saved in:", output)
                    return True
                else:
                    print(f"\n[-] Impossible to save the text from {url} (HTTP status : {response.status_code} ")
                    return False
            except httpx.RequestException as e:
                print(f"\n[-] Error in the downloading {url} : {e}")
                return False
            
    async def get_headers(self, url):
        """Get the headers of the HTTP request"""
        async with httpx.AsyncClient(proxy = self.proxy_url, timeout=10) as client:
            try:
                response = await client.get(url, timeout = 5)
                if response.status_code == 200: 
                    response_h = response.headers
                    if response_h:
                        print("\n[+] Headers found") 
                        return response_h #headers found, returning them
                    else:
                        print("No headers found")
            except Exception as e:
                print(f"Error in downloading {url}: {e}")
                return False    


def display_images_src(img_tags):
    """Displays the source URLs of all images on the page."""
    imgs_list = []
    for img in tqdm(img_tags, desc = "Displaying the image's source..."):
        src = img.get('src')
        if src and not src.startswith('data:'): 
            tqdm.write(f"- Image: {src}") #displaying the image source
            imgs_list.append(src) #add the image to the list
    return imgs_list
    
def analyze_server_info(response_h):
    """Analyze all the data from the headers that can be useful"""
    #Not going to comment this code, it's pretty easy
    server_infos = {}
    server = response_h.get('Server')
    
    if server:
        print(f"\n[+] Server of the web page : {server}")
        server_infos['Server'] = server
    else:
        print("\n[-] No server found in the header")
        server_infos['Server'] = ["No server found"]
        
    powered_by = response_h.get('X-Powered-By')
    if powered_by:
        print(f"\n[+] This server is powered by : {powered_by}")
        server_infos['Powered by'] = [f"{powered_by}"]
    else:
        print("\n[-] No services found")
        server_infos['Powered by'] = ["None"]
        
    forwarded = response_h.get('X-Forwarded-For')
    if forwarded:
        print("\n[+] Forwarded")
        server_infos['Forwarded'] = [f"{forwarded}"]
    else:
        print("\n[-] Not forwarded")
        server_infos['Forwarded'] = ["None"]
        
    ETag = response_h.get('ETag')
    if ETag:
        print("\n[+] ETag found")
        server_infos['Etag'] = [f"{ETag}"]
    else:
        print("\n[-] No ETag found")
        server_infos['Etag'] = ["None"]
        
    cookies = response_h.get('Set-Cookie')
    if cookies:
        print(f"\n[+] Tracking cookies found: {cookies}")
        server_infos['Cookies'] = [f"{cookies}"]
    else:
        print("\n[-] No cookies found")
        server_infos['Cookies'] = ["None"]
        
    Accss_Cntrl_Al_Org = response_h.get('Access-Control-Allow-Origin')
    if Accss_Cntrl_Al_Org:
        print("\n[+] CORS policy found")
        server_infos["Access-Control-Allow-Origin"] = [f"{Accss_Cntrl_Al_Org}"]
    else:
        print("\n[-] No CORS policy found")
        server_infos["Access-Control-Allow-Origin"] = ["None"]
    return server_infos

def analyze_security_headers(response_h):
    """Analyze all the stuffs from the headers that can be useful for security informations"""
    #Not going to comment this code either
    secur_headers = {}
    
    HTTPS_pres = response_h.get('Strict-Transport-Security')
    if HTTPS_pres:
        print("\n[+] HTTPS is required for this web page")
        secur_headers["HTTPS requirement"] = True
    else:
        print("\n[-] HTTPS isn't required to access to this page")
        secur_headers["HTTPS requirement"] = False
        
    XSS_prot =  response_h.get('Content-Security-Policy')
    if XSS_prot:
        print("\n[+] Content-Security-Policy found for this page")
        secur_headers["Content-Security-Policy"] = True
    else:
        print("\n[-] No Content-Security-Policy found for this page")
        secur_headers["Content-Security-Policy"] = False
        
    clickJacking_prot = response_h.get('X-Frame-Options')
    if clickJacking_prot:
        print("\n[+] Protections against clickjacking found")
        secur_headers["X-Frame-Options"] = True
    else:
        print("\n[-] No clickjacking protections found")
        secur_headers["X-Frame-Options"] = False
        
    MIME_prot = response_h.get('X-Content-Type-Options')
    if MIME_prot:
        print("\n[+] Protections against MIME sniffing found")
        secur_headers["X-Content-Type-Options"] = True
    else:
        print("\n[-] No protections against MIME sniffing found")
        secur_headers["X-Content-Type-Options"] = False
        
    Authorization = response_h.get('Authorization')
    if Authorization:
        print(f"\n[+] Authorization found in the headers: {Authorization}")
        secur_headers["Authorization"] = [f"{Authorization}"]
    else:
        print("\n[-] No authorizations found in the headers")
        secur_headers["Authorization"] = ["No Authorization found"]
        
    cache = response_h.get('Cache-Control')
    if cache:
        print("\n[+] Cache-Control found, no vuln")
        secur_headers["Cache-Control"] = True
    else:
        print("\n[-] No Cache-Control found, vuln found") #Yes, cache-control is important 
        secur_headers["Cache-Control"] = False
    return secur_headers

def export_JSON(database, name):
    """Export all the infos in a JSON file wich can be sent to an AI using an API"""
    filename = f"{name}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=4, ensure_ascii=False) #saving the data
        print(f"\n Data successfully saved in : {filename}")


def site_type_detector2000(soup):
    """Can detect the type of site you're scrapping"""
    #I really like the name I gave to this function
    score = {
        "ecommerce" : 0,
        "blog_media" : 0,
        "corporate_showcase" : 0,
        "directory_listing" : 0
    }

    KEYWORDS_DICTIONARY = { #an entire dict with keyword to find wich type of site the user is scraping
        "ecommerce": [
            "cart", "shopping-cart", "minicart", "bag", "basket",
            "checkout", "add-to-cart", "buy-now", "purchase", "order", 
            "product-id", "sku", "price", "currency", "stock", "in-stock",
            "wishlist", "shipping", "billing", "my-account", "customer",
            "stripe", "paypal", "shopify", "woocommerce"
        ],
    
        "blog_media": [
            "blog", "article", "post", "news", "press",
            "author", "writer", "byline", "published-at", "datepublished",
            "reading-time", "min-read", "read-time",
            "category", "tag", "comments", "newsletter", "subscribe",
            "feed", "rss", "headline", "editorial"
        ],
    
        "corporate_showcase": [
            "about-us", "about", "our-team", "who-we-are", "company",
            "services", "solutions", "features", "what-we-do", "portfolio",
            "contact", "get-in-touch", "contact-form", "request-quote", "cta",
            "testimonials", "case-studies", "clients", "careers", "hiring",
            "privacy-policy", "terms-of-service", "legal"
        ],
    
        "directory_listing": [
            "search", "find", "explore", "browse",
            "listing", "listings", "item", "card",
            "filter", "filters", "sorting", "refine",
            "jobs", "apply", "vacancy",
            "property", "estate", "rent", "sale", "location", "map",
            "pagination", "next-page", "load-more"
        ]
    }

    for site_type, patterns in KEYWORDS_DICTIONARY.items():
        for pattern in patterns:
            if re.search(pattern, str(soup), re.IGNORECASE): #check for matching patterns
                score[site_type] += 1

    type_detected = max(score, key=score.get)

    if score[type_detected] == 0:
        tqdm.write("\n[-] We couldn't find what type of site is this one")
    else:
        tqdm.write(f"\n[+] This site is probably a {type_detected}")
        return type_detected

def find_file():
    """Search for the file with the path given by the user"""
    path = input("\n[?] Enter the path of your JSON file configurating your proxy")
    try:
        with open(path, 'r', encoding = 'utf-8') as file:
            dict = json.load(file) #loading the file directly converted into a dict
            return dict
    except FileNotFoundError:
        print(f"\n[-] Error, the file located at {path} isn't found")
        return False
    except PermissionError:
        print(f"\n[-] Error, we don't have the perms to read this file")
        return False
    

