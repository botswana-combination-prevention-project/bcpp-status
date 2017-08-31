from arrow.arrow import Arrow

from edc_constants.constants import POS

from .values import Values


class ElisaResult(Values):

    """Indirect documentation of HIV status.
    """

    model = 'bcpp_subject.elisahivresult'
    visit_model = 'bcpp_subject.subjectvisit'
    attrs = ['elisa_hiv_result', 'elisa_hiv_result_date']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.longitudinal_refset.order_by('hiv_result_datetime')
        elisa_hiv_result = None
        elisa_hiv_result_datetime = None
        # try to get the first POS
        for index, result in enumerate(self.longitudinal_refset.fieldset('hiv_result')):
            if result == POS:
                elisa_hiv_result = result
                elisa_hiv_result_datetime = self.longitudinal_refset.fieldset(
                    'hiv_result_datetime')[index]
                break
        # if not, get the most recent result (last)
        if not elisa_hiv_result:
            elisa_hiv_result = self.longitudinal_refset.fieldset(
                'hiv_result').last()
            elisa_hiv_result_datetime = self.longitudinal_refset.fieldset(
                'hiv_result_datetime').last()

        self.values.update(elisa_hiv_result=elisa_hiv_result)
        if elisa_hiv_result_datetime:
            self.values.update(elisa_hiv_result_date=Arrow.fromdatetime(
                elisa_hiv_result_datetime).date())
        else:
            self.values.update(elisa_hiv_result_date=None)
        self.values.update(hiv_result=elisa_hiv_result)
        self.values.update(hiv_result_datetime=elisa_hiv_result_datetime)
        self.values.update(elisa_hiv_result=elisa_hiv_result)
        self.values.update(elisa_hiv_result_datetime=elisa_hiv_result_datetime)
