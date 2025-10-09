import cloudscraper

def topup(phone, vouch):
    """
    This function redeems TrueMoney Wallet voucher by phone number and code.
    Uses Cloudscraper to bypass Cloudflare.
    """
    scraper = cloudscraper.create_scraper()
    payload = {
        "phone": phone,
        "vouch": vouch
    }

    r = scraper.post("https://api.kasawa.pro/api/wallet/topup", json=payload)
    return r
