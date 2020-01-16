from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject

# Adapted from
# https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    result
        `object` data returned from processing, anything

    """

    result = pyqtSignal(object)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        result = self.fn(*self.args, **self.kwargs)
        self.signals.result.emit(result)
