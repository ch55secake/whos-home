import json
from typing import Annotated

import rich
import typer as t

from src.data.scan_result import ScanResult
from src.executor.nmap_executor import NmapExecutor
from src.parser.nmap_output_parser import NmapOutputParser

app: t.Typer = t.Typer()

@app.command(help="Scan a provided host to find the devices that are currently on the host that you provided, "
                  "will execute either a passive or aggressive scan depending on the option provided. You are also "
                  "able to provide a given CIDR that you want to scan across. The CIDR will default to 24.",
             short_help="Scan for details about your network")
def now(host: Annotated[str, t.Argument(help="The host that you want to scan against.")],
        cidr: Annotated[str, t.Option(help="The CIDR of the host that you want to scan against.")] = "24",
        schedule: Annotated[str, t.Option(help="Run scans on a schedule of any of these values: 5m, 15m, 30m, 45m, 1h")] = "",
        host_range: Annotated[str, t.Option(help="Run scans against a range of IPs.")] = ""):
    """
    Discover hosts on the network using nmap
    """
    executor: NmapExecutor = NmapExecutor(host=host, cidr=cidr)
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
    🛰️ Curious about the devices connected to your network?
    """

def main():
   app()

if __name__ == "__main__":
    main()
