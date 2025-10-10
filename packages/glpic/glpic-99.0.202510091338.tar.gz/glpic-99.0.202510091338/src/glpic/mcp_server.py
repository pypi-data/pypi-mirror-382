import argparse
# import os
from glpic import Glpi
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers

mcp = FastMCP("glpimcp")


@mcp.tool()
def create_reservation(context: Context,
                       computer: str, overrides: dict) -> dict:
    """Create glpi reservation"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.create_reservation(computer, overrides)


@mcp.tool()
def delete_reservation(context: Context,
                       reservation: str) -> dict:
    """Delete glpi reservation"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.delete_reservation(reservation)


@mcp.tool()
def info_computer(context: Context,
                  computer: str) -> dict:
    """Get info on glpi computer"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.info_reservation({'computer': computer})


@mcp.tool()
def info_reservation(context: Context,
                     reservation: str) -> dict:
    """Get info on glpi reservation"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.info_reservation(reservation)


@mcp.tool()
def get_user(context: Context,
             searchuser: str = None) -> dict:
    """Get info on glpi user"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.get_user(searchuser or user)


@mcp.tool()
def list_computers(context: Context,
                   overrides: dict) -> list:
    """List glpi computers"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.list_computers(overrides)


@mcp.tool()
def list_reservations(context: Context,
                      overrides: dict) -> list:
    """List glpi reservations"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.list_reservations(overrides)


@mcp.tool()
def list_users(context: Context,
               overrides: dict) -> list:
    """List glpi users"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.list_users(overrides)


@mcp.tool()
def update_computer(context: Context,
                    computer: str, overrides: dict) -> dict:
    """Update glpi computer"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    return glpic.update_computer(computer, overrides)


@mcp.tool()
def update_reservation(context: Context,
                       user: str, reservation: str, overrides: dict) -> dict:
    """Create glpi reservation"""
    url = get_http_headers().get('glpi_url')
    user = get_http_headers().get('glpi_user')
    token = get_http_headers().get('glpi_token')
    glpic = Glpi(url, user, token)
    overrides['user'] = user
    return glpic.update_reservation(reservation, overrides)


def main():
    parser = argparse.ArgumentParser(description="glpimcp")
    parser.add_argument("--port", type=int, default=8000, help="Localhost port to listen on")
    parser.add_argument("-s", "--stdio", action='store_true')
    args = parser.parse_args()
    parameters = {'transport': 'stdio'} if args.stdio else {'transport': 'http', 'host': '0.0.0.0', 'port': args.port}
    mcp.run(**parameters)


if __name__ == "__main__":
    main()
