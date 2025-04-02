# MCP for VuFind



## Scope

This is a simple MCP server based on https://github.com/jlowin/fastmcp the goal is to enable the integration of VuFinds Swagger API into an LLM like Sonet.
This enables the LLM to use  Vufind and search for literature 

## Supported Systems

Currently this MCP server supports DAIA and VuFinds Swagger API

## Installation 

just use
pip install -r requierments.txt

## configure your APIs 

Claude executes the MCP server on your local machine each API call originates from your system . This implies that the API has to be accessible from your local machine. 
Define your API endpoints in config.ini

## Configure Claude

To set up Claude Desktop as a Ghidra MCP client, go to `Claude` -> `Settings` -> `Developer` -> `Edit Config` -> `claude_desktop_config.json` and add the following:

```json
{
    "mcpServers": {
      "Vufind": {
        "command": "python",
        "args": [
          "C:/ubmcp/UBBSMCP/server.py ",
          "C:/ubmcp/UBBSMCP/config.ini"
        ]
      }
    }
  }
```
adjust the paths to your server.py and config.ini acordingly

## claude in action


![claude on startup](images\claude_main.PNG)

A small hammer indicates that claude uses an MCP server. A click  on the hammer icon shows to exported MCP functions.

![exposed MCP Functions](\UBBSMCP\images\claude_main.PNG)
