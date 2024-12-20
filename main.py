import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QGridLayout, QComboBox, QMainWindow, QTableWidget, QTableWidgetItem, QMessageBox,
    QFormLayout, QHBoxLayout, QVBoxLayout, QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
import numpy as np


class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Банковская Информатика")
        self.setGeometry(200, 200, 800, 800)
        self.setWindowIcon(QIcon("image.png"))  # Установите иконку приложения

        # Создание вкладок
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Вкладки для кредитного и депозитного калькуляторов
        self.tabs.addTab(CreditCalculatorTab(), "Кредитный калькулятор")
        self.tabs.addTab(DepositCalculatorTab(), "Депозитный калькулятор")

        # Установка стилей для приложения
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px;
                border: 1px solid #ccc;
                margin-right: 5px;
            }
            QTabBar::tab:selected {
                background-color: #fff;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QTableWidget {
                border: 1px solid #ccc;
                gridline-color: #ccc;
            }
        """)


class CreditCalculatorTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Группа для формы ввода
        form_group = QGroupBox("Параметры кредита")
        form_layout = QFormLayout()

        self.payment_type = QComboBox()
        self.payment_type.addItems(["Дифференцированный", "Аннуитетный"])
        self.payment_type.setToolTip("Выберите тип платежа")
        form_layout.addRow("Вид платежа:", self.payment_type)

        self.loan_amount = QLineEdit()
        self.loan_amount.setPlaceholderText("Введите сумму кредита")
        self.loan_amount.setToolTip("Сумма кредита в рублях")
        form_layout.addRow("Сумма в рублях:", self.loan_amount)

        self.loan_term = QLineEdit()
        self.loan_term.setPlaceholderText("Введите срок кредита")
        self.loan_term.setToolTip("Срок кредита в месяцах")
        form_layout.addRow("Срок в месяцах:", self.loan_term)

        self.interest_rate = QLineEdit()
        self.interest_rate.setPlaceholderText("Введите процентную ставку")
        self.interest_rate.setToolTip("Годовая процентная ставка")
        form_layout.addRow("Процентная ставка:", self.interest_rate)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Кнопка "Рассчитать"
        self.calculate_button = QPushButton("Рассчитать")
        self.calculate_button.clicked.connect(self.calculate_loan)
        layout.addWidget(self.calculate_button)

        # Результаты
        self.result_label = QLabel("Результаты:")
        self.result_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.result_label)

        # График и таблица рядом в центре
        bottom_layout = QHBoxLayout()

        # Добавляем отступы для центрирования
        spacer_left = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        spacer_right = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        bottom_layout.addItem(spacer_left)

        # График
        self.figure, self.ax = plt.subplots(figsize=(10, 4))  # Увеличиваем размер графика
        self.canvas = self.figure.canvas
        bottom_layout.addWidget(self.canvas)

        # Таблица для платежей
        self.payment_table = QTableWidget()
        self.payment_table.setColumnCount(2)
        self.payment_table.setHorizontalHeaderLabels(["Месяц", "Платеж (руб.)"])
        bottom_layout.addWidget(self.payment_table)

        bottom_layout.addItem(spacer_right)

        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def calculate_loan(self):
        try:
            self.result_label.setText("")
            payment_type = self.payment_type.currentText()
            loan_amount = self.loan_amount.text().replace(',', '.')
            loan_term = self.loan_term.text()
            interest_rate = self.interest_rate.text().replace(',', '.')

            # Проверка ввода
            if not re.match(r'^[1-9]\d*$', loan_term):
                raise ValueError("Срок кредита должен быть положительным целым числом.")
            if not re.match(r'^[0-9]+(\.[0-9]+)?$', loan_amount):
                raise ValueError("Сумма кредита должна быть положительным числом.")
            if not re.match(r'^[0-9]+(\.[0-9]+)?$', interest_rate):
                raise ValueError("Процентная ставка должна быть положительным числом.")

            loan_amount = float(loan_amount)
            loan_term = int(loan_term)
            interest_rate = float(interest_rate)

            # Проверки на корректность значений
            if loan_amount <= 0:
                raise ValueError("Сумма кредита должна быть положительным числом.")
            if loan_term <= 0:
                raise ValueError("Срок кредита должен быть положительным числом.")
            if interest_rate <= 0:
                raise ValueError("Процентная ставка должна быть положительным числом.")

            monthly_rate = interest_rate / 100 / 12

            if payment_type == "Аннуитетный":
                annuity_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** loan_term) / ((1 + monthly_rate) ** loan_term - 1)
                total_payment = annuity_payment * loan_term
                overpayment = total_payment - loan_amount
                result = f"Ежемесячный платёж: {annuity_payment:.2f} руб.\nОбщая переплата: {overpayment:.2f} руб."
                self.result_label.setText(result)

                annuity_payments = [annuity_payment] * loan_term
                self.plot_bar_chart(annuity_payments, "Сумма платежа (руб.)", "Месяц")

                self.payment_table.setRowCount(loan_term)
                for i in range(loan_term):
                    self.payment_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    self.payment_table.setItem(i, 1, QTableWidgetItem(f"{annuity_payment:.2f}"))
            else:
                monthly_payments = []
                principal = loan_amount / loan_term
                for month in range(loan_term):
                    monthly_interest = (loan_amount - principal * month) * monthly_rate
                    monthly_payment = principal + monthly_interest
                    monthly_payments.append(monthly_payment)
                total_payment = sum(monthly_payments)
                overpayment = total_payment - loan_amount
                result = f"Общая переплата: {overpayment:.2f} руб."
                self.result_label.setText(result)

                self.plot_bar_chart(monthly_payments, "Сумма платежа (руб.)", "Месяц")

                self.payment_table.setRowCount(len(monthly_payments))
                for i, payment in enumerate(monthly_payments):
                    self.payment_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    self.payment_table.setItem(i, 1, QTableWidgetItem(f"{payment:.2f}"))
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def plot_bar_chart(self, values, ylabel, xlabel):
        self.ax.clear()
        self.ax.bar(range(1, len(values) + 1), values)
        self.ax.set_title("График платежей по месяцам")
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        # Увеличиваем отступы
        self.ax.margins(x=0.1, y=0.1)

        # Автоматическое масштабирование осей
        self.ax.relim()
        self.ax.autoscale_view()

        # Устанавливаем формат меток на оси Y
        self.ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))

        self.canvas.draw()


class DepositCalculatorTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Группа для формы ввода
        form_group = QGroupBox("Параметры депозита")
        form_layout = QFormLayout()

        self.deposit_amount = QLineEdit()
        self.deposit_amount.setPlaceholderText("Введите сумму депозита")
        self.deposit_amount.setToolTip("Сумма депозита в рублях")
        form_layout.addRow("Сумма в рублях:", self.deposit_amount)

        self.deposit_term = QLineEdit()
        self.deposit_term.setPlaceholderText("Введите срок депозита")
        self.deposit_term.setToolTip("Срок депозита в месяцах")
        form_layout.addRow("Срок в месяцах:", self.deposit_term)

        self.deposit_rate = QLineEdit()
        self.deposit_rate.setPlaceholderText("Введите процентную ставку")
        self.deposit_rate.setToolTip("Годовая процентная ставка")
        form_layout.addRow("Процентная ставка:", self.deposit_rate)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Кнопка "Рассчитать"
        self.calculate_button = QPushButton("Рассчитать")
        self.calculate_button.clicked.connect(self.calculate_deposit)
        layout.addWidget(self.calculate_button)

        # Результаты
        self.result_label = QLabel("Результаты:")
        self.result_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.result_label)

        # График и таблица рядом в центре
        bottom_layout = QHBoxLayout()

        # Добавляем отступы для центрирования
        spacer_left = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        spacer_right = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        bottom_layout.addItem(spacer_left)

        # График
        self.figure, self.ax = plt.subplots(figsize=(10, 4))  # Увеличиваем размер графика
        self.canvas = self.figure.canvas
        bottom_layout.addWidget(self.canvas)

        # Таблица для баланса
        self.balance_table = QTableWidget()
        self.balance_table.setColumnCount(2)
        self.balance_table.setHorizontalHeaderLabels(["Месяц", "Баланс (руб.)"])
        bottom_layout.addWidget(self.balance_table)

        bottom_layout.addItem(spacer_right)

        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def calculate_deposit(self):
        try:
            deposit_amount = self.deposit_amount.text().replace(',', '.')
            deposit_term = self.deposit_term.text()
            deposit_rate = self.deposit_rate.text().replace(',', '.')

            if not re.match(r'^[0-9]+(\.[0-9]+)?$', deposit_amount):
                raise ValueError("Сумма вклада должна быть положительным числом.")
            if not re.match(r'^[1-9]\d*$', deposit_term):
                raise ValueError("Срок вклада должен быть положительным целым числом.")
            if not re.match(r'^[0-9]+(\.[0-9]+)?$', deposit_rate):
                raise ValueError("Процентная ставка должна быть положительным числом.")

            deposit_amount = float(deposit_amount)
            deposit_term = int(deposit_term)
            deposit_rate = float(deposit_rate)

            if deposit_amount <= 0:
                raise ValueError("Сумма вклада должна быть положительным числом.")
            if deposit_term <= 0:
                raise ValueError("Срок вклада должен быть положительным числом.")
            if deposit_rate <= 0:
                raise ValueError("Процентная ставка должна быть положительным числом.")

            monthly_rate = deposit_rate / 100 / 12

            balances = [deposit_amount]
            for _ in range(1, deposit_term + 1):
                new_balance = balances[-1] * (1 + monthly_rate)
                balances.append(new_balance)

            total_interest = balances[-1] - deposit_amount
            self.result_label.setText(f"Итоговая сумма процентов: {total_interest:.2f} руб.\nОбщая сумма к выдаче: {balances[-1]:.2f} руб.")

            self.plot_deposit_bar_chart(balances[1:])

            self.balance_table.setRowCount(len(balances) - 1)
            for i, balance in enumerate(balances[1:], start=1):
                self.balance_table.setItem(i - 1, 0, QTableWidgetItem(str(i)))
                self.balance_table.setItem(i - 1, 1, QTableWidgetItem(f"{balance:.2f}"))
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def plot_deposit_bar_chart(self, balances):
        self.ax.clear()
        self.ax.bar(range(1, len(balances) + 1), balances)
        self.ax.set_title("График состояния счета по месяцам")
        self.ax.set_xlabel("Месяц")
        self.ax.set_ylabel("Баланс (руб.)")

        # Увеличиваем отступы
        self.ax.margins(x=0.1, y=0.1)

        # Автоматическое масштабирование осей
        self.ax.relim()
        self.ax.autoscale_view()

        # Устанавливаем формат меток на оси Y
        self.ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))

        self.canvas.draw()


app = QApplication(sys.argv)
window = CalculatorApp()
window.show()
sys.exit(app.exec())