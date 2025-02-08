import json
from bs4 import BeautifulSoup
import requests
import re

def get_neighborhoods(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    neighborhoods = []
    script_tag = soup.find('script', string=lambda t: t and 'window.__PRELOADED_STATE__' in t)
    if script_tag:
        script_content = script_tag.string
        
        # استخراج محتوای JSON از اسکریپت با استفاده از regex
        match = re.search(r'window.__PRELOADED_STATE__\s*=\s*({.*?});', script_content, re.DOTALL)
        if match:
            json_content = match.group(1)
            
            try:
                data = json.loads(json_content)
                options = data['nb']['filtersPage']['widgetList'][0]['widgetList'][0]['options']
                for option in options:
                    neighborhoods.append(option['name'])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error decoding JSON: {e}")
                print("JSON content:")
                print(json_content[:1000])  # چاپ 1000 کاراکتر اول برای بررسی

    return neighborhoods

if __name__ == "__main__":
    url = 'https://divar.ir/s/tehran/real-estate'
    neighborhoods = get_neighborhoods(url)
    
    # ذخیره کردن لیست محله‌ها در فایل JSON
    with open('neighborhoods.json', 'w', encoding='utf-8') as f:
        json.dump(neighborhoods, f, ensure_ascii=False, indent=4)
    
    print(neighborhoods)
