import re

import curl_cffi
from curl_cffi import requests


def get_auction_id(url:str):
    pattern = r"https://www\.eauctionsindia\.com/properties/(\d+)"
    match = re.search(pattern=pattern,string=url)
    return match.group(1)


def sale_notice_url_formatter(sales_notice):
    if 'eauctionsindia' in sales_notice:
        return sales_notice
    else:
        return 'https://www.eauctionsindia.com'+sales_notice


from seleniumbase import SB

# def get_cookies(url):
#     with SB(uc=True, test=True,headless=True) as sb:
#         sb.uc_open_with_reconnect(url, 4)
#         sb.uc_gui_click_captcha()
#
#         print(sb.get_page_title())
#
#         html = sb.get_page_source()
#         print(f"Page length: {len(html)} bytes")
#
#         status = sb.execute_script("""
#             const entries = window.performance.getEntriesByType('navigation');
#             return entries.length ? entries[0].responseStatus : null;
#         """)
#         print(f"Page status: {status}")
#
#         # ── Extract all cookies as a dict ──────────────────────────────────
#         raw_cookies = sb.driver.get_cookies()  # list of cookie dicts
#
#         cookie_dict = {c["name"]: c["value"] for c in raw_cookies}
#
#         # Pull cf_clearance specifically
#         cf_clearance = cookie_dict.get("cf_clearance")
#         print(f"cf_clearance: {cf_clearance}")
#         print(f"All cookies: {cookie_dict}")
#         actual_ua = sb.execute_script("return navigator.userAgent")
#
#         return actual_ua,cookie_dict


def get_cookies(url):
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        headers = response.headers
        return dict(headers)
    except curl_cffi.exceptions.RequestException as e:
        print(e)

def is_property_cached(borrower_cache:dict,borrower_name:str,branch_name:str)->bool:#function used to eliminate the duplicate auction properties

    if borrower_cache.get(borrower_name):
        #if this condition satisfies then the property is already inserted
        #now check for the bank names as well
        if borrower_cache.get(borrower_name) == branch_name:
            #if this condition also satisfies then this is considered as a duplicate entry
            return True

    return False

