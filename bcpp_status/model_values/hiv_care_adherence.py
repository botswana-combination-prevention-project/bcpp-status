from edc_constants.constants import NOT_APPLICABLE, DWTA, NO

from .values import Values


class HivCareAdherence(Values):

    model = 'bcpp_subject.hivcareadherence'
    visit_model = 'bcpp_subject.subjectvisit'
    attrs = ['arv_evidence', 'ever_taken_arv', 'on_arv']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        arv_evidence = self.longitudinal_refset.fieldset(
            'arv_evidence').last()
        if arv_evidence == NOT_APPLICABLE:
            arv_evidence = None

        ever_taken_arv = self.longitudinal_refset.fieldset(
            'ever_taken_arv').last()
        if ever_taken_arv == DWTA:
            ever_taken_arv = NO

        on_arv = self.longitudinal_refset.fieldset('on_arv').last()
        if on_arv == NOT_APPLICABLE:
            on_arv = None
        elif on_arv == DWTA:
            on_arv = NO

        self.values.update(arv_evidence=arv_evidence)
        self.values.update(ever_taken_arv=ever_taken_arv)
        self.values.update(on_arv=on_arv)
