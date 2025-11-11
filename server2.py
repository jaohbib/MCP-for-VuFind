from typing import Dict, List, Optional
import requests
import configparser
import argparse
import logging
import sys

from fastmcp import FastMCP

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

mcp = FastMCP("VuFind MCP")


class Config:
    def __init__(self, path: str = "config.ini"):
        self.vufind_url: str = ""
        self.vufind_url_article: str = ""
        self.vufind_url_frontend: str = ""
        self.vufind_url_frontend_article: str = ""
        self.daia_url: str = ""
        self.server_mode: str = ""
        self._load(path)

    def _load(self, path: str) -> None:
        cfg = configparser.ConfigParser()
        read_files = cfg.read(path)
        if not read_files:
            log.info("No config file found at '%s', using defaults", path)
            return

        if "vufind" in cfg and "vufind_url" in cfg["vufind"]:
            self.vufind_url = cfg["vufind"]["vufind_url"]
        if "vufind" in cfg and "vufind_url_article" in cfg["vufind"]:
            self.vufind_url_article = cfg["vufind"]["vufind_url_article"]
        if "paia" in cfg and "daia_url" in cfg["paia"]:
            self.daia_url = cfg["paia"]["daia_url"]
        if "server" in cfg and "mode" in cfg["server"]:
            log.info("server mode set")
            self.server_mode = cfg["server"]["mode"]
        if "vufind" in cfg and "vufind_url_frontend" in cfg["vufind"]:
            log.info("frontend set")
            self.vufind_url_frontend = cfg["vufind"]["vufind_url_frontend"]
        if "vufind" in cfg and "vufind_url_frontend_article" in cfg["vufind"]:
            self.vufind_url_frontend_article = cfg["vufind"]["vufind_url_frontend_article"]


class HTTPClient:
    def __init__(self, timeout: float = 10.0):
        self.session = requests.Session()
        self.timeout = timeout

    def get_lines(self, base_url: str, endpoint: str = "", params: Optional[Dict] = None) -> List[str]:
        if not base_url:
            return ["Error: base URL not configured"]
        url = base_url.rstrip("/") + (f"/{endpoint.lstrip('/')}" if endpoint else "")
        try:
            resp = self.session.get(url, params=params or {}, timeout=self.timeout)
            resp.encoding = "utf-8"
            if resp.ok:
                return resp.text.splitlines()
            return [f"Error {resp.status_code}: {resp.text.strip()}"]
        except requests.RequestException as exc:
            log.debug("Request failed: %s", exc, exc_info=True)
            return [f"Request failed: {exc}"]


def register_tools(mcp_instance: FastMCP, cfg: Config, client: HTTPClient) -> None:
    """
    Register MCP tools conditionally depending on config.
    Each tool uses the shared HTTPClient and Config without globals.
    """

    if cfg.daia_url:
        log.info("daia tool set")
        @mcp_instance.tool()
        def get_availability(offset: int = 0, limit: int = 100, ppn: str = "*") -> List[str]:
            """
            Get local availability for a document by PPN using the DAIA endpoint.
            """
            params = {"id": f"ppn:{ppn}", "format": "json", "offset": offset, "limit": limit}
            return client.get_lines(cfg.daia_url, params=params)

    if cfg.vufind_url:
        @mcp_instance.tool()
        def search_literature(offset: int = 0, limit: int = 100, lookfor: str = "*") -> List[str]:
            """
            Search the VuFind catalogue.
            """
            params = {"lookfor": lookfor, "offset": offset, "limit": limit}
            return client.get_lines(cfg.vufind_url , params=params)

    if cfg.vufind_url_article:
        @mcp_instance.tool()
        def search_article(offset: int = 0, limit: int = 100, lookfor: str = "*") -> List[str]:
            """
            Search the VuFind catalogue for articles.
            """
            params = {"lookfor": lookfor, "offset": offset, "limit": limit}
            return client.get_lines(cfg.vufind_url_article , params=params)

    if cfg.vufind_url_frontend:
        log.info("frontend tool set")
        @mcp_instance.tool()
        def frontend_link( ppn: str = "*") -> str:
            """
            returns a catalogue link for a given ppn.
            """
            return cfg.vufind_url_frontend+ppn 

    if cfg.vufind_url_frontend_article:
        @mcp_instance.tool()
        def frontend_link__article( ppn: str = "*") -> str:
            """
            returns a catalogue link for a given article ppn.
            """
            return cfg.vufind_url_frontend_article+ppn


def main(argv: Optional[List[str]] = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run VuFind MCP")
    parser.add_argument("-c", "--config", default="config.ini", help="Path to configuration file")
    args = parser.parse_args(argv)

    cfg = Config(args.config)
    client = HTTPClient(timeout=5.0)
    register_tools(mcp, cfg, client)

    if cfg.server_mode == "http":
        mcp.run(transport="http", host="127.0.0.1", port=8000)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
