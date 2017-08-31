from arrow.arrow import Arrow

from edc_constants.constants import POS, NEG, DECLINED

from .values import Values


class HivResult(Values):

    """Fetches the first POS from the history of HivResult,
    if one exists, or with a NEG result from today, if it exists.
    """

    model = 'bcpp_subject.hivresult'
    visit_model = 'bcpp_subject.subjectvisit'
    attrs = ['today_hiv_result', 'today_hiv_result_date', 'declined']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        declined = None
        self.longitudinal_refset.order_by('hiv_result_datetime')
        hiv_result = None
        hiv_result_datetime = None
        for index, result in enumerate(self.longitudinal_refset.fieldset('hiv_result')):
            if result == POS:
                hiv_result = result
                hiv_result_datetime = self.longitudinal_refset.fieldset(
                    'hiv_result_datetime')[index]
                break
        if not hiv_result:
            # try to get the last NEG or DECLINED
            self.longitudinal_refset.order_by('-report_datetime')
            for index, result in enumerate(self.longitudinal_refset.fieldset('hiv_result')):
                if result in [DECLINED, NEG]:
                    if result == DECLINED:
                        declined = True
                    hiv_result = result
                    hiv_result_datetime = self.longitudinal_refset.fieldset(
                        'hiv_result_datetime')[index]
                    break
        if not hiv_result:
            self.longitudinal_refset.order_by('report_datetime')
            hiv_result = self.longitudinal_refset.fieldset(
                'hiv_result').last()
            hiv_result_datetime = self.longitudinal_refset.fieldset(
                'hiv_result_datetime').last()
        self.values.update(hiv_result=hiv_result)
        self.values.update(hiv_result_datetime=hiv_result_datetime)
        self.values.update(today_hiv_result=hiv_result)
        if hiv_result_datetime:
            self.values.update(today_hiv_result_date=Arrow.fromdatetime(
                hiv_result_datetime).date())
        else:
            self.values.update(today_hiv_result_date=None)
        self.values.update(declined=declined)
