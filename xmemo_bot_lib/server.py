from .xmemo_bot import XmemoBot


xmemo = XmemoBot()

msg_list = xmemo.get_msg_list()
last_offset = msg_list[-1]["update_id"] - 2

while True:
    last_offset += 1
    msg = xmemo.get_last_msg(last_offset)
    msg_txt = msg[-1]["message"]["text"]
    chat_id = msg[-1]["message"]["chat"]["id"]
    xmemo.handle_response(msg_txt, chat_id)