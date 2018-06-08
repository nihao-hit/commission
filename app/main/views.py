from flask import render_template,redirect,url_for,flash, \
    current_app,request,make_response
from flask_login import login_required,current_user
from . import main
from .. import db
from ..models import Role,User,Order,Goods,Report
from ..decorators import role_required
from .forms import SaleForm
from math import isclose


@main.route('/')
def index():
    page = request.args.get('page',1,type=int)
    monthreport = bool(request.cookies.get('monthreport',''))
    if monthreport:
        query = Report.query.order_by(Report.date.desc())
    else:
        query = Order.query.order_by(Order.date.desc())
    if page == -1:
        page = query.count()//10+1
    pagination = query.paginate(
        page,per_page=10,error_out=False
    )
    orders = pagination.items
    return render_template('index.html',pagination=pagination,
                           orders=orders,monthreport=monthreport)


@main.route('/soldnote')
def soldnote():
    res = make_response(redirect(url_for('.index')))
    res.set_cookie('monthreport','')
    return res


@main.route('/monthreport')
def monthreport():
    res = make_response(redirect(url_for('.index')))
    res.set_cookie('monthreport','1')
    return res


@main.route('/admin/<name>')
@login_required
@role_required('Admin')
def admin(name):
    role_id = Role.query.filter_by(name='Admin').first().id
    page = request.args.get('page',1,type=int)
    pagination = User.query.filter(User.role_id!=role_id). \
        paginate(page=page,per_page=10,error_out=False)
    users = pagination.items
    return render_template('admin.html',pagination=pagination,
                           users=users)


@main.route('/admin/<name>/unconfirm/<u>')
@login_required
@role_required('Admin')
def unconfirm(name,u):
    user = User.query.filter_by(name=u).first()
    user.confirmed = False
    return redirect(url_for('.admin',name=name))


@main.route('/admin/<name>/confirm/<u>')
@login_required
@role_required('Admin')
def confirm(name,u):
    user = User.query.filter_by(name=u).first()
    user.confirmed = True
    return redirect(url_for('.admin',name=name))


@main.route('/gunsmith/<name>')
@login_required
def gunsmith(name):
    role_id = Role.query.filter_by(name='Salesperson').first().id
    page = request.args.get('page',1,type=int)
    pagination = User.query.filter(User.role_id==role_id). \
        paginate(page=page,per_page=10,error_out=False)
    salespersons = pagination.items
    return render_template('gunsmith.html',pagination=pagination,
                           salespersons=salespersons,user=current_user)


@main.route('/gunsmith/<name>/supply/<s>')
@login_required
@role_required('Gunsmith')
def supply(name,s):
    g = User.query.filter_by(name=name).first()
    if not g:
        flash('User is not exist.')
        return redirect(url_for('.index'))
    salesperson = User.query.filter_by(name=s).first()
    if not s:
        flash('Salesperson is not exist.')
    salesperson.goods.first().supply()
    flash('A supply has been completed.')
    return redirect(url_for('.gunsmith', name=name))


@main.route('/gunsmith/<name>/commission/<s>')
@login_required
@role_required('Gunsmith')
def commission(name,s):
    g = User.query.filter_by(name=name).first()
    if not g:
        flash('User is not exist.')
        return redirect(url_for('.index'))
    salesperson = User.query.filter_by(name=s).first()
    if not s:
        flash('Salesperson is not exist.')
        return redirect(url_for('.gunsmith', name=name))
    g.commission(salesperson)
    flash('A commission has been completed.')
    return redirect(url_for('.gunsmith',name=name))


@main.route('/salesperson/<name>')
@login_required
def salesperson(name):
    user = User.query.filter_by(name=name).first()
    if not user:
        flash('User is not exist.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Order.query.filter_by(user_id=user.id). \
        order_by(Order.date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    orders = pagination.items
    return render_template('salesperson.html', pagination=pagination,
                           orders=orders,user=user)


@main.route('/salesperson/<name>/sale',methods=['GET','POST'])
@login_required
@role_required('Salesperson')
def sale(name):
    user = User.query.filter_by(name=name).first()
    if not user:
        flash('User is not exist.')
        return redirect(url_for('.index'))
    if user.name != current_user.name:
        flash('You are not the Salesperson.')
        return redirect(url_for('.salesperson',name=name))
    form = SaleForm()
    if form.validate_on_submit():
        my_goods = user.goods.first()
        locks = my_goods.locks
        stocks = my_goods.stocks
        barrels = my_goods.barrels
        if form.locks.data>locks or form.stocks.data>stocks \
            or form.barrels.data>barrels:
            flash('Invalid Numbers.')
            return redirect(url_for('.sale',name=name))
        order = Order(user_id=user.id,
                      locks=form.locks.data,
                      stocks=form.stocks.data,
                      barrels=form.barrels.data
                      )
        order.calculate_total()
        db.session.add(order)
        db.session.commit()
        flash('A sale has been completed.')
        return redirect(url_for('.salesperson',name=name))
    return render_template('sale.html',form=form)


@main.route('/salesperson/<name>/report')
@login_required
@role_required('Salesperson')
def report(name):
    user = User.query.filter_by(name=name).first()
    if not user:
        flash('User is not exist.')
        return redirect(url_for('.index'))
    if user.name != current_user.name:
        flash('You are not the Salesperson.')
        return redirect(url_for('.salesperson',name=name))
    user.report()
    flash('A report has been completed.')
    return redirect(url_for('.index',monthreport=1,page=-1))
