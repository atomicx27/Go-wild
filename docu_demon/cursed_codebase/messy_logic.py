class X:
    def __init__(self, d):
        self.d = d
    def p(self):
        r = []
        for k, v in self.d.items():
            if isinstance(v, list):
                r.extend([str(i) for i in v if i])
            elif v:
                r.append(str(v))
        return "_".join(r)
