from datetime import datetime


class Current:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            try:
                v = datetime.strptime(v, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                pass
            setattr(self, k, v)
