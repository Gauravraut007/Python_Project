from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initial Data
initial_budget = 0
budget = initial_budget
expenses = {}  # Empty dictionary for dynamic expenses
savings_goal = 0

# Function to save data to an Excel file
def save_to_excel():
    import pandas as pd
    if expenses:
        df = pd.DataFrame(list(expenses.items()), columns=['Expense Name', 'Amount'])
    else:
        df = pd.DataFrame(columns=['Expense Name', 'Amount'])

    summary = pd.DataFrame({
        'Budget': [budget],
        'Total Expenses': [sum(expenses.values())],
        'Remaining Budget': [budget - sum(expenses.values())],
        'Saving Goal': [savings_goal]
    })
    with pd.ExcelWriter('Budget_Data.xlsx') as writer:
        df.to_excel(writer, sheet_name='Expenses', index=False)
        summary.to_excel(writer, sheet_name='Summary', index=False)

# Route for the home page
@app.route('/')
def index():
    total_expenses = sum(expenses.values())
    remaining_budget = budget - total_expenses
    return render_template('index.html', budget=budget, expenses=expenses, total_expenses=total_expenses,
                           remaining_budget=remaining_budget, savings_goal=savings_goal)

# Route to set the budget
@app.route('/set_budget', methods=['POST'])
def set_budget():
    global budget
    budget_input = request.form.get('budget', type=float)

    if budget_input is not None:
        if budget_input >= 0:
            budget = budget_input
            flash(f'Budget set to: ₹{budget}', 'success')
            save_to_excel()
        else:
            flash('Please enter a positive value for the budget.', 'error')
    else:
        flash('Budget value is required.', 'error')

    return redirect(url_for('index'))

# Route to add an expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    global expenses
    expense_name = request.form.get('expense_name')
    expense_amount = request.form.get('expense_amount', type=float)

    if expense_name and expense_amount is not None:
        if expense_amount > 0:
            expenses[expense_name] = expenses.get(expense_name, 0) + expense_amount
            total_expenses = sum(expenses.values())
            remaining_budget = budget - total_expenses

            if remaining_budget < 0:
                flash('Warning: Your expenses have crossed the budget!', 'warning')

            flash(f'Added expense: {expense_name} - ₹{expense_amount}', 'success')
            save_to_excel()
        else:
            flash('Please enter a positive value for the expense amount.', 'error')
    else:
        flash('Please enter both expense name and amount.', 'error')

    return redirect(url_for('index'))

# Route to remove an expense
@app.route('/remove_expense', methods=['POST'])
def remove_expense():
    global expenses
    expense_name = request.form.get('expense_name')

    if expense_name in expenses:
        del expenses[expense_name]
        flash(f'Removed expense: {expense_name}', 'success')
        save_to_excel()
    else:
        flash('Expense not found.', 'error')

    return redirect(url_for('index'))

# Route to set the savings goal
@app.route('/set_savings_goal', methods=['POST'])
def set_savings_goal():
    global savings_goal
    goal_input = request.form.get('savings_goal', type=float)

    if goal_input is not None:
        if goal_input > 0:
            savings_goal = goal_input
            flash(f'Savings goal set to: ₹{savings_goal}', 'success')
            save_to_excel()
        else:
            flash('Please enter a positive value for the savings goal.', 'error')
    else:
        flash('Savings goal value is required.', 'error')

    return redirect(url_for('index'))

# Route to reset the budget and expenses
@app.route('/reset', methods=['POST'])
def reset():
    global budget, expenses, savings_goal
    confirm_reset = request.form.get('confirm_reset')

    if confirm_reset == 'yes':
        budget = initial_budget
        expenses = {}
        savings_goal = 0
        flash('All transactions, budget, and savings goal have been reset.', 'success')
        save_to_excel()
    else:
        flash('Reset operation was canceled.', 'info')

    return redirect(url_for('index'))

# Route to generate pie chart of expenses
@app.route('/expense_pie_chart')
def expense_pie_chart():


    labels = expenses.keys()
    sizes = expenses.values()

    if not expenses:
        flash('No expenses to display in the pie chart.', 'info')
        return redirect(url_for('index'))

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    plt.close(fig)

    return send_file(io.BytesIO(output.getvalue()), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)


