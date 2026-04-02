# salary_calc.py
class SalaryCalculator:
    @staticmethod
    def calculate(salary, norm_hours, day_entries):
        """
        day_entries: список из 31 элемента (индекс 1..31) или None, каждый элемент = (regular, overtime, weekend)
        Возвращает словарь с платежами и итогом
        """
        if norm_hours <= 0:
            return {'error': 'Норма часов должна быть больше нуля'}

        total_regular_hours = 0
        total_overtime_payment = 0
        total_weekend_payment = 0

        # Сначала посчитаем общее количество обычных часов
        for day in range(1, 32):
            if day in day_entries:
                regular, overtime, weekend = day_entries[day]
                total_regular_hours += regular
            else:
                continue

        # Оплата обычных часов (пропорционально норме)
        if total_regular_hours < norm_hours:
            hourly_rate = salary / norm_hours
            regular_payment = total_regular_hours * hourly_rate
        else:
            regular_payment = salary
            hourly_rate = salary / norm_hours

        # Теперь считаем сверхурочные и выходные по дням
        for day in range(1, 32):
            if day not in day_entries:
                continue
            regular, overtime, weekend = day_entries[day]
            # Сверхурочные в этот день
            if overtime > 0:
                first_two = min(2.0, overtime)
                rest = max(0.0, overtime - 2.0)
                total_overtime_payment += first_two * hourly_rate * 1.5 + rest * hourly_rate * 2.0
            # Выходные в этот день
            total_weekend_payment += weekend * hourly_rate * 2.0

        total = regular_payment + total_overtime_payment + total_weekend_payment

        return {
            'hourly_rate': round(hourly_rate, 2),
            'regular_payment': round(regular_payment, 2),
            'overtime_payment': round(total_overtime_payment, 2),
            'weekend_payment': round(total_weekend_payment, 2),
            'total': round(total, 2),
            'error': None
        }
        