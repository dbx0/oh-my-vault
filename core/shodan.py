from core.enums import COLORS
from utils.terminal import print_colored
import requests

def _search_page(api_key, search_term, page=1):
    try:
        base_url = "https://api.shodan.io/shodan/host/search"
        params = {
            "key": api_key,
            "query": search_term,
            "page": page
        }

        response = requests.get(base_url, params=params)
        
        if response.status_code != 200:
            print_colored(f"[!] Failed to call Shodan. Status code: {response.status_code}", COLORS.RED)
            return

        data = response.json()        
        return data["matches"]
    except Exception as e:
        print_colored(f"[!] Failed to call Shodan. Error message: {e}", COLORS.RED)

def search_open_omv(api_key):
    found = []

    page = 1

    search_term = "http.title:openmediavault"

    print_colored(f"[*] Searching Shodan using search term '{search_term}'", COLORS.WHITE)

    while True:
        results = _search_page(api_key, search_term, page)

        if not results:
            break

        print_colored(f"Found {len(results)} results on page {page} on Shodan.", COLORS.WHITE)
        for result in results:
            try:
                ip = result["ip_str"]
                port = result["port"]
                if "http" in result:
                    prefix = 'http'

                    if str(port) == '443':
                        prefix += 's'

                    found.append(f"{prefix}://{ip}:{port}")
            except:
                pass
                
        page += 1

    return found