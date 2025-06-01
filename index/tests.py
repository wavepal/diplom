from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date

from .models import Form, Questions, Choices, Answer, Responses, RegionMedCenter, MedCenterGroup

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            city='ASTANA',
            med_center='Test Center',
            date_of_birth=date(1990, 1, 1),
            gender='M',
            role='USER'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.city, 'ASTANA')
        self.assertEqual(self.user.get_city_display(), 'Астана')
        self.assertEqual(self.user.med_center, 'Test Center')
        self.assertEqual(self.user.gender, 'M')
        self.assertEqual(self.user.role, 'USER')

    def test_user_age_calculation(self):
        today = date.today()
        expected_age = today.year - 1990 - ((today.month, today.day) < (1, 1))
        self.assertEqual(self.user.age(), expected_age)

    def test_user_role_methods(self):
        self.assertTrue(self.user.is_regular_user())
        self.assertFalse(self.user.is_admin())
        self.assertFalse(self.user.is_trainer())
        self.assertFalse(self.user.is_manager())
        
        # Change role and test again
        self.user.role = 'ADMIN'
        self.user.save()
        self.assertTrue(self.user.is_admin())
        self.assertFalse(self.user.is_regular_user())

class RegionMedCenterTests(TestCase):
    def setUp(self):
        self.group = MedCenterGroup.objects.create(
            name='Test Group',
            description='Test Description'
        )
        self.med_center = RegionMedCenter.objects.create(
            region='ASTANA',
            med_center='Test Center',
            address='Test Address',
            group=self.group
        )

    def test_region_med_center_creation(self):
        self.assertEqual(self.med_center.region, 'ASTANA')
        self.assertEqual(self.med_center.med_center, 'Test Center')
        self.assertEqual(self.med_center.address, 'Test Address')
        self.assertEqual(self.med_center.group, self.group)
        self.assertEqual(str(self.med_center), 'Астана - Test Center')

    def test_get_med_centers_by_region(self):
        centers = RegionMedCenter.get_med_centers_by_region('ASTANA')
        self.assertEqual(centers.count(), 1)
        self.assertEqual(centers.first(), self.med_center)

class FormModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='formcreator',
            email='creator@example.com',
            password='password123'
        )
        self.form = Form.objects.create(
            code='TEST123',
            title='Test Form',
            description='Test Description',
            creator=self.user,
            is_active=True
        )
        
        # Create question and choices
        self.choice1 = Choices.objects.create(choice='Option 1', is_answer=True, scores=5)
        self.choice2 = Choices.objects.create(choice='Option 2', is_answer=False, scores=0)
        
        self.question = Questions.objects.create(
            question='Test Question?',
            question_type='multiple_choice',
            required=True,
            score=5,
            order=1
        )
        self.question.choices.add(self.choice1, self.choice2)
        self.form.questions.add(self.question)

    def test_form_creation(self):
        self.assertEqual(self.form.code, 'TEST123')
        self.assertEqual(self.form.title, 'Test Form')
        self.assertEqual(self.form.creator, self.user)
        self.assertTrue(self.form.is_active)
        self.assertEqual(self.form.questions.count(), 1)

    def test_is_creator(self):
        self.assertTrue(self.form.is_creator(self.user))
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )
        self.assertFalse(self.form.is_creator(other_user))

class ResponsesModelTests(TestCase):
    def setUp(self):
        # Create creator
        self.creator = User.objects.create_user(
            username='formcreator',
            email='creator@example.com',
            password='password123'
        )
        
        # Create responder
        self.responder = User.objects.create_user(
            username='responder',
            email='responder@example.com',
            password='password123',
            city='ALMATY',
            med_center='City Hospital',
            date_of_birth=date(1995, 5, 15),
            gender='F'
        )
        
        # Create form
        self.form = Form.objects.create(
            code='RESP123',
            title='Response Test Form',
            description='Test Description',
            creator=self.creator,
            is_active=True,
            authenticated_responder=True
        )
        
        # Create question and answer
        self.question = Questions.objects.create(
            question='Test Question?',
            question_type='text',
            required=True
        )
        self.form.questions.add(self.question)
        
        self.answer = Answer.objects.create(
            answer='Test Answer',
            answer_to=self.question
        )
        
        # Create response
        self.response = Responses.objects.create(
            response_code='R12345',
            response_to=self.form,
            responder_ip='127.0.0.1',
            responder=self.responder
        )
        self.response.response.add(self.answer)

    def test_response_creation(self):
        self.assertEqual(self.response.response_code, 'R12345')
        self.assertEqual(self.response.response_to, self.form)
        self.assertEqual(self.response.responder, self.responder)
        self.assertEqual(self.response.response.count(), 1)
        self.assertEqual(self.response.response.first(), self.answer)

    def test_user_data_propagation(self):
        # Test that user data is properly copied to response
        self.assertEqual(self.response.responder_username, 'responder')
        self.assertEqual(self.response.responder_email, 'responder@example.com')
        self.assertEqual(self.response.responder_gender, 'F')
        self.assertEqual(self.response.responder_city, 'ALMATY')
        self.assertEqual(self.response.responder_med, 'City Hospital')
        self.assertEqual(self.response.responder_birth_date, date(1995, 5, 15))
        
        # Test display methods
        self.assertEqual(self.response.get_city_display(), 'Алматы')
        self.assertEqual(self.response.get_gender_display(), 'Женский')
