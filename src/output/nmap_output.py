import rich

from src.data.device import Device


def format_and_output(devices: list[Device]) -> None:
    """
    Neatly outputs the devices it finds
    :param devices: set of devices to output
    :return: nothing, will just print
    """
    for device in devices:
        rich.print(
            f" 🛰️ [bold magenta] Found ip address: [/bold magenta][bold cyan]{device.ip_addr}[/bold cyan] "
            f"[bold magenta]and mac address:[/bold magenta] [bold cyan]{device.mac_addr}[/bold cyan] "
            f"[bold magenta]for hostname:[/bold magenta] "
            f"[bold cyan]{device.hostname}[/bold cyan]"
        )
