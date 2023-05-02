import json


def construct_msg(msg_type, msg_content):
    msg = json.dumps({"type": msg_type, "content": msg_content})
    return msg.encode("utf-8")


def parse_msg(json_obj):
    msg = json_obj.decode("utf-8")
    return json.loads(msg)
