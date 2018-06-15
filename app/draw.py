from app.models import Report,User,Town,Order
from datetime import date
from matplotlib import pyplot as plt
import numpy as np
from app import db
from sqlalchemy import func
from pylab import mpl


class Draw():
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['font.sans-serif'] = ['FangSong']

    today = date.today()
    def drawMonthNumber(self):
        plt.close()

        tongji = db.session.query(Report.month,
                                   func.sum(Report.locks).label('locks'),
                                   func.sum(Report.stocks).label('stocks'),
                                   func.sum(Report.barrels).label('barrels'),
                                   func.sum(Report.total).label('total'),
                                   func.sum(Report.commission).label('commission')) \
                            .filter_by(year=self.today.year).filter(Report.month!=self.today.month) \
                            .group_by(Report.month).all()

        month = [1,2,3,4,5,6,7,8,9,10,11,12]
        locks = [0]*12
        stocks = [0]*12
        barrels = [0]*12
        total = [0]*12
        commission = [0.0]*12
        for i in tongji:
            locks[int(i[0])-1] = int(i[1])
            stocks[int(i[0])-1] = int(i[2])
            barrels[int(i[0])-1] = int(i[3])
            total[int(i[0])-1] = int(i[4])
            commission[int(i[0])-1] = float(i[5])

        label = ['locks','stocks','barrels']
        x = np.arange(0,42,3.5)
        plt.bar(x,locks,width=1,color='r',label=label[0])
        plt.bar(x+1,stocks,width=1,color='b',label=label[1])
        plt.bar(x+2,barrels,width=1,color='g',label=label[2])

        plt.title(u'月销售数量柱状图')
        plt.xlabel('Month')
        plt.xticks(np.arange(0,42,3.5)+1,month)
        plt.ylabel('Number')
        '''
        for i in range(12):
            plt.text(i+4.5,locks[i]+0.05,locks[i],ha='center',va='bottom')
            plt.text(i+4.5, stocks[i] + 0.05, stocks[i], ha='center', va='bottom')
            plt.text(i+4.5, barrels[i] + 0.05, barrels[i], ha='center', va='bottom')
        '''
        plt.legend()
        return plt

    def drawSalesperson(self):
        plt.close()

        tongji = db.session.query(Report.user_id,
                                  func.sum(Report.commission).label('commission')) \
            .filter_by(year=self.today.year).filter(Report.month != self.today.month) \
            .group_by(Report.user_id).all()
        tongji = sorted(tongji,key=lambda x:x[1],reverse=True)
        ids = []
        names = []
        commissions = []

        for i in tongji:
            ids.append(i[0])
            commissions.append(float(i[1]))
        for id in ids:
            names.append(User.query.get(int(id)).name)
        x = np.arange(0,len(names),1)
        plt.bar(x,commissions,width=0.8,color='r')

        plt.title(u'佣金柱状图')
        plt.xlabel('name')
        plt.xticks(x,names)
        plt.ylabel('commission')
        return plt


    def drawTown(self):
        plt.close()

        tongji = db.session.query(Order.town_id,
                                      func.sum(Order.total).label('total')) \
                .filter_by(year=self.today.year).filter(Order.month != self.today.month) \
                .group_by(Order.town_id).all()
        tongji = sorted(tongji,key=lambda x:x[1],reverse=True)
        towns = []
        totals = []
        for i in tongji:
            towns.append(Town.query.get(i[0]).name)
            totals.append(int(i[1]))

        plt.title(u'省销售额饼状图')

        plt.axes(aspect=1)
        plt.pie(x=totals,labels=towns,
                explode=[x*0.02 for x in range(len(towns))],
                autopct='%3.1f %%',shadow=False,labeldistance=1.1,
                startangle=0,pctdistance=0.8,center=(-1,0))
        #plt.legend(loc=7, bbox_to_anchor=(1.5, .8), ncol=3, fancybox=True, shadow=True, fontsize=8)
        return plt


    def drawMonthProfit(self):
        plt.close()

        tongji = db.session.query(Report.month,
                                      func.sum(Report.total).label('total')) \
                .filter_by(year=self.today.year).filter(Report.month != self.today.month) \
                .group_by(Report.month).all()
        tongji = sorted(tongji,key=lambda x:x[1],reverse=True)
        months = []
        totals = []
        for i in tongji:
            months.append(str(i[0])+'月')
            totals.append(int(i[1]))

        plt.title(u'月销售额饼状图')

        plt.axes(aspect=1)
        plt.pie(x=totals,labels=months,
                explode=[x*0.02 for x in range(len(months))],
                autopct='%3.1f %%',shadow=False,labeldistance=1.1,
                startangle=0,pctdistance=0.8,center=(-1,0))
        #plt.legend(loc=7, bbox_to_anchor=(1.5, .8), ncol=3, fancybox=True, shadow=True, fontsize=8)
        return plt