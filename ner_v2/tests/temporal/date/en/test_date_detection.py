from __future__ import absolute_import

import datetime

import mock
import pytz
from django.test import TestCase

from ner_v2.detectors.temporal.date.date_detection import DateAdvancedDetector


class DateDetectionTest(TestCase):
    def setUp(self):
        self.entity_name = 'date'
        self.timezone = pytz.timezone('UTC')
        self.now_date = datetime.datetime.now(tz=self.timezone)

    def test_en_date_detection_date_range_ddth_of_mmm_to_ddth(self):
        """
        Date detection for pattern '2nd jan to 5th'
        """
        message = '2nd jan to 5th'
        # If we run
        day1 = 2
        day2 = 5
        month = 1
        year1 = self.now_date.year
        year2 = self.now_date.year
        if self.now_date.month > month or (self.now_date.month == month and self.now_date.day > day1):
            year1 += 1
            year2 += 1

        date_detector_object = DateAdvancedDetector(entity_name=self.entity_name, language='en')
        date_dicts, original_texts = date_detector_object.detect_entity(message)

        self.assertIn({
            'normal': False,
            'start_range': True,
            'end_range': False,
            'from': False,
            'to': False, 'value': {'dd': day1, 'mm': month, 'yy': year1, 'type': 'date'}
        }, date_dicts)

        self.assertIn({
            'normal': False,
            'start_range': False,
            'end_range': True,
            'from': False,
            'to': False,
            'value': {'dd': day2, 'mm': month, 'yy': year2, 'type': 'date'}
        }, date_dicts)

        self.assertEqual(original_texts.count(message), 2)

    @mock.patch('ner_v2.detectors.temporal.date.en.date_detection.get_weekdays_for_month')
    def test_en_date_detection_day_range_for_nth_week_month(self, mocked_get_weekdays_for_month):
        """
        Date detection for pattern 'first week of jan'
        """
        message = 'first week of jan'
        day1 = 1
        day2 = 7
        month = 1
        year = self.now_date.year
        if self.now_date.month > month:
            year += 1

        # TODO: functionality is incorrect, when run after 1st week of Jan, detector must return 1st week of next year
        # if (self.now_date.month == month and self.now_date.day > day1):
        #     year += 1

        mocked_get_weekdays_for_month.return_value = [day1, day2]

        date_detector_object = DateAdvancedDetector(entity_name=self.entity_name, language='en')
        date_dicts, original_texts = date_detector_object.detect_entity(message)

        # TODO: functionality is incorrect, start_range should be True in 1st and end_range should be True in second
        self.assertIn({
            'normal': True,
            'start_range': False,
            'end_range': False,
            'from': False,
            'to': False,
            'value': {'dd': day1, 'mm': month, 'type': 'date', 'yy': year}
        }, date_dicts)

        self.assertIn({
            'normal': True,
            'start_range': False,
            'end_range': False,
            'from': False,
            'to': False,
            'value': {'dd': day2, 'mm': month, 'type': 'date', 'yy': year}
        }, date_dicts)
        self.assertEqual(original_texts.count(message), 2)
