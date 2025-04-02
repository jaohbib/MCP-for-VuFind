from fastmcp import FastMCP
import requests
import configparser
import sys


vufind_url = ""
daia_url = ""

mcp = FastMCP("VuFind MCP")


def parse_conf(path: str = "C:/config.ini"):
    config = configparser.ConfigParser()
    config.read(path)
    global vufind_url
    global daia_url
    if ('vufind' in config): 
        vufind_url = config['vufind']['vufind_url']
    if ('paia' in config): 
        daia_url = config['paia']['daia_url']


def safe_get(endpoint: str, params: dict = None) -> list:
    """
    Perform a GET request. If 'params' is given, we convert it to a query string.
    """
    if params is None:
        params = {}
    qs = [f"{k}={v}" for k, v in params.items()]
    query_string = "&".join(qs)
    url = f"{vufind_url}/{endpoint}"
    if query_string:
        url += "?" + query_string

    try:
        response = requests.get(url, timeout=5)
        response.encoding = 'utf-8'
        if response.ok:
            return response.text.splitlines()
        else:
            return [f"Error {response.status_code}: {response.text.strip()}"]
    except Exception as e:
        return [f"Request failed: {str(e)}"]

def safe_get_daia(endpoint: str, params: dict = None) -> list:
    """
    return a publications availability based on its id 
    """
    if params is None:
        params = {}
    qs = [f"{k}={v}" for k, v in params.items()]
    query_string = "&".join(qs)
    url = f"{daia_url}/{endpoint}"
    if query_string:
        url += "?" + query_string

    try:
        response = requests.get(url, timeout=5)
        response.encoding = 'utf-8'
        if response.ok:
            return response.text.splitlines()
        else:
            return [f"Error {response.status_code}: {response.text.strip()}"]
    except Exception as e:
        return [f"Request failed: {str(e)}"]



def check_functions():
    global vufind_url
    global daia_url
    if (daia_url != ""):

        @mcp.tool()
        def get_availability(offset: int = 0, limit: int = 100, ppn: str ="*") -> list:
            """
        get the local availability of o document specified by the id of the document
            """
            return safe_get_daia("daia", {"id":"ppn:"+ppn, "format":"json"})

    if (vufind_url != ""):

        @mcp.tool()
        def search_literature(offset: int = 0, limit: int = 100, lookfor: str ="*") -> list:
            """
        look for content in the library catalogue 
            """
            return safe_get("vufind/api/v1/search", {"lookfor":lookfor})


if __name__ == "__main__":
    if (len(sys.argv) == 2):
        parse_conf(str(sys.argv[1]))
        #parse_conf()
    else:
      	parse_conf()
    check_functions()
    mcp.run()