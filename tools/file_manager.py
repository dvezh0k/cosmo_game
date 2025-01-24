def get_frame(filepath: str):
    try:
        with open(filepath, "r") as file:
            frame = file.read()
            return frame
    except FileNotFoundError:
        return None
