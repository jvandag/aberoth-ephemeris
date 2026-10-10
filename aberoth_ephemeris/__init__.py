from .ephemeris import Ephemeris

__all__ = ["Ephemeris", "app"]


def __getattr__(name):
    if name == "app":
        from .UpdateWebServer import app

        globals()[name] = app
        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
