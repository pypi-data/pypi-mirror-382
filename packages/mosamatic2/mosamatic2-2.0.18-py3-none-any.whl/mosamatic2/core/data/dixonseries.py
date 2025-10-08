from mosamatic2.core.data.filedata import FileData


class DixonSeries(FileData):
    def __init__(self):
        super(DixonSeries, self).__init__()
        self._series = {'ip': None, 'op': None, 'water': None, 'fat': None}

    def ip(self):
        return self._series['ip']
    
    def op(self):
        return self._series['op']
    
    def water(self):
        return self._series['water']
    
    def fat(self):
        return self._series['fat']
    
    def load(self):
        pass