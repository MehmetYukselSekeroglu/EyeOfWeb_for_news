import imghdr

def validate_image(stream_of_image):
    header_is = stream_of_image.read(512)
    file_format = imghdr.what(None, header_is)
    if not file_format:
        return None
    return "." + str(file_format)

