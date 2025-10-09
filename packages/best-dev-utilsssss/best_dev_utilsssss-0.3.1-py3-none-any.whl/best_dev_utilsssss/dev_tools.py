import time
import sys
import string
import secrets
from functools import wraps
from typing import Any, Callable


class DevTools:
    @staticmethod
    def timer(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"{func.__name__} performed for {end_time - start_time:.4f}")
            return result

        return wrapper

    @staticmethod
    def size_of_object(obj: Any) -> int:
        return sys.getsizeof(obj)

    @staticmethod
    def list_attributes(obj: Any, private: bool = False) -> list:
        if private:
            return [attr for attr in dir(obj)]
        else:
            return [attr for attr in dir(obj) if not attr.startswith('_')]

    @staticmethod
    def generate_password(length: int = 12, use_special_chars: bool = True) -> str:
        letters = string.ascii_letters
        digits = string.digits
        special = "!@#$%^&*"

        alphabet = letters + digits
        if use_special_chars:
            alphabet += special

        password = [
            secrets.choice(letters),
            secrets.choice(digits),
        ]

        if use_special_chars:
            password.append(secrets.choice(special))

        password += [secrets.choice(alphabet) for _ in range(length - len(password))]

        secrets.SystemRandom().shuffle(password)

        return ''.join(password)

    @staticmethod
    def progress_bar(iteration: int, total: int, length: int = 50, prefix: str = 'Progress:') -> None:
        percent = int(100 * (iteration / total))
        filled_length = int(length * iteration // total)
        bar = ' ' * filled_length + ' ' * (length - filled_length)

        print(f'\r{prefix} |{bar}| {percent}% ({iteration}/{total})', end='\r')

        if iteration == total:
            print()
