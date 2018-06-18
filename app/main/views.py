from flask import render_template,redirect,url_for,flash, \
    current_app,request,make_response
from flask_login import login_required,current_user
from . import main
from .. import db
from ..models import Role,User,Order,Goods,Report,Town
from ..decorators import role_required
from .forms import SaleForm,QueryForm,QueryReportForm
from datetime import datetime,date
from sqlalchemy import extract,and_
from app.draw import Draw
from io import BytesIO
import os
import base64
from threading import Thread
from sqlalchemy import func


@main.before_app_request
def supply_report_commission():
    today = date.today()
    #自动供货
    if today.day == 2:
        users = User.query.join(Goods,User.id==Goods.user_id) \
            .filter(Goods.supplyDate.year!=today.year) \
            .filter(Goods.supplyDate.month!=today.month).all()
        for u in users:
            g = u.goods.first()
            if g:
                g.supply()
    #自动生成销售报告和佣金结算

        users = User.query.all()
        for u in users:
            r = u.reports.order_by(Report.year.desc(),
                                  Report.month.desc()).first()
            if r and r.month == today.month-2:
                u.report(datetime.strptime('{}-{}-{}'.format(today.year,today.month-1,1),'%Y-%m-%d'))
        db.session.commit()

        report = Report.query.filter_by(commission=0.0).first()
        if report.year == today.year and report.month != today.month:
            reports = Report.query.filter_by(commission=0.0).all()
            for r in reports:
                User.commission(r.master)


@main.route('/',methods=['GET','POST'])
def index():
    '''
    salesperson返回‘’，day返回0，town返回‘’
    :return:
    '''
    page = request.args.get('page', 1, type=int)
    form = QueryForm()
    query = Order.query
    if form.validate_on_submit():
        if form.salesperson.data != '':
            query = query.filter_by(
                master=User.query.filter_by(name=form.salesperson.data).first())
        if form.year.data != 0:
            query = query.filter_by(year=form.year.data)
        if form.month.data != 0:
            query = query.filter_by(month=form.month.data)
        if form.day.data != 0:
            query = query.filter_by(day=form.day.data)
        if form.town.data != '无':
            query = query.filter_by(
                town=Town.query.filter_by(name=form.town.data).first())
    pagination = query.order_by(Order.month.desc(),Order.day.desc()) \
                    .paginate(page,per_page=10,error_out=False)
    orders = pagination.items
    return render_template('index.html',pagination=pagination,
                           orders=orders,form=form)


@main.route('/soldreport',methods=['GET','POST'])
def soldreport():
    page = request.args.get('page', 1, type=int)
    form = QueryReportForm()
    query = Report.query
    if form.validate_on_submit():
        if form.year.data != 0:
            query = query.filter_by(year=form.year.data)
        if form.month.data != 0:
            query = query.filter_by(month=form.month.data)
        if form.salesperson.data != '':
            query = query.filter_by(
                master=User.query.filter_by(name=form.salesperson.data).first())
    pagination = query.order_by(Report.month.desc()).paginate(
        page, per_page=10, error_out=False
    )
    reports = pagination.items
    return render_template('soldreport.html', pagination=pagination,
                           reports=reports, form=form)


@main.route('/draw')
def draw():
    today = date.today()
    month = today.month-1
    draw = Draw()
    monthNumber = draw.drawMonthNumber()
    sio = BytesIO()
    monthNumber.savefig(sio,format='png')
    mN = base64.encodebytes(sio.getvalue()).decode()

    monthProfit = draw.drawMonthProfit()
    sio = BytesIO()
    monthProfit.savefig(sio,format='png')
    mP = base64.encodebytes(sio.getvalue()).decode()

    town = draw.drawTown()
    sio = BytesIO()
    town.savefig(sio, format='png')
    t = base64.encodebytes(sio.getvalue()).decode()

    salesperson = draw.drawSalesperson()
    sio = BytesIO()
    salesperson.savefig(sio, format='png')
    s = base64.encodebytes(sio.getvalue()).decode()

    sumTotal = db.session.query(
                              func.sum(Report.locks).label('locks'),
                              func.sum(Report.stocks).label('stocks'),
                              func.sum(Report.barrels).label('barrels'),
                              func.sum(Report.total).label('total'),
                              func.sum(Report.commission).label('commission')) \
        .filter_by(year=today.year).all()
    total = []
    for i in range(len(sumTotal[0])):
        if i != 4:
            total.append(int(sumTotal[0][i]))
        else:
            total.append(float(sumTotal[0][i]))

    return render_template('draw.html',mN=mN,mP=mP,
                           t=t,s=s,month=month,total=total)


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
    today = date.today()
    user = User.query.filter_by(name=name).first()
    if not user:
        flash('User is not exist.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    r = bool(request.cookies.get('r',''))
    reports = None
    orders = None
    if r:
        query = Report.query.filter_by(user_id=user.id). \
            filter_by(year=today.year).order_by(Report.month.desc())
        pagination = query.paginate(
            page=page, per_page=10, error_out=False
        )
        reports = pagination.items
    else:
        query = Order.query.filter_by(user_id=user.id). \
            filter_by(year=today.year).filter_by(month=today.month). \
            order_by(Order.year.desc(), Order.month.desc(),Order.day.desc())
        pagination = query.paginate(
            page=page, per_page=10, error_out=False
        )
        orders = pagination.items
    return render_template('salesperson.html', pagination=pagination,
                           orders=orders,reports=reports,user=user,r=r)


@main.route('/orders')
def orders():
    name = request.args.get('name')
    res = make_response(redirect(url_for('.salesperson',name=name)))
    res.set_cookie('r','')
    return res


@main.route('/reports')
def reports():
    name = request.args.get('name')
    res = make_response(redirect(url_for('.salesperson',name=name)))
    res.set_cookie('r','1')
    return res


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
        if not my_goods:
            flash('You have not goods.')
            return redirect(url_for('.salesperson',name=name))
        locks = my_goods.locks
        stocks = my_goods.stocks
        barrels = my_goods.barrels
        flash('{}{}{}'.format(locks,stocks,barrels))
        if form.locks.data>locks or form.stocks.data>stocks \
            or form.barrels.data>barrels:
            flash('Invalid Numbers.')
            return redirect(url_for('.sale',name=name))
        try:
            order = Order(user_id=user.id,
                          locks=form.locks.data,
                          stocks=form.stocks.data,
                          barrels=form.barrels.data,
                          town=Town.query.filter_by(name=form.town.data).first()
                          )
            order.calculate_total()
            db.session.add(order)

            my_goods.locks -= form.locks.data
            my_goods.stocks -= form.stocks.data
            my_goods.barrels -= form.barrels.data
            db.session.add(my_goods)

            db.session.commit()
            flash('A sale has been completed.')
        except:
            db.session.rollback()
            flash('The sale is failed.')
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
    today = date.today()
    user.report(today)
    flash('A report has been completed.')
    return redirect(url_for('.index',monthreport=1,page=-1))
