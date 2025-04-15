# whos-home
🛰️ Scan for people on your local network and see whos home 

## Getting Started
### Dependencies
- [Python](https://www.python.org/) - v3.12 or later
- [Poetry](https://python-poetry.org/)
- [nmap](https://nmap.org/)

### Running the application
Install the dependencies by executing the following command:
```
poetry install
```

Run the command to see the available commands:
```
poetry run python src/whos_home.py --help
```

## Developing
### Running the tests
We use [pytest](https://docs.pytest.org/en/stable/) for testing. You can run the tests by executing the following command:
```
poetry run pytest
```

### Code style
We use [Pylint](https://pypi.org/project/pylint/) for linting and [Black](https://github.com/psf/black) for code formatting.

In this repository, we have a minimum linting score of 9/10. To run pylint, execute the following command:
```
poetry run pylint .
```

To run Black, execute the following command:
```
poetry run black .
```

## License
This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details
