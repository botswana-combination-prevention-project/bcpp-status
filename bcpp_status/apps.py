from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'bcpp_status'

    models = dict(
        elisahivresult='bcpp_subject.elisahivresult',
        hivcareadherence='bcpp_subject.hivcareadherence',
        hivresult='bcpp_subject.hivresult',
        hivresultdocumentation='bcpp_subject.hivresultdocumentation',
        hivtestinghistory='bcpp_subject.hivtestinghistory',
        hivtestreview='bcpp_subject.hivtestreview',
        subjectvisit='bcpp_subject.subjectvisit',
    )
