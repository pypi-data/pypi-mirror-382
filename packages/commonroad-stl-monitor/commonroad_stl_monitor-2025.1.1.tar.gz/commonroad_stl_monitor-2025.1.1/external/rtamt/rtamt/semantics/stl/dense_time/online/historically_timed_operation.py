
from rtamt.semantics.abstract_dense_time_online_operation import AbstractDenseTimeOnlineOperation
import rtamt.semantics.stl.dense_time.online.intersection as intersect


class HistoricallyTimedOperation(AbstractDenseTimeOnlineOperation):
    def __init__(self, begin, end):
        self.prev = []
        self.residual_start = float("inf")
        self.max = float("inf")
        self.begin = begin
        self.end = end

    def reset(self):
        pass

    def update(self, sample, *args, **kargs):
        # get inputs
        sample_result = []
        out = self.prev
        self.prev = []

        begin = self.begin
        end = self.end

        if sample:
            # update when the residuals start in this iteration
            self.residual_start = sample[-1][0]
            if out:
                # update the last previous sample with current knowledge
                last_prev = out[len(out) - 1]
                first_now = sample[0]
                del (out[len(out) - 1])
                out.append((last_prev[0], first_now[0] + end, last_prev[2]))

        i = 1
        while len(sample) >= i:
            if i == 1 and sample[0][0] == 0 and begin > 0:
                out.append((0, sample[0][0] + begin, float('inf')))

            if i == len(sample):
                b = (sample[i - 1][0] + begin, sample[i - 1][0] + end, sample[i - 1][1])
            else:
                b = (sample[i - 1][0] + begin, sample[i][0] + end, sample[i - 1][1])

            if not out:
                out.append(b)
            else:
                a = out[len(out) - 1]
                while (a[2] > b[2]) and (b[0] < a[0]):
                    del (out[len(out) - 1])
                    a = out[len(out) - 1]
                if not intersect.intersects(a[0], a[1], b[0], b[1]):
                    out.append(b)
                else:
                    if a[2] <= b[2]:
                        out.append((a[1], b[1], b[2]))
                    else:
                        del (out[len(out) - 1])
                        if b[0] > a[0]:
                            out.append((a[0], b[0], a[2]))
                        out.append((b[0], b[1], b[2]))
            i = i + 1

        prev = float("nan")

        last = []
        for i, b in enumerate(out):
            if self.residual_start >= b[1]:
                last = [b[0], b[2]]
                if b[2] != prev or i == len(out) - 1:
                    sample_result.append(last)
            elif b[0] <= self.residual_start < b[1]:
                last = [b[0], b[2]]
                if b[2] != prev or i == len(out) - 1:
                    sample_result.append(last)
                if self.residual_start > b[0]:
                    last = [self.residual_start, b[2]]
                    self.prev.append((self.residual_start, b[1], b[2]))
            else:
                self.prev.append(b)
            prev = b[2]

        if last:
            if not sample_result:
                sample_result.append(last)
            else:
                if last[0] > sample_result[-1][0]:
                    sample_result.append(last)

        return sample_result

    def update_final(self, sample, *args, **kargs):
        ans = []

        ans = self.update(sample, *args, **kargs)

        out = self.prev

        for i, b in enumerate(out):
            ans.append([b[0], b[2]])
        return ans
