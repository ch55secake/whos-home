## Todo

- BUG FIX: when there is only one found ip, the ScanResult hosts variable is not a list as intended. It is instead a dict.


- add markdown table option for output (disabled by default)
- fix os scanning
- Be able to scan multiple ranges
- web interface
- db
- notify user
- way to compare known devices to devices just scanned

### wanted args
- --schedule={1m | 5m | 10m | 15m | 30m | 1h | 1h30m}
- --range={192.168.1.0/24 | 192.168.1.1-10 | "192.168.1.0/24 |192.168.1.1-10"}
