class Observable:
    """
    A simple class to facilitate the observable pattern.
    """
    def __init__(self, parent, default=None):
        self.parent = parent
        self._value = default
        self._callables = []

    def add_callable(self, clb):
        """
        Add a new change handler.
        """
        self._callables.append(clb)

    def _notify(self):
        for c in self._callables:
            c(self._value, self.parent)

    def set(self, value):
        """
        Set new value
        """
        self._value = value
        self._notify()

    def get(self):
        """
        Get current value
        """
        return self._value
