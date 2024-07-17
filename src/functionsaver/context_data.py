import contextvars


class ContextData:
    """
    This class is used to store the context data.
    It allows to store the data in a thread local way (supporting multithreading),
                                or a task local way (supporting asyncio tasks).
    """

    def __init__(self):
        self._save_internals = contextvars.ContextVar("THREAD_LOCAL_SAVE_INTERNALS", default=False)
        self._internal_folder = contextvars.ContextVar("THREAD_LOCAL_INTERNAL_FOLDER", default=None)
        self._verbose = contextvars.ContextVar("THREAD_LOCAL_VERBOSE", default=False)
        self._option_save_in = contextvars.ContextVar("THREAD_LOCAL_OPTION_SAVE_IN", default=True)
        self._option_save_out = contextvars.ContextVar("THREAD_LOCAL_OPTION_SAVE_OUT", default=True)
        self._option_save_internals = contextvars.ContextVar("THREAD_LOCAL_OPTION_SAVE_INTERNALS", default=True)
        self._initialized = contextvars.ContextVar("THREAD_LOCAL_INITIALIZED", default=False)

    @property
    def save_internals(self):
        return self._save_internals.get()

    @save_internals.setter
    def save_internals(self, value):
        self._save_internals.set(value)

    @property
    def internal_folder(self):
        return self._internal_folder.get()

    @internal_folder.setter
    def internal_folder(self, value):
        self._internal_folder.set(value)

    @property
    def verbose(self):
        return self._verbose.get()

    @verbose.setter
    def verbose(self, value):
        self._verbose.set(value)

    @property
    def option_save_in(self):
        return self._option_save_in.get()

    @option_save_in.setter
    def option_save_in(self, value):
        self._option_save_in.set(value)

    @property
    def option_save_out(self):
        return self._option_save_out.get()

    @option_save_out.setter
    def option_save_out(self, value):
        self._option_save_out.set(value)

    @property
    def option_save_internals(self):
        return self._option_save_internals.get()

    @option_save_internals.setter
    def option_save_internals(self, value):
        self._option_save_internals.set(value)

    @property
    def initialized(self):
        return self._initialized.get()

    @initialized.setter
    def initialized(self, value):
        self._initialized.set(value)
