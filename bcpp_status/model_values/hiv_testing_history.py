from .values import Values


class HivTestingHistory(Values):

    model = 'bcpp_subject.hivtestinghistory'
    visit_model = 'bcpp_subject.subjectvisit'
    attrs = ['self_reported_result', 'has_tested', 'other_record']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.longitudinal_refset.order_by('report_datetime')
        verbal_hiv_result = self.longitudinal_refset.fieldset(
            'verbal_hiv_result').last()
        has_tested = self.longitudinal_refset.fieldset(
            'has_tested').last()
        other_record = self.longitudinal_refset.fieldset(
            'other_record').last()
        self.values.update(verbal_hiv_result=verbal_hiv_result)
        self.values.update(self_reported_result=verbal_hiv_result)
        self.values.update(has_tested=has_tested)
        self.values.update(other_record=other_record)
