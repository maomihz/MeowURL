# request control ??

import time

# interval in seconds
# an argument(exceed limit or not) will be passed to callback
def limit(interval, max_request, callback):
    last_req = None
    count = 0

    def handler():
        nonlocal last_req
        nonlocal count

        count += 1
        now = time.time()
        exceed = False

        if last_req is None:
            last_req = now
        elif now - last_req < interval:
            if count > max_request:
                exceed = True
        else: # interval exceeded
            last_req = now
            count = 0

        return callback(exceed)

    return handler
