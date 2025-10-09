import threading
import time
from typing import Optional

start_time_value = 1759777543

class CodeGenerator:
    def __init__(self):
        self._last_id = 0
        self._lock = threading.Lock()
    
    def __iter__(self):
        return self
    
    def __next__(self) -> Optional[int]:
        with self._lock:
            time_value = int(time.time())
            new_id = time_value - start_time_value
            if new_id <= self._last_id:
                new_id = self._last_id + 1
            self._last_id = new_id
            return new_id

code_generator = CodeGenerator()

if __name__ == "__main__":
    print(next(code_generator))