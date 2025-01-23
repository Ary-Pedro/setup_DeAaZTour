import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup_DeAaZTour.settings')
django.setup()

from django.test import TestCase
from apps.worker.models import Funcionario
from django.core.exceptions import ValidationError
import datetime

class FuncionarioTestCase(TestCase):
    def setUp(self):
        # Set up any initial data for the tests
        Funcionario.objects.create(
            first_name='John',
            last_name='Doe',
            username='johndoe',
            email='johndoe@example.com',
            telefone='(12) 3456-4789',
            data_nascimento='1990-01-01',
            cpf='123.456.789-00'
        )

    def test_model_creation(self):
        """Test that a model instance can be created"""
        instance = Funcionario.objects.get(username='johndoe')
        self.assertEqual(instance.first_name, 'John')
        self.assertEqual(instance.last_name, 'Doe')
        self.assertEqual(instance.email, 'johndoe@example.com')

    def test_model_str(self):
        """Test the __str__ method of the model"""
        instance = Funcionario.objects.get(username='johndoe')
        self.assertEqual(str(instance), 'John Doe')

    def test_model_update(self):
        """Test that a model instance can be updated"""
        instance = Funcionario.objects.get(username='johndoe')
        instance.first_name = 'Jane'
        instance.save()
        self.assertEqual(instance.first_name, 'Jane')

    def test_model_delete(self):
        """Test that a model instance can be deleted"""
        instance = Funcionario.objects.get(username='johndoe')
        instance.delete()
        with self.assertRaises(Funcionario.DoesNotExist):
            Funcionario.objects.get(username='johndoe')

    def test_calculate_age(self):
        """Test the age calculation method"""
        instance = Funcionario.objects.get(username='johndoe')
        today = datetime.date.today()
        birth_date = instance.data_nascimento
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        self.assertEqual(instance.idade, age)

        # Test with a specific birth date to ensure the calculation is correct
        instance.data_nascimento = datetime.date(2002, 1, 1)
        instance.save()
        expected_age = today.year - 2002 - ((today.month, today.day) < (1, 1))
        self.assertEqual(instance.idade, expected_age)

    def test_email_verification(self):
        """Test the email verification method"""
        instance = Funcionario.objects.get(username='johndoe')
        self.assertEqual(instance.verificar_email(), instance.password)

    def test_unique_email(self):
        """Test that the email field is unique"""
        with self.assertRaises(Exception):
            Funcionario.objects.create(
                first_name='Jane',
                last_name='Doe',
                username='janedoe',
                email='johndoe@example.com',  # Same email as 'johndoe'
                telefone='987654321',
                data_nascimento='1992-02-02',
                cpf='987.654.321-00'
            )

    def test_unique_username(self):
        """Test that the username field is unique"""
        with self.assertRaises(Exception):
            Funcionario.objects.create(
                first_name='Jane',
                last_name='Doe',
                username='johndoe',  # Same username as 'johndoe'
                email='janedoe@example.com',
                telefone='987654321',
                data_nascimento='1992-02-02',
                cpf='987.654.321-00'
            )

    def test_invalid_email(self):
        """Test that an invalid email raises a ValidationError"""
        with self.assertRaises(ValidationError):
            Funcionario.objects.create(
                first_name='Jane',
                last_name='Doe',
                username='janedoe',
                email='invalid-email',  # Invalid email format
                telefone='(21) 99589-7270',
                data_nascimento='1992-02-02',
                cpf='987.654.321-00'
            )

    def test_default_values(self):
        """Test the default values of certain fields"""
        instance = Funcionario.objects.get(username='johndoe')
        self.assertEqual(instance.salario, 0)
        self.assertEqual(instance.comissao_acumulada, 0)
        self.assertEqual(instance.departamento, 'Adm')
        self.assertEqual(instance.atividade, 'Ativo')

    def test_is_active_based_on_atividade(self):
        """Test that is_active is set based on atividade"""
        instance = Funcionario.objects.get(username='johndoe')
        instance.atividade = 'Inativo'
        instance.save()
        self.assertFalse(instance.is_active)
        instance.atividade = 'Ativo'
        instance.save()
        self.assertTrue(instance.is_active)