import click
import functools

def progress_bar(length=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            label = kwargs.get("label", "Processing...")

            iterable = args[0] if args else kwargs.get("data", [])
            total = length or len(iterable)

            fill_char = click.style("♥", fg="red")
            empty_char = click.style("♡", fg="white", dim=True)

            with click.progressbar(length=total, label=label, fill_char=fill_char, empty_char=empty_char) as bar:
                return func(*args, **kwargs, bar=bar)  # Pass progress bar to function

        return wrapper

    return decorator
