class recipient:
    def __init__(self, name, ip, port):
        self.name=name
        self.ip=ip
        self.port=port

    def __eq__(self, other):
        return self.name==other.name