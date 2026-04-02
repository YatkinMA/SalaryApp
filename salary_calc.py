# salary_calc.py
class SalaryCalculator:
    @staticmethod
    def calculate(salary, norm_hours, regular_hours, overtime_hours, weekend_hours):
        if norm_hours <= 0:
            return {
                'hourly_rate': 0,
                'regular_payment': 0,
                'overtime_payment': 0,
                'weekend_payment': 0,
                'total': 0,
                'error': 'Норма часов должна быть больше нуля'
            }
        hourly_rate = salary / norm_hours

        # Обычные часы
        if regular_hours < norm_hours:
            regular_payment = regular_hours * hourly_rate
        else:
            regular_payment = salary  # полный оклад при отработке нормы или больше (сверхурочные отдельно)

        # Сверхурочные (первые 2 часа по 1.5, остальные по 2)
        overtime_payment = 0
        if overtime_hours > 0:
            first_two = min(2.0, overtime_hours)
            rest = max(0.0, overtime_hours - 2.0)
            overtime_payment = first_two * hourly_rate * 1.5 + rest * hourly_rate * 2.0

        # Выходные
        weekend_payment = weekend_hours * hourly_rate * 2.0

        total = regular_payment + overtime_payment + weekend_payment

        return {
            'hourly_rate': round(hourly_rate, 2),
            'regular_payment': round(regular_payment, 2),
            'overtime_payment': round(overtime_payment, 2),
            'weekend_payment': round(weekend_payment, 2),
            'total': round(total, 2),
            'error': None
        }
        