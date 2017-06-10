import sys

from django.apps import apps as django_apps

from edc_constants.constants import (
    POS, YES, NEG, NO, NAIVE, UNK, IND)

from .model_values import ModelValues
from .constants import ART_PRESCRIPTION, DEFAULTER, ON_ART


class ValuesSetter:

    def __init__(self, model_values):
        for attr, value in model_values.items():
            if not hasattr(self, attr):
                setattr(self, attr, value)


class SubjectHelper:
    """A class the determines a number of derived variables around
    HIV status and ART status.
    """

    def __init__(self, visit=None, subject_identifier=None, model_values=None, **kwargs):
        self._subject_visits = None
        self.documented_pos = None
        self.documented_pos_date = None
        self.final_arv_status = None
        self.final_hiv_status = None
        self.newly_diagnosed = None
        self.prev_result = None
        self.prev_result_date = None
        self.prev_result_known = None

        if visit:
            self.subject_identifier = visit.subject_identifier
            self.subject_visit = visit
        else:
            self.subject_identifier = subject_identifier
            self.subject_visit = self.subject_visits.last()
        self.survey_schedule = self.subject_visit.survey_schedule_object.field_value
        self.visit_schedule_name = self.subject_visit.visit_schedule_name
        self.schedule_name = self.subject_visit.schedule_name
        self.visit_code = self.subject_visit.visit_code
        for index, subject_visit in enumerate(self.subject_visits):
            value_setter = ValuesSetter(
                model_values or ModelValues(subject_visit).__dict__)
            setattr(self, subject_visit.visit_code, value_setter)
            if index == 0:
                self.baseline = value_setter
            if subject_visit == self.subject_visit:
                self.current = value_setter

#         self.baseline = ValuesSetter(
#             model_values or ModelValues(self.subject_visit, baseline=True).__dict__)
#         self.current = ValuesSetter(
#             model_values or ModelValues(self.subject_visit).__dict__)
        if self.current.result_recorded_document == ART_PRESCRIPTION:
            self.current.arv_evidence = YES

        self._prepare_documented_status_and_date()
        self._prepare_final_hiv_status()
        self._prepare_final_arv_status()
        self._prepare_previous_status_date_and_awareness()
        if self.previous_visit:
            previous_helper = self.__class__(visit=self.previous_visit)
            previous_result = previous_helper.final_hiv_status
            previous_result_known = YES if previous_helper.final_hiv_status else NO
            previous_result_date = previous_helper.final_hiv_status_date
            if not self.prev_result_date:
                self.prev_result = previous_result
                self.prev_result_known = previous_result_known
                self.prev_result_date = previous_result_date
            elif (previous_result_date
                    and previous_result_date > self.prev_result_date):
                self.prev_result = previous_result
                self.prev_result_known = previous_result_known
                self.prev_result_date = previous_result_date

        self.indeterminate = (
            self.current.today_hiv_result == IND
            and self.current.elisa_hiv_result not in [POS, NEG])

        self.newly_diagnosed = (
            self.final_hiv_status == POS and self.prev_result_known != YES)
        self.known_positive = (
            self.prev_result == POS and self.prev_result_known == YES)
        self.has_tested = YES if YES in [
            self.baseline.has_tested, self.current.has_tested] else NO

    @property
    def subject_visits(self):
        if not self._subject_visits:
            SubjectVisit = django_apps.get_model(
                *'bcpp_subject.subjectvisit'.split('.'))
            self._subject_visits = SubjectVisit.objects.filter(
                subject_identifier=self.subject_identifier).order_by('report_datetime')
        return self._subject_visits

    @property
    def previous_visit(self):
        visits = [obj for obj in self.subject_visits]
        for index, visit in enumerate(visits):
            if visit == self.subject_visit:
                if index > 0:
                    try:
                        return visits[index - 1]
                    except IndexError:
                        return None
        return None

    @property
    def options(self):
        options = self.__dict__
        options.update(
            final_arv_status_baseline=self.final_arv_status_baseline,
            naive_at_baseline=self.naive_at_baseline,
            defaulter_at_baseline=self.defaulter_at_baseline,
            final_hiv_status_date=self.final_hiv_status_date,
            prev_results_discordant=self.prev_results_discordant,
        )
        return options

    @property
    def final_arv_status_baseline(self):
        baseline_helper = self.__class__(visit=self.baseline.subject_visit)
        return baseline_helper.final_arv_status

    @property
    def naive_at_baseline(self):
        return self.final_arv_status_baseline == NAIVE

    @property
    def defaulter_at_baseline(self):
        baseline_helper = self.__class__(visit=self.baseline.subject_visit)
        return baseline_helper.final_arv_status == DEFAULTER

    @property
    def final_hiv_status_date(self):
        """Returns the oldest POS result date or the most recent
        NEG result date.
        """
        final_hiv_status_date = self._final_hiv_status_date_if_pos
        if not final_hiv_status_date:
            final_hiv_status_date = self._final_hiv_status_date_if_neg
        return final_hiv_status_date

    @property
    def prev_results_discordant(self):
        if self.current.result_recorded and self.current.recorded_hiv_result:
            return self.current.result_recorded != self.current.recorded_hiv_result
        return False

    @property
    def best_prev_result_date(self):
        """Returns best date after changing result based on ARV status.
        """
        if self.current.recorded_hiv_result == POS:
            best_prev_result_date = self.current.recorded_hiv_result_date
        elif self.current.result_recorded == POS:
            best_prev_result_date = self.current.result_recorded_date
        else:
            best_prev_result_date = None
        return best_prev_result_date

    def _prepare_previous_status_date_and_awareness(self):
        """Prepares prev_result, prev_result_date, and prev_result_known.

        * Get the POS prev_result or the NEG result.
        * If final and prev are discordant and prev_results_discordant,
          select the prev_result that equals the final result
        """
        self._update_prev_result_if(POS)
        if not self.prev_result:
            self._update_prev_result_if(NEG)
        if self.prev_results_discordant and self.final_hiv_status != self.prev_result:
            self._update_prev_result_if(self.final_hiv_status)
        if not self.prev_result:
            self._update_prev_result_if(None)
        self._previous_status_date_and_awareness_exceptions()

    def _update_prev_result_if(self, result=None):
        """Updates the prev_result attributes based on the value of `result`.

        The caller is responsible for handling recorded_hiv_result
        and result_recorded being discordant.
        """
        # FIXME: to be final_hiv_status at baseline or previous
        # at baseline
        if result and self.current.recorded_hiv_result == result:
            self.prev_result = result
            self.prev_result_date = self.current.recorded_hiv_result_date
            self.prev_result_known = YES
        elif result and self.current.result_recorded == result:
            self.prev_result = result
            self.prev_result_date = self.current.result_recorded_date
            self.prev_result_known = YES
        elif not result:
            self.prev_result = None
            self.prev_result_date = None
            self.prev_result_known = None

    def _previous_status_date_and_awareness_exceptions(self):
        """Overwrites invalid result sequence and/or derives from
        arv status if possible.
        """
        # evidence of ARV's implies POS previous result
        if (self.final_arv_status in (DEFAULTER, ON_ART)
                and (self.prev_result == NEG or not self.prev_result)):
            self.prev_result = POS
            self.prev_result_date = self.best_prev_result_date
            self.prev_result_known = YES
        # if finally NEG, a known previous result must be wrong, so flip to NEG
        if self.final_hiv_status == NEG and self.prev_result_known == YES:
            self.prev_result = NEG
            # self.debug.append('changed prev_result POS->NEG')

    def _prepare_final_arv_status(self):
        self.final_arv_status = None
        if self.final_hiv_status == POS:
            if ((not self.current.ever_taken_arv or self.current.ever_taken_arv == NO)
                    and (self.current.arv_evidence == NO or not self.current.arv_evidence)):
                self.final_arv_status = NAIVE
            elif ((self.current.ever_taken_arv == YES or self.current.arv_evidence == YES)
                  and self.current.on_arv == NO):
                self.final_arv_status = DEFAULTER
            elif ((self.current.arv_evidence == YES or self.current.ever_taken_arv == YES)
                  and self.current.on_arv == YES):
                self.final_arv_status = ON_ART
            elif (self.current.arv_evidence == YES
                  and not self.current.on_arv
                  and not self.current.ever_taken_arv):
                self.final_arv_status = ON_ART
            else:
                sys.stdout.write(
                    'Cannot determine final_arv_status for {}. '
                    'Got ever_taken_arv={}, on_arv={}, arv_evidence={}'.format(
                        self.subject_identifier,
                        self.current.ever_taken_arv,
                        self.current.on_arv,
                        self.current.arv_evidence))

    def _prepare_documented_status_and_date(self):
        if self.current.recorded_hiv_result == POS:
            self.documented_pos = YES
            self.documented_pos_date = self.current.recorded_hiv_result_date
        elif self.current.other_record == YES and self.current.result_recorded == POS:
            self.documented_pos = YES
            self.documented_pos_date = self.current.result_recorded_date
        elif self.current.arv_evidence == YES:
            self.documented_pos = YES
            self.documented_pos_date = None
        elif (self.current.recorded_hiv_result not in (POS, NEG) and
                not (self.current.other_record == YES and self.current.result_recorded == POS)):
            self.documented_pos = NO
            self.documented_pos_date = None
        else:
            self.documented_pos = NO
            self.documented_pos_date = None

    def _prepare_final_hiv_status(self):
        if self.current.elisa_hiv_result in (POS, NEG):
            self.final_hiv_status = self.current.elisa_hiv_result
        elif self.current.today_hiv_result in (POS, NEG):
            self.final_hiv_status = self.current.today_hiv_result
        elif self.documented_pos == YES:
            self.final_hiv_status = POS
        else:
            self.final_hiv_status = UNK

    @property
    def _final_hiv_status_date_if_pos(self):
        """Returns oldest date if final result is POS.
        """
        final_hiv_status_date = None
        if self.final_hiv_status == POS:
            if self.prev_result_known == YES and self.prev_result == POS:
                final_hiv_status_date = self.prev_result_date
            elif self.current.today_hiv_result == POS:
                final_hiv_status_date = self.current.today_hiv_result_date
            elif self.current.elisa_hiv_result == POS:
                final_hiv_status_date = self.current.elisa_hiv_result_date
        return final_hiv_status_date

    @property
    def _final_hiv_status_date_if_neg(self):
        """Returns most recent date if final result is NEG.
        """
        final_hiv_status_date = None
        if self.final_hiv_status == NEG:
            if self.current.elisa_hiv_result_date:
                final_hiv_status_date = self.current.elisa_hiv_result_date
            elif self.current.today_hiv_result_date:
                final_hiv_status_date = self.current.today_hiv_result_date
            elif self.prev_result_known == YES and self.prev_result == NEG:
                final_hiv_status_date = self.prev_result_date
        return final_hiv_status_date
