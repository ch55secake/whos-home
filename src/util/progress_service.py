from rich.progress import Progress, TextColumn, SpinnerColumn


class ProgressService:
    """
    Singleton class for the progress service
    """

    _instance = None
    progress: Progress | None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProgressService, cls).__new__(cls, *args, **kwargs)
            cls._instance.progress = Progress(
                TextColumn(" "),
                SpinnerColumn(style="magenta", spinner_name="aesthetic"),
                TextColumn("[progress.description]{task.description}"),
            )
        return cls._instance
