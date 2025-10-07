"""
Helper tools for development purposes.
"""

import time


class TimeIt:
    """
    Measure the duration of an operation.

    Equivalent to console.time / console.timeEnd in JS.

    Usage:
        import omgui.helpers.timeit as timeit

        timeit.start()
        # ... operation ...
        timeit.end()

        timeit.start("my_operation")
        # ... operation ...
        timeit.end("my_operation")
    """

    identifiers = {}

    def start(self, identifier=None):
        """Start timing an operation."""
        self.identifiers[identifier] = time.time()

    def end(self, identifier=None):
        """End timing an operation."""
        start_time = self.identifiers[identifier]
        del self.identifiers[identifier]

        # Calculate total time
        total_time_ms = round((time.time() - start_time) * 1000)
        if total_time_ms > 1000:
            total_time = f"{total_time_ms / 1000} s"
        else:
            total_time = f"{total_time_ms} ms"

        # Print result
        identifier = f"{identifier} " if identifier else ""
        print(f"Operation {identifier}took {total_time}")


timeit = TimeIt()
