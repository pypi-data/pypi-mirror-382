import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from .cache_service import get_cache_service
from .cache_handlers import ChatHistoriesHandler, AppValuesHandler, CacheInfoHandler
from .unified_database_schema_service import UnifiedDatabaseSchemaHandler, UnifiedDatabaseQueryHandler
from .snowflake_schema_service import SnowflakeSchemaHandler, SnowflakeQueryHandler


class HelloWorldHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": "Hello World from SignalPilot AI backend!",
            "message": "This is a simple hello world endpoint from the sage agent backend."
        }))


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    # Original hello world endpoint
    hello_route = url_path_join(base_url, "signalpilot-ai-internal", "hello-world")
    
    # Cache service endpoints
    chat_histories_route = url_path_join(base_url, "signalpilot-ai-internal", "cache", "chat-histories")
    chat_history_route = url_path_join(base_url, "signalpilot-ai-internal", "cache", "chat-histories", "([^/]+)")
    
    app_values_route = url_path_join(base_url, "signalpilot-ai-internal", "cache", "app-values")
    app_value_route = url_path_join(base_url, "signalpilot-ai-internal", "cache", "app-values", "([^/]+)")
    
    cache_info_route = url_path_join(base_url, "signalpilot-ai-internal", "cache", "info")
    
    # Database service endpoints
    database_schema_route = url_path_join(base_url, "signalpilot-ai-internal", "database", "schema")
    database_query_route = url_path_join(base_url, "signalpilot-ai-internal", "database", "query")
    
    # MySQL service endpoints
    mysql_schema_route = url_path_join(base_url, "signalpilot-ai-internal", "mysql", "schema")
    mysql_query_route = url_path_join(base_url, "signalpilot-ai-internal", "mysql", "query")
    
    # Snowflake service endpoints
    snowflake_schema_route = url_path_join(base_url, "signalpilot-ai-internal", "snowflake", "schema")
    snowflake_query_route = url_path_join(base_url, "signalpilot-ai-internal", "snowflake", "query")
    
    handlers = [
        # Original endpoint
        (hello_route, HelloWorldHandler),
        
        # Chat histories endpoints
        (chat_histories_route, ChatHistoriesHandler),
        (chat_history_route, ChatHistoriesHandler),
        
        # App values endpoints
        (app_values_route, AppValuesHandler),
        (app_value_route, AppValuesHandler),
        
        # Cache info endpoint
        (cache_info_route, CacheInfoHandler),
        
        # Database service endpoints (unified for PostgreSQL and MySQL)
        (database_schema_route, UnifiedDatabaseSchemaHandler),
        (database_query_route, UnifiedDatabaseQueryHandler),
        
        # MySQL service endpoints (use unified handler)
        (mysql_schema_route, UnifiedDatabaseSchemaHandler),
        (mysql_query_route, UnifiedDatabaseQueryHandler),
        
        # Snowflake service endpoints
        (snowflake_schema_route, SnowflakeSchemaHandler),
        (snowflake_query_route, SnowflakeQueryHandler),
    ]
    
    web_app.add_handlers(host_pattern, handlers)
    
    # Initialize cache service on startup
    cache_service = get_cache_service()
    if cache_service.is_available():
        print(f"SignalPilot AI cache service initialized successfully")
        print(f"Cache directory: {cache_service.cache_dir}")
    else:
        print("WARNING: SignalPilot AI cache service failed to initialize!")
    
    print("SignalPilot AI backend handlers registered:")
    print(f"  - Hello World: {hello_route}")
    print(f"  - Chat Histories: {chat_histories_route}")
    print(f"  - Chat History (by ID): {chat_history_route}")
    print(f"  - App Values: {app_values_route}")
    print(f"  - App Value (by key): {app_value_route}")
    print(f"  - Cache Info: {cache_info_route}")
    print(f"  - Database Schema: {database_schema_route}")
    print(f"  - Database Query: {database_query_route}")
    print(f"  - MySQL Schema: {mysql_schema_route}")
    print(f"  - MySQL Query: {mysql_query_route}")
    print(f"  - Snowflake Schema: {snowflake_schema_route}")
    print(f"  - Snowflake Query: {snowflake_query_route}")