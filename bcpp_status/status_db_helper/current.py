from datetime import datetime


class Current:
    def __init__(self, today_hiv_result=None, **kwargs):
        self.today_hiv_result = today_hiv_result
        for k, v in kwargs.items():
            try:
                v = datetime.strptime(v, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                pass
            setattr(self, k, v)

    def __str__(self):
        return self.today_hiv_result
