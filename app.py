from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from datetime import timedelta
from tracker_module import SavingsTracker
from auth import AuthService
from database import db, UserModel, TransactionModel
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_tracker.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

tracker = SavingsTracker()

@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = str(request.form['password'])
        if AuthService.login_user(username, password):
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password==confirm_password:
            if AuthService.register_user(username, email, password):
                return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/expense', methods=['GET', 'POST'])
@login_required
def expense():
    if request.method == 'POST':
        try:
            name = request.form['expense_name']
            amount = request.form['expense_amount']
            category = request.form['expense_category']
            date = request.form['expense_date']
            tracker.add_expense(current_user.id, name, amount, category, date)
        except (ValueError, TypeError) as e:
            flash("Invalid input: " + str(e), "error")
            return redirect(url_for('expense'))
        else:
            flash("Expense added successfully", "success")
        return redirect(url_for('expense'))
    recent_expenses = TransactionModel.query.filter_by(user_id=current_user.id).filter(TransactionModel.description!="Income").order_by(TransactionModel.date.desc()).limit(5).all()
    return render_template('expense.html', recent_expenses=recent_expenses)

@app.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    if request.method == 'POST':
        try:
            amount = float(request.form.get('income_amount'))
            source = request.form['income_source']
            date = request.form['income_date']
            tracker.add_income(current_user.id, "Income", amount, source, date)
        except (ValueError, TypeError) as e:
            flash("Invalid input: " + str(e), "error")
            return redirect(url_for('income'))
        else:
            flash("Income added successfully")
        return redirect(url_for('income'))
    recent_incomes = TransactionModel.query.filter_by(user_id=current_user.id).filter(TransactionModel.description=="Income").order_by(TransactionModel.date.desc()).limit(5).all()
    return render_template('income.html', recent_incomes=recent_incomes)

@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    if request.method == 'POST':
        report_type = request.form['report_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        if report_type=='income-expense':
            income_total = db.session.query(func.sum(TransactionModel.amount)).filter_by(user_id=current_user.id, description="Income").filter(TransactionModel.date >= start_date, TransactionModel.date <= end_date).scalar() or 0
            expense_total = db.session.query(func.sum(TransactionModel.amount)).filter_by(user_id=current_user.id).filter(TransactionModel.description!="Income").filter(TransactionModel.date >= start_date, TransactionModel.date <= end_date).scalar() or 0
            net = income_total - expense_total
            income_expense_summary = {"income": income_total, "expense": expense_total, "net": net}
            return render_template('reports.html', income_expense_summary=income_expense_summary)
        elif report_type=='category-analysis':
            category_summary = db.session.query(TransactionModel.source, func.sum(TransactionModel.amount)).filter_by(user_id=current_user.id).filter(TransactionModel.description!="Income", TransactionModel.date >= start_date, TransactionModel.date <= end_date).group_by(TransactionModel.source).all()
            return render_template('reports.html', category_summary=category_summary)
    return render_template('reports.html')

if __name__ == '__main__':
    app.run(debug=True)
