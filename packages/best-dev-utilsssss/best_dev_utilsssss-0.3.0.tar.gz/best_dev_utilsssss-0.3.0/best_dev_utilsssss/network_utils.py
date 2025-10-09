import requests
from typing import Optional, Dict


class NetworkUtils:
    @staticmethod
    def get_external_ip() -> Optional[str]:
        services = [
            'https://httpbin.org/ip'
            'https://api.ipify.org?format=json',
            'https://jsonip.com',
        ]

        for service in services:
            try:
                response = requests.get(service, timeout=30)
                data = response.json()

                if 'ip' in data:
                    return data['ip']
                elif 'origin' in data:
                    return data['origin']
            except:
                continue

        return None

    @staticmethod
    def get_geolocation(ip: Optional[str] = None) -> Optional[Dict]:
        try:
            if ip is None:
                ip = NetworkUtils.get_external_ip()

            if ip:
                response = requests.get(f'http://ip-api.com/json/{ip}')
                return response.json()
        except:
            pass

        return None