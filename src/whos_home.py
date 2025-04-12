import json
from typing import Annotated

import rich
import typer as t

from src.data.scan_result import ScanResult
from src.executor.nmap_executor import NmapExecutor
from src.parser.nmap_output_parser import NmapOutputParser

app: t.Typer = t.Typer()

@app.command(help="", short_help="")
def now():
    """
    Discover hosts on the network using nmap
    """
    executor: NmapExecutor = NmapExecutor(host="192.168.1.0", ranges="24")
    discovery = executor.execute_icmp_host_discovery()
    parser: NmapOutputParser = NmapOutputParser(discovery)
    parsed = parser.create_scan_result()
    rich.print_json(json.dumps(parsed.run_stats))
    for host in parsed.hosts:
        rich.print_json(json.dumps(host))

    pass


@app.callback()
def callback() -> None:
    """



    """

def main():
   app()

if __name__ == "__main__":
    main()
