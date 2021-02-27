import os


def get_available_hyvees():
    print(os.environ["HYVEE_RADIUS"])
    print(os.environ["HYVEE_LATITUDE"])
    print(os.environ["HYVEE_LONGITUDE"])
    return [{"id": "this one"}]


# If appointments are available,
# use redis to make sure we don't notify again until they're unavailable
