class BPF(str):
    def __init__(self, *args, **kwargs):
        # Initialize string
        super(BPF, self).__init__(*args, **kwargs)

        # Make sure string is not empty
        assert self, "BPF string cannot be empty"

    def __or__(self, other):
        return BPF("(%s) or (%s)" % (self, other))

    def __and__(self, other):
        return BPF("(%s) and (%s)" % (self, other))

    def __invert__(self):
        return BPF("not (%s)" % self)

    def __lt__(self, other):
        return BPF(self & BPF("less %d" % other))

    def __gt__(self, other):
        return BPF(self & BPF("greater %d" % other))


# Define lower case class for ease of use
bpf = BPF
