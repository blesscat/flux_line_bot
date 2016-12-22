class AssistReply(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message

if __name__ == '__main__':
    try:
        raise AssistReply('error has raised')
    except AssistReply as msg:
        print('{} ,{}'.format(msg.message, type(msg.message)))
