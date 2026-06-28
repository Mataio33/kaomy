from kaomy.version import __title__, __description__, __version__


class KaomyBanner:
    """
    Display Kaomy startup and collector banners.
    """

    @staticmethod
    def startup() -> str:
        return f"""
============================================================
 _  __
| |/ /__ _  ___  _ __ ___  _   _
| ' // _` |/ _ \\| '_ ` _ \\| | | |
| . \\ (_| | (_) | | | | | | |_| |
|_|\\_\\__,_|\\___/|_| |_| |_|\\__, |
                            |___/

{__title__} v{__version__}
{__description__}
============================================================
"""

    @staticmethod
    def collector(name: str, provider: str, location: str, cache_status: str, simulation: bool) -> str:
        simulation_text = "Yes" if simulation else "No"

        return f"""
------------------------------------------------------------
Kaomy Collector : {name}
Provider        : {provider}
Location        : {location}
Cache           : {cache_status}
Simulation      : {simulation_text}
------------------------------------------------------------
"""
