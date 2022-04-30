from django.test import TestCase
from first_criteria.data_processing import vibrations
from first_criteria.models import Engine

# Create your tests here.
class CalculationsModelTest(TestCase):
    def test_one_engine_b_and_d(self):
        engine = Engine.objects.create(
            name='test_engine',
            nu=500,
            N_e=294,
            pe=0.54,
            pz=5.1,
            N_max=16490,
            delta=0.0002,
            D_czvt=13610,
            D_czb=81780
        )
