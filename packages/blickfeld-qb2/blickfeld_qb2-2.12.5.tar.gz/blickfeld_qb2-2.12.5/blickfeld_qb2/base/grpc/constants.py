# Increase message size limit to allow large point cloud transfers
MAX_MESSAGE_LENGTH = 32 * 1024 * 1024
OPTIONS = [
    ("grpc.max_send_message_length", MAX_MESSAGE_LENGTH),
    ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
]
