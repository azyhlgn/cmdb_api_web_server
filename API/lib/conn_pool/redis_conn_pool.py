import redis
from CMDB_API_WEB_Server import settings

redis_pool = redis.ConnectionPool.from_url(settings.REDIS_DEFAULT_URL)
url = (
        '%s'
        # '?decode_responses=true'
        '&max_connections=50'
        '&socket_timeout=5'
        '&socket_connect_timeout=3'
        '&health_check_interval=30'
        '&retry_on_timeout=true' % settings.REDIS_DEFAULT_URL
)

pool = redis.ConnectionPool.from_url(url)
