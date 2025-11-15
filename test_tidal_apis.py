from spotiflac.services import get_available_tidal_apis

apis = get_available_tidal_apis()
print(f'Found {len(apis)} Tidal APIs:')
print()

for i, api in enumerate(apis[:10], 1):
    url = api.get('url', 'N/A')
    uptime = api.get('uptime', 0)
    success = api.get('last_check', {}).get('success', False)
    avg_time = api.get('avg_response_time', 0)
    
    status = "✅ WORKING" if success and uptime > 50 else "❌ DOWN"
    print(f'{i}. {status}')
    print(f'   URL: {url}')
    print(f'   Uptime: {uptime:.1f}%')
    print(f'   Avg Response: {avg_time}ms')
    print()
