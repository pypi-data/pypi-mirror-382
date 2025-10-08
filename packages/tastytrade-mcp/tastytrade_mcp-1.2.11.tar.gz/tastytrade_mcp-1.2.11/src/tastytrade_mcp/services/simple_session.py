"""Simple session manager that uses OAuth tokens."""
import os
import httpx
from typing import Optional
from tastytrade import Session
from tastytrade_mcp.config.settings import get_settings
from tastytrade_mcp.utils.logging import get_logger

logger = get_logger(__name__)

_session: Optional[Session] = None
_access_token: Optional[str] = None


def get_tastytrade_session() -> Session:
    """
    Get a TastyTrade session using either username/password OR OAuth tokens.

    Supports two modes:
    1. Simple mode: Username/password authentication (sandbox)
    2. OAuth mode: Refresh token flow (production/sandbox)

    Returns:
        Session: Authenticated TastyTrade session
    """
    global _session, _access_token

    if _session is None:
        settings = get_settings()

        # Try OAuth credentials first (database mode)
        client_id = os.getenv('TASTYTRADE_CLIENT_ID')
        client_secret = os.getenv('TASTYTRADE_CLIENT_SECRET')
        refresh_token = os.getenv('TASTYTRADE_REFRESH_TOKEN')

        # Fall back to sandbox username/password (simple mode)
        sandbox_username = os.getenv('TASTYTRADE_SANDBOX_USERNAME')
        sandbox_password = os.getenv('TASTYTRADE_SANDBOX_PASSWORD')

        use_production = os.getenv('TASTYTRADE_USE_PRODUCTION', 'false').lower() == 'true'

        try:
            # OAuth mode (database/production)
            if all([client_id, client_secret, refresh_token]):
                logger.info(f"Using OAuth authentication for {'PRODUCTION' if use_production else 'SANDBOX'}")
                base_url = "https://api.tastyworks.com" if use_production else "https://api.cert.tastyworks.com"

                response = httpx.post(
                    f"{base_url}/oauth/token",
                    data={
                        'grant_type': 'refresh_token',
                        'refresh_token': refresh_token,
                        'client_id': client_id,
                        'client_secret': client_secret
                    }
                )

                if response.status_code != 200:
                    raise Exception(f"Token refresh failed: {response.text}")

                token_data = response.json()
                _access_token = token_data['access_token']

                from tastytrade_mcp.services.oauth_session import OAuthSession
                _session = OAuthSession(_access_token, is_test=not use_production)

                logger.info(f"✅ Successfully authenticated to TastyTrade {'PRODUCTION' if use_production else 'SANDBOX'} via OAuth")

            # Simple mode (username/password sandbox)
            elif sandbox_username and sandbox_password:
                logger.info(f"Using username/password authentication for {'PRODUCTION' if use_production else 'SANDBOX'}")

                _session = Session(
                    sandbox_username,
                    sandbox_password,
                    is_test=not use_production
                )

                logger.info(f"✅ Successfully authenticated to TastyTrade {'PRODUCTION' if use_production else 'SANDBOX'} via username/password")

            else:
                raise ValueError(
                    "No credentials configured. Need either:\n"
                    "1. TASTYTRADE_SANDBOX_USERNAME and TASTYTRADE_SANDBOX_PASSWORD (simple mode), or\n"
                    "2. TASTYTRADE_CLIENT_ID, TASTYTRADE_CLIENT_SECRET, and TASTYTRADE_REFRESH_TOKEN (OAuth mode)"
                )

        except Exception as e:
            logger.error(f"Failed to authenticate to TastyTrade: {e}")
            raise

    return _session


def clear_session():
    """Clear the cached session (useful for testing or credential changes)."""
    global _session
    _session = None