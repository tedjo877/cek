import requests
import csv
import os
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            continent = data.get("continent", "Unknown").upper()  # Assuming continent is in the response

            if proxy_id != "Unknown" and isp != "Unknown":
                print(f"{ip}:{port} is ALIVE ✅ - ID: {proxy_id}, ISP: {isp}, Continent: {continent}")
                return (ip, port, proxy_id, isp, continent), None
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
    json_file_8 = 'update_proxyip8.json'
    error_file = 'error.txt'
    api_url_template = os.getenv('API_URL', 'https://proxy.ndeso.xyz/check?ip={ip}:{port}')

    alive_proxies = []
    error_logs = []
    proxy_dict = defaultdict(list)
    continent_dict = defaultdict(list)  # For continent-based categorization

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
                ip, port, proxy_id, _, continent = alive
                proxy_dict[proxy_id].append(f"{ip}:{port}")

                # Categorize by continent
                continent_abbr = continent[:5].upper()  # Get first 5 letters of the continent name
                continent_dict[continent_abbr].append(f"{ip}:{port}")

            if error:
                error_logs.append(error)

    # Sort the results by proxy_id
    alive_proxies.sort(key=lambda x: x[2])

    try:
        with open(update_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(alive_proxies)
        print(f"Proxy yang ALIVE telah disimpan di {update_file}.")
    except Exception as e:
        print(f"Error menulis ke {update_file}: {e}")

    try:
        with open(json_file, "w") as f:
            json.dump(proxy_dict, f, indent=2)
        print(f"Data JSON proxy yang ALIVE telah disimpan di {json_file}.")
    except Exception as e:
        print(f"Error menulis ke {json_file}: {e}")

    # Write the continent-based categorization to update_proxyip8.json
    try:
        with open(json_file_8, "w") as f:
            # Add the continent categories to the file
            continent_dict['ALLIN'] = [item for sublist in continent_dict.values() for item in sublist]  # All proxies
            json.dump(continent_dict, f, indent=2)
        print(f"Data JSON proxy berdasarkan benua telah disimpan di {json_file_8}.")
    except Exception as e:
        print(f"Error menulis ke {json_file_8}: {e}")

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
