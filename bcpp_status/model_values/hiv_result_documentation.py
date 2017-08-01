from edc_constants.constants import POS

from .values import Values


class HivResultDocumentation(Values):

    """Indirect documentation of HIV status.
    """

    model = 'bcpp_subject.hivresultdocumentation'
    attrs = ['result_recorded', 'result_recorded_date',
             'result_recorded_document']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        result_recorded = None
        result_recorded_date = None
        result_recorded_document = None
        self.longitudinal_refset.order_by('result_date')
        for index, result in enumerate(self.longitudinal_refset.fieldset('result_recorded')):
            if result == POS:
                result_recorded = result
                result_recorded_date = (
                    self.longitudinal_refset.fieldset('result_date')[index])
                result_recorded_document = (
                    self.longitudinal_refset.fieldset('result_doc_type')[index])
                break
        # if not, get the most recent result (last)
        if not result_recorded:
            result_recorded = self.longitudinal_refset.fieldset(
                'result_recorded').last()
            result_recorded_date = self.longitudinal_refset.fieldset(
                'result_date').last()
            result_recorded_document = self.longitudinal_refset.fieldset(
                'result_doc_type').last()

        self.values.update(result_recorded=result_recorded)
        self.values.update(result_recorded_date=result_recorded_date)
        self.values.update(result_recorded_document=result_recorded_document)
        self.values.update(result_date=result_recorded_date)
        self.values.update(result_doc_type=result_recorded_document)
