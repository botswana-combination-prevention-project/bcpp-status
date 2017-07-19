from edc_constants.constants import POS

from .values import Values


class ElisaResult(Values):

    """Indirect documentation of HIV status.
    """

    model = 'bcpp_subject.elisahivresult'
    attrs = ['elisa_hiv_result', 'elisa_hiv_result_date']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.longitudinal_refset.order_by('hiv_result_datetime')
        elisa_hiv_result = None
        elisa_hiv_result_date = None
        # try to get the first POS
        for index, result in enumerate(self.longitudinal_refset.fieldset('hiv_result')):
            if result == POS:
                elisa_hiv_result = result
                elisa_hiv_result_date = self.longitudinal_refset.fieldset(
                    'hiv_result_datetime')[index]
                break
        # if not, get the most recent result (last)
        if not elisa_hiv_result:
            elisa_hiv_result = self.longitudinal_refset.fieldset(
                'hiv_result').last()
            elisa_hiv_result_date = self.longitudinal_refset.fieldset(
                'hiv_result_datetime').last()
        self.values.update(elisa_hiv_result=elisa_hiv_result)
        self.values.update(elisa_hiv_result_date=elisa_hiv_result_date)
        self.values.update(hiv_result=elisa_hiv_result)
        self.values.update(hiv_result_datetime=elisa_hiv_result_date)
