class BPF(str):
    def __or__(self, other):
        assert self and other
        return BPF("(%s) or (%s)" % (self, other))

    def __and__(self, other):
        assert self and other
        return BPF("(%s) and (%s)" % (self, other))

    def __invert__(self):
        assert self
        return BPF("not (%s)" % self)

    def __lt__(self, other):
        assert self and other
        return BPF(self & BPF("less %d" % other))

    def __gt__(self, other):
        assert self and other
        return BPF(self & BPF("greater %d" % other))


# Define lower case class for ease of use
bpf = BPF
