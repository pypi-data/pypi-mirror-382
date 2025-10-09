import datetime, inspect

class AoLog:
    def __init__(
        self, 
        log_level: int = 0,
        rollover_size: int = 50000000,
        send_stdout: bool = False,
        log_file_path: str = "main.log",
        has_info: bool = False,
        has_warnings: bool = False,
        has_errors: bool = False,
        transactions: list[str] = [],
    ):
        self.log_level = log_level
        self.rollover_size= rollover_size
        self.send_stdout = send_stdout
        self.log_file_path = log_file_path
        self.has_info = has_info
        self.has_warnings= has_warnings
        self.has_errors= has_errors
        self.transactions = transactions
    
    def _get_caller_info(self) -> tuple[str, str, int]:
        frame = inspect.currentframe()
        if frame == None:
            return "no_frame", "no_function", 0

        else:
            frame = frame.f_back.f_back
            frame_info = inspect.getframeinfo(frame)
            return frame_info.filename, frame_info.function, frame_info.lineno

    def log_info(self, message: str) -> int:
        message = str(message)
        file, func, line = self._get_caller_info()
        formatted_message = f"{datetime.datetime.now().isoformat(timespec='seconds')} | INFO: {file}.{func}:{line} -- {message}"
        self.transactions.append(formatted_message)
        self.has_info = True
        return len(self.transactions)

    def log_warning(self, message: str, debug: str) -> int:
        message = str(message)
        file, func, line = self._get_caller_info()
        formatted_message = f"{datetime.datetime.now().isoformat(timespec='seconds')} | WARNING: {file}.{func}:{line} -- {message} | DEBUG: {debug}"
        self.transactions.append(formatted_message)
        self.has_warnings = True
        return len(self.transactions)

    def log_error(self, message: str, debug: str) -> int:
        message = str(message)
        file, func, line = self._get_caller_info()
        formatted_message = f"{datetime.datetime.now().isoformat(timespec='seconds')} | ERROR: {file}.{func}:{line} -- {message} | DEBUG: {debug}"
        self.transactions.append(formatted_message)
        self.has_errors = True
        return len(self.transactions)
    
    def full_reset(self):
        del self.calling_func
        del self.line_number
        del self.transactions

        self.calling_func = ""
        self.line_number = 0
        self.transactions= []
        self.has_errors = False
        self.has_warnings= False
        self.has_info= False

    def reset_errors(self):
        self.has_errors = False

    def reset_warnings(self):
        self.has_warnings= False

    def reset_info(self):
        self.has_info= False

    def flush(self, log_file_path: str = "", keep_state: bool = False) -> bool:
        """
        Purpose:
            This function is the actual mechnism by which stored log data gets written to the log file(s).
            Logs aren't immediately pushed to the log file because batching is more efficient and allows for
            additional controls in case logs are large or could potentially contain sensitive info.
        """
        error = False

        if type(log_file_path) != str:
            error = True
        
        elif log_file_path == "":
            with open(self.log_file_path, "a+") as f:
                for line in self.transactions:
                    line = line.replace("\n", "--")
                    f.write(line + "\n")

        else:
            with open(log_file_path, "a+") as f:
                for line in self.transactions:
                    line = line.replace("\n", "--")
                    f.write(line + "\n")
        
        # reset the logger to neutral
        if keep_state == False:
            del self.transactions
            self.transactions = []
            self.reset_errors()
            self.reset_info()
            self.reset_warnings()

        return error
    
    def rollup_aolog(self, log: "AoLog"):
        self.transactions.extend(log.transactions)
        if log.has_errors: self.has_errors = True
        if log.has_info: self.has_info = True
        if log.has_warnings: self.has_warnings = True
        
        del log

    
if __name__ == "__main__":
    Log = AoLog()
    Log.log_info("test info")
    Log.log_warning("test warning", "")
    Log.log_error("test error", "this is an error string")
    flushed = Log.flush()
    if not flushed:
        print("didn't flush")