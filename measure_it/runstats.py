import stats

class RunningStats(object):

    stats = dict()
    
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.elapsed = stats.running_sum()
        self.count = stats.running_sum()
        self.last_elapsed = None
        self.last_count = None
        
    def record(self, count, elapsed):
        self.points += 1
        self.last_elapsed = self.elapsed.send(elapsed)
        self.last_count = self.count.send(count)
        
    @classmethod
    def metric(cls, name, count, elapsed):
        try:
            self = cls.stats[name]
        except KeyError:
            self = cls.stats[name] = cls(name)
        
        self.record(count, elapsed)