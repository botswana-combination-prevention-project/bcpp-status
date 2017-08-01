from edc_reference.tests import ReferenceTestHelper as Base


class ReferenceTestHelper(Base):

    def create(self, model=None, visits=None, longitudinal_values=None):
        for visit_code, report_datetime in visits.items():
            self.create_visit(
                report_datetime=report_datetime, timepoint=visit_code)
            self.create_for_model(
                model=model,
                report_datetime=report_datetime, visit_code=visit_code,
                **longitudinal_values.get(visit_code))
