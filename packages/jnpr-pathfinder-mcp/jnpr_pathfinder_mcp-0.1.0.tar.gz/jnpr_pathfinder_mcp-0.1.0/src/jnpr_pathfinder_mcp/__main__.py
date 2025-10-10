import argparse

from jnpr_pathfinder_mcp import server


def parse_args():
    parser = argparse.ArgumentParser(prog="jnpr_pathfinder_mcp")
    parser.add_argument(
        "--transport", choices=["stdio", "http"], default="stdio", help="transport to use"
    )
    parser.add_argument("--host", help="host for http transport", default=None)
    parser.add_argument("--port", help="port for http transport", type=int, default=None)
    return parser.parse_args()


def run_cli(args):
    transport = args.transport
    host = args.host
    port = args.port

    if transport == "stdio" and (host is not None or port is not None):
        raise ValueError("host/port cannot be used with stdio transport")

    server.run(transport=transport, host=host, port=port)


def main():
    args = parse_args()
    run_cli(args)


if __name__ == "__main__":  # pragma: no cover
    main()
