from rich.live import Live
from rich.panel import Panel
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
                # Hack so I can have the spinner more nicely spaced
                TextColumn(" "),
                SpinnerColumn(style="magenta", speed=20),
                TextColumn("[progress.description]{task.description}"),
            )
        return cls._instance
