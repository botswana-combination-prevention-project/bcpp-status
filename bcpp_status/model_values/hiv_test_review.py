from edc_constants.constants import POS

from .values import Values


class HivTestReview(Values):

    """Direct documentation of HIV status.
    """

    model = 'bcpp_subject.hivtestreview'
    attrs = ['recorded_hiv_result', 'recorded_hiv_result_date']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.longitudinal_refset.order_by('hiv_test_date')
        recorded_hiv_result = None
        recorded_hiv_result_date = None
        for index, result in enumerate(
                self.longitudinal_refset.fieldset('recorded_hiv_result')):
            if result == POS:
                recorded_hiv_result = result
                recorded_hiv_result_date = self.longitudinal_refset.fieldset(
                    'hiv_test_date')[index]
                break
        if not recorded_hiv_result:
            recorded_hiv_result = self.longitudinal_refset.fieldset(
                'recorded_hiv_result').last()
            recorded_hiv_result_date = self.longitudinal_refset.fieldset(
                'hiv_test_date').last()

        self.values.update(recorded_hiv_result=recorded_hiv_result)
        self.values.update(recorded_hiv_result_date=recorded_hiv_result_date)
        self.values.update(hiv_test_date=recorded_hiv_result_date)
