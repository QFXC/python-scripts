import functools, timeit


def timer(func):
    """Prints the runtime of the decorated function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        value = func(*args, **kwargs)
        end_time = timeit.default_timer()
        elapsed_time = end_time - start_time
        msg = f'Took {round(elapsed_time, 2)} seconds.'
        script_obj = args[0]
        try:
            if script_obj.generate_excel:
                msg += ' (Including the time it took to generate the Excel file.)'
            else:
                msg += ' (NOT including the time it took to generate the Excel file.)'
        except AttributeError:
            pass
        print(msg)
        return value

    return wrapper
