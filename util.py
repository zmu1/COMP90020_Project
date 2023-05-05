# import json
import pickle


def construct_msg(msg_type, msg_content):
    # msg = json.dumps({"type": msg_type, "content": msg_content})
    msg = {"type": msg_type, "content": msg_content}
    return pickle.dumps(msg)


# def parse_msg(json_obj):
    # msg = json_obj.decode("utf-8")
    # return json.loads(msg)

def parse_msg(pickle_obj):
    return pickle.loads(pickle_obj)
