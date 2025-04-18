import json
from pathlib import Path
from typing import OrderedDict, Any

import pytest
from rich import print_json

from src.data.command_result import CommandResult
from src.data.scan_result import ScanResult
from src.parser.nmap_output_parser import NmapOutputParser


@pytest.fixture
def fake_nmap_response():
    resource_path = Path(__file__).parent / "resources" / "fake_nmap_response.xml"

    if not resource_path.exists():
        pytest.fail(f"Resource file {resource_path} not found!")

    with open(resource_path, encoding="UTF-8") as file:
        return file.read()


def test_nmap_output_parser(fake_nmap_response):
    command_result: CommandResult = CommandResult(
        command="nmap",
        stdout=fake_nmap_response,
        stderr="",
        success=True,
        return_code=0,
    )

    parser = NmapOutputParser(command_result=command_result)
    dict_output_from_parser: OrderedDict[str, Any] = parser.parse()
    print_json(json.dumps(dict_output_from_parser, indent=2))


def test_nmap_output_parser_for_scan_result(fake_nmap_response):
    command_result: CommandResult = CommandResult(
        command="nmap",
        stdout=fake_nmap_response,
        stderr="",
        success=True,
        return_code=0,
    )

    parser = NmapOutputParser(command_result=command_result)
    actual_scan_result: ScanResult = parser.create_scan_result()
    assert actual_scan_result.hosts is not None
    assert actual_scan_result.run_stats is not None
