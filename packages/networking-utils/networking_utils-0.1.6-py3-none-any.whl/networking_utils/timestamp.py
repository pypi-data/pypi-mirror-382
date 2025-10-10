from datetime import datetime

class Timestamp():
    
    def __init__(self):
        self.timestamp = ''
        self.now = ''
        self.time_str = ''
        
    def get_timestamp(self):
        self.now = datetime.now()
        self.timestamp = self.now.strftime('%Y_%m_%d_%H_%M_%S')
        self.time_str = self.now.strftime('%Y-%m-%d %H:%M:%S')
