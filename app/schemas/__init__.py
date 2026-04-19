from app.schemas.province import ProvinceCreate, ProvinceUpdate, ProvinceResponse
from app.schemas.district import DistrictCreate, DistrictUpdate, DistrictResponse
from app.schemas.academic_years import AcademicYearCreate, AcademicYearUpdate, AcademicYearResponse
from app.schemas.subject_category import SubjectCategoryCreate, SubjectCategoryUpdate, SubjectCategoryResponse
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.level import LevelCreate, LevelUpdate, LevelResponse
from app.schemas.fee import FeeCreate, FeeUpdate, FeeResponse
from app.schemas.discount import DiscountCreate, DiscountUpdate, DiscountResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from app.schemas.teacher_assignment import TeacherAssignmentCreate, TeacherAssignmentUpdate, TeacherAssignmentResponse
from app.schemas.teaching_log import TeachingLogCreate, TeachingLogUpdate, TeachingLogResponse
from app.schemas.salary_payment import (
    SalaryPaymentCreate,
    SalaryPaymentUpdate,
    SalaryPaymentResponse,
    SalaryPaymentReceiptRequest,
)
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.schemas.registration import (
    RegistrationCreate, RegistrationUpdate, RegistrationResponse,
    RegistrationDetailCreate, RegistrationDetailUpdate, RegistrationDetailResponse,
)
from app.schemas.tuition_payment import TuitionPaymentCreate, TuitionPaymentUpdate, TuitionPaymentResponse
from app.schemas.evaluation import (
    EvaluationCreate, EvaluationUpdate, EvaluationResponse,
    EvaluationDetailCreate, EvaluationDetailUpdate, EvaluationDetailResponse,
)
from app.schemas.expense_category import ExpenseCategoryCreate, ExpenseCategoryUpdate, ExpenseCategoryResponse
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse
from app.schemas.donation import (
    DonorCreate, DonorUpdate, DonorResponse,
    DonationCreate, DonationUpdate, DonationResponse,
)
