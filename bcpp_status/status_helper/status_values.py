from ..model_data import ModelData


class StatusValues:

    model_data_cls = ModelData

    def __init__(self, visit=None):
        model_data = self.model_data_cls(
            subject_identifier=visit.subject_identifier,
            report_datetime=visit.report_datetime,
            visit_model=visit.model,
            app_label=visit.model.split('.')[0])
        self.subject_identifier = visit.subject_identifier
        self.report_datetime = visit.report_datetime
        self.visit_code = visit.visit_code
        self.subject_visit = visit
        for attr, value in model_data:
            if not hasattr(self, attr):
                setattr(self, attr, value)

    def __repr__(self):
        return (f'{self.__class__.__name__}(subject_identifier={self.subject_identifier},'
                f'visit_code={self.visit_code},report_datetime={self.report_datetime})')
