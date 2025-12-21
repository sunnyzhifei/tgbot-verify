import httpx
import config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_proxy():
    proxy_url = config.PROXY_URL
    print("=" * 50)
    print(f"Current Proxy Setting: {proxy_url}")
    print("=" * 50)

    # 1. 尝试不使用代理获取 IP
    print("1. Testing WITHOUT proxy...")
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get("https://httpbin.org/ip")
            direct_ip = resp.json()["origin"]
            print(f"   Direct IP: {direct_ip}")
    except Exception as e:
        direct_ip = None
        print(f"   Failed to get direct IP: {e}")

    # 2. 尝试使用代理获取 IP
    print("\n2. Testing WITH proxy...")
    if not proxy_url:
        print("   No proxy URL configured in config.py.")
        return

    try:
        # 在 httpx 0.27.0+ 中使用 proxy 参数
        with httpx.Client(proxy=proxy_url, timeout=15.0) as client:
            # 访问一个返回 IP 的服务
            resp = client.get("https://httpbin.org/ip")
            if resp.status_code == 200:
                proxy_ip = resp.json()["origin"]
                print(f"   Proxy IP: {proxy_ip}")
                
                if direct_ip and proxy_ip == direct_ip:
                    print("\n⚠️  WARNING: Proxy IP is the same as Direct IP. Proxy might not be working or you are on the same network.")
                else:
                    print("\n✅ SUCCESS: Proxy is working and returned a different IP!")
            else:
                print(f"   Proxy request failed with status code: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ FAILED: Proxy is not working or connection failed.")
        print(f"   Error: {e}")
        print("\nPlease check if your proxy server (e.g. Clash, V2Ray) is running and the address/port is correct.")

    print("\n3. Testing access to SheerID with proxy...")
    try:
        with httpx.Client(proxy=proxy_url, timeout=15.0) as client:
            resp = client.get("https://services.sheerid.com", follow_redirects=True)
            print(f"   Access to SheerID: {'OK' if resp.status_code == 200 else 'Failed'}")
    except Exception as e:
        print(f"   Access to SheerID failed: {e}")
    print("=" * 50)

if __name__ == "__main__":
    test_proxy()
