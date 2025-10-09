"""Schema definitions for Nmbrs package"""

DATEFORMAT = '%Y%m%d'

from .address import AddressGet, AddressCreate
from .bank import BankGet, BankCreate, BankUpdate, BankDelete
from .contracts import ContractGet, ContractCreate, ContractUpdate, ContractDelete
from .department import EmployeeDepartmentGet, DepartmentCreate, EmployeeDepartmentUpdate, DepartmentGet
from .employees import EmployeeGet, EmployeeCreate, EmployeeUpdate, EmployeeDelete
from .employment import EmploymentGet, EmploymentCreate, EmploymentUpdate, EmploymentDelete
from .function import FunctionGet, FunctionUpdate
from .hours import FixedHoursGet, FixedHoursCreate, FixedHoursUpdate, HoursDelete, VariableHoursGet, VariableHoursCreate, VariableHoursUpdate
from .salary import SalaryGet, SalaryCreate
from .manager import ManagerGet, ManagerBasicGet, EmployeeManagerGet, ManagerHistoricBasicGet, ManagerCreate, ManagerUpdate, ManagerDelete, UpdateEmployeeManager
from .salary import SalaryGet, SalaryCreate, SalaryUpdate, SalaryDelete
from .wagecomponents import FixedWageComponentGet, FixedWageComponentCreate, FixedWageComponentUpdate, WageComponentDelete, VariableWageComponentGet, VariableWageComponentCreate, VariableWageComponentUpdate
from .wage_tax import WageTaxGet, WageTaxUpdate


__all__ = [
    'DATEFORMAT',
    'AddressGet', 'AddressCreate',
    'BankGet', 'BankCreate', 'BankUpdate', 'BankDelete',
    'ContractGet', 'ContractCreate', 'ContractUpdate', 'ContractDelete',
    'EmployeeDepartmentGet', 'DepartmentCreate', 'EmployeeDepartmentUpdate', 'DepartmentGet',
    'EmployeeGet', 'EmployeeCreate', 'EmployeeUpdate', 'EmployeeDelete',
    'EmploymentGet', 'EmploymentCreate', 'EmploymentUpdate', 'EmploymentDelete',
    'FunctionGet', 'FunctionUpdate',
    'FixedHoursGet', 'FixedHoursCreate', 'FixedHoursUpdate', 'HoursDelete',
    'VariableHoursGet', 'VariableHoursCreate', 'VariableHoursUpdate',
    'ManagerGet', 'ManagerBasicGet', 'EmployeeManagerGet', 'ManagerHistoricBasicGet',
    'ManagerCreate', 'ManagerUpdate', 'ManagerDelete', 'UpdateEmployeeManager',
    'SalaryGet', 'SalaryCreate',
    'FixedWageComponentGet', 'FixedWageComponentCreate', 'FixedWageComponentUpdate', 'WageComponentDelete',
    'VariableWageComponentGet', 'VariableWageComponentCreate', 'VariableWageComponentUpdate',
    'WageTaxGet', 'WageTaxUpdate'
]
