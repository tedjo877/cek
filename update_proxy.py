import requests
import csv
import os
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Mapping kode negara ke benua (maksimal 5 huruf)
COUNTRY_TO_CONTINENT = {
    # Asia
    'AF': 'ASIAN', 'AM': 'ASIAN', 'AZ': 'ASIAN', 'BH': 'ASIAN', 'BD': 'ASIAN', 'BT': 'ASIAN',
    'BN': 'ASIAN', 'KH': 'ASIAN', 'CN': 'ASIAN', 'CY': 'ASIAN', 'GE': 'ASIAN', 'IN': 'ASIAN',
    'ID': 'ASIAN', 'IR': 'ASIAN', 'IQ': 'ASIAN', 'IL': 'ASIAN', 'JP': 'ASIAN', 'JO': 'ASIAN',
    'KZ': 'ASIAN', 'KW': 'ASIAN', 'KG': 'ASIAN', 'LA': 'ASIAN', 'LB': 'ASIAN', 'MY': 'ASIAN',
    'MV': 'ASIAN', 'MN': 'ASIAN', 'MM': 'ASIAN', 'NP': 'ASIAN', 'KP': 'ASIAN', 'OM': 'ASIAN',
    'PK': 'ASIAN', 'PS': 'ASIAN', 'PH': 'ASIAN', 'QA': 'ASIAN', 'SA': 'ASIAN', 'SG': 'ASIAN',
    'KR': 'ASIAN', 'LK': 'ASIAN', 'SY': 'ASIAN', 'TW': 'ASIAN', 'TJ': 'ASIAN', 'TH': 'ASIAN',
    'TL': 'ASIAN', 'TR': 'ASIAN', 'TM': 'ASIAN', 'AE': 'ASIAN', 'UZ': 'ASIAN', 'VN': 'ASIAN',
    'YE': 'ASIAN',

    # Europe
    'AL': 'EUROP', 'AD': 'EUROP', 'AT': 'EUROP', 'BY': 'EUROP', 'BE': 'EUROP', 'BA': 'EUROP',
    'BG': 'EUROP', 'HR': 'EUROP', 'CZ': 'EUROP', 'DK': 'EUROP', 'EE': 'EUROP', 'FI': 'EUROP',
    'FR': 'EUROP', 'DE': 'EUROP', 'GR': 'EUROP', 'HU': 'EUROP', 'IS': 'EUROP', 'IE': 'EUROP',
    'IT': 'EUROP', 'LV': 'EUROP', 'LI': 'EUROP', 'LT': 'EUROP', 'LU': 'EUROP', 'MT': 'EUROP',
    'MD': 'EUROP', 'MC': 'EUROP', 'ME': 'EUROP', 'NL': 'EUROP', 'MK': 'EUROP', 'NO': 'EUROP',
    'PL': 'EUROP', 'PT': 'EUROP', 'RO': 'EUROP', 'RU': 'EUROP', 'SM': 'EUROP', 'RS': 'EUROP',
    'SK': 'EUROP', 'SI': 'EUROP', 'ES': 'EUROP', 'SE': 'EUROP', 'CH': 'EUROP', 'UA': 'EUROP',
    'GB': 'EUROP', 'VA': 'EUROP',

    # North America
    'AG': 'NORTH', 'BS': 'NORTH', 'BB': 'NORTH', 'BZ': 'NORTH', 'CA': 'NORTH', 'CR': 'NORTH',
    'CU': 'NORTH', 'DM': 'NORTH', 'DO': 'NORTH', 'SV': 'NORTH', 'GD': 'NORTH', 'GT': 'NORTH',
    'HT': 'NORTH', 'HN': 'NORTH', 'JM': 'NORTH', 'MX': 'NORTH', 'NI': 'NORTH', 'PA': 'NORTH',
    'KN': 'NORTH', 'LC': 'NORTH', 'VC': 'NORTH', 'TT': 'NORTH', 'US': 'NORTH',

    # South America
    'AR': 'SOUTH', 'BO': 'SOUTH', 'BR': 'SOUTH', 'CL': 'SOUTH', 'CO': 'SOUTH', 'EC': 'SOUTH',
    'GY': 'SOUTH', 'PY': 'SOUTH', 'PE': 'SOUTH', 'SR': 'SOUTH', 'UY': 'SOUTH', 'VE': 'SOUTH',

    # Africa
    'DZ': 'AFRIC', 'AO': 'AFRIC', 'BJ': 'AFRIC', 'BW': 'AFRIC', 'BF': 'AFRIC', 'BI': 'AFRIC',
    'CV': 'AFRIC', 'CM': 'AFRIC', 'CF': 'AFRIC', 'TD': 'AFRIC', 'KM': 'AFRIC', 'CD': 'AFRIC',
    'DJ': 'AFRIC', 'EG': 'AFRIC', 'GQ': 'AFRIC', 'ER': 'AFRIC', 'ET': 'AFRIC', 'GA': 'AFRIC',
    'GM': 'AFRIC', 'GH': 'AFRIC', 'GN': 'AFRIC', 'GW': 'AFRIC', 'CI': 'AFRIC', 'KE': 'AFRIC',
    'LS': 'AFRIC', 'LR': 'AFRIC', 'LY': 'AFRIC', 'MG': 'AFRIC', 'MW': 'AFRIC', 'ML': 'AFRIC',
    'MR': 'AFRIC', 'MU': 'AFRIC', 'MA': 'AFRIC', 'MZ': 'AFRIC', 'NA': 'AFRIC', 'NE': 'AFRIC',
    'NG': 'AFRIC', 'RW': 'AFRIC', 'ST': 'AFRIC', 'SN': 'AFRIC', 'SC': 'AFRIC', 'SL': 'AFRIC',
    'SO': 'AFRIC', 'ZA': 'AFRIC', 'SS': 'AFRIC', 'SD': 'AFRIC', 'SZ': 'AFRIC', 'TZ': 'AFRIC',
    'TG': 'AFRIC', 'TN': 'AFRIC', 'UG': 'AFRIC', 'EH': 'AFRIC', 'ZM': 'AFRIC', 'ZW': 'AFRIC',

    # Oceania
    'AS': 'OCEAN', 'AU': 'OCEAN', 'CK': 'OCEAN', 'FJ': 'OCEAN', 'PF': 'OCEAN', 'GU': 'OCEAN',
    'KI': 'OCEAN', 'MH': 'OCEAN', 'FM': 'OCEAN', 'NR': 'OCEAN', 'NC': 'OCEAN', 'NZ': 'OCEAN',
    'NU': 'OCEAN', 'MP': 'OCEAN', 'PW': 'OCEAN', 'PG': 'OCEAN', 'WS': 'OCEAN', 'SB': 'OCEAN',
    'TK': 'OCEAN', 'TO': 'OCEAN', 'TV': 'OCEAN', 'VU': 'OCEAN', 'WF': 'OCEAN'
}


def check_proxy(row, api_url_template):
    ip, port = row[0].strip(), row[1].strip()
    api_url = api_url_template.format(ip=ip, port=port)
    try:
        response = requests.get(api_url, timeout=180)
        response.raise_for_status()
        data = response.json()

        message = data.get("message", "").strip().upper()
        if "ACTIVE ✅" in message:
            proxy_id = data.get("country", "Unknown").split()[0]
            isp = data.get("isp", "Unknown")

            if proxy_id != "Unknown" and isp != "Unknown":
                print(f"{ip}:{port} is ALIVE ✅ - ID: {proxy_id}, ISP: {isp}")
                return (ip, port, proxy_id, isp), None
            else:
                error_message = f"{ip}:{port} has Unknown ID/ISP (ID: {proxy_id}, ISP: {isp})"
                print(error_message)
                return None, error_message
        else:
            print(f"{ip}:{port} is DEAD ❌")
            return None, None
    except requests.exceptions.RequestException as e:
        error_message = f"Error checking {ip}:{port}: {e}"
        print(error_message)
        return None, error_message

def main():
    input_file = os.getenv('IP_FILE', 'proxyip.txt')
    update_file = 'update_proxyip.txt'
    json_file = 'update_proxyip.json'
    json_file_continent = 'update_proxyip8.json'
    error_file = 'error.txt'
    api_url_template = os.getenv('API_URL', 'https://proxy.ndeso.xyz/check?ip={ip}:{port}')

    alive_proxies = []
    error_logs = []
    proxy_dict = defaultdict(list)
    continent_dict = defaultdict(list)

    try:
        with open(input_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"File {input_file} tidak ditemukan.")
        return

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_proxy, row, api_url_template): row for row in rows if len(row) >= 2}

        for future in as_completed(futures):
            alive, error = future.result()
            if alive:
                alive_proxies.append(alive)
                ip, port, proxy_id, _ = alive
                proxy_dict[proxy_id].append(f"{ip}:{port}")
            if error:
                error_logs.append(error)

    # Urutkan hasil berdasarkan proxy_id
    alive_proxies.sort(key=lambda x: x[2])

    # Simpan ke update_proxyip.txt
    try:
        with open(update_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(alive_proxies)
        print(f"Proxy yang ALIVE telah disimpan di {update_file}.")
    except Exception as e:
        print(f"Error menulis ke {update_file}: {e}")

    # Simpan ke update_proxyip.json
    try:
        with open(json_file, "w") as f:
            json.dump(proxy_dict, f, indent=2)
        print(f"Data JSON proxy berdasarkan negara telah disimpan di {json_file}.")
    except Exception as e:
        print(f"Error menulis ke {json_file}: {e}")

    # Baca kembali update_proxyip.txt dan bangun update_proxyip8.json berdasarkan benua
    try:
        with open(update_file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    ip, port, proxy_id = row[0].strip(), row[1].strip(), row[2].strip().upper()
                    continent = COUNTRY_TO_CONTINENT.get(proxy_id, "N/A")[:5].upper()
                    continent_dict[continent].append(f"{ip}:{port}")
                    continent_dict["ALLIN"].append(f"{ip}:{port}")

        with open(json_file_continent, "w") as f:
            json.dump(continent_dict, f, indent=2)
        print(f"Data JSON proxy berdasarkan benua telah disimpan di {json_file_continent}.")
    except Exception as e:
        print(f"Error membangun atau menulis ke {json_file_continent}: {e}")

    # Simpan error
    if error_logs:
        try:
            with open(error_file, "w") as f:
                for error in error_logs:
                    f.write(error + "\n")
            print(f"Beberapa error telah dicatat di {error_file}.")
        except Exception as e:
            print(f"Error menulis ke {error_file}: {e}")

if __name__ == "__main__":
    main()
