from django.db import models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


from django.utils import translation
from django.utils.translation import gettext as _

translation.activate("tr")

class MarketOrderModelManager(models.Manager):
    def getStatistics(self):
        orders = self.all()

        todaysSales = self.getTodaysSales(orders)
        todaysSalesAmount = self.getSalesAmount(todaysSales)
        
        yesterdaySales = self.getYesterdaySales(orders)

        thisWeeksSales, lastWeeksSales = self.getWeeksSales(orders)

        thisMonthsSales, lastMonthsSales = self.getMonthsSales(orders)

        return {
            "dailySalesCount": len(todaysSales),
            "dailySalesDifference": self.getDifference(len(todaysSales), len(yesterdaySales)) if len(yesterdaySales)>0 else 0,
            "dailySalesAmount": todaysSalesAmount,
            "dailySalesDifferenceAmount": self.getDifference(todaysSalesAmount, self.getSalesAmount(yesterdaySales)) if len(yesterdaySales)>0 else 0,

            "weeklySalesCount": len(thisWeeksSales),
            "weeklySalesDifference": self.getDifference(len(thisWeeksSales), len(lastWeeksSales)) if len(lastWeeksSales)>0 else 0,
            "weeklySalesAmount": self.getSalesAmount(thisWeeksSales),
            "weeklySalesDifferenceAmount": self.getDifference(self.getSalesAmount(thisWeeksSales), self.getSalesAmount(lastWeeksSales)) if len(lastWeeksSales)>0 else 0,
            "weeklySalesGraph": self.getWeeksSalesGraph(thisWeeksSales),

            "monthlySalesCount": len(thisMonthsSales),
            "monthlySalesDifference": self.getDifference(len(thisMonthsSales), len(lastMonthsSales)) if len(lastMonthsSales)>0 else 0,
            "monthlySalesAmount": self.getSalesAmount(thisMonthsSales),
            "monthlySalesDifferenceAmount": self.getDifference(self.getSalesAmount(thisMonthsSales), self.getSalesAmount(lastMonthsSales)) if len(lastMonthsSales)>0 else 0,
            "monthlySalesGraph": self.getMonthsSalesGraph(thisMonthsSales),
        }

    def getTodaysSales(self, orders):
        return orders.filter(orderDate__gte=datetime.now().replace(hour=0,minute=0,second=0, microsecond=0))

    def getYesterdaySales(self, orders):
        today = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        return orders.filter(orderDate__gte=today-timedelta(days=1), orderDate__lt=today)

    def getWeeksSales(self, orders):
        endThisWeek = datetime.now().replace(hour=0,minute=0,second=0, microsecond=0)
        startThisWeek = endThisWeek - timedelta(weeks=1)

        return orders.filter(orderDate__gte=startThisWeek, orderDate__lt=endThisWeek), orders.filter(orderDate__gte=startThisWeek-timedelta(weeks=1), orderDate__lt=startThisWeek)

    def getWeeksSalesGraph(self, orders):
        today = datetime.now().replace(hour=0,minute=0,second=0, microsecond=0)
        firstDate = today - timedelta(weeks=1)

        data = [[],[],[]]

        while firstDate < today:
            secondDate = firstDate + timedelta(days=1)
            dayOrders = orders.filter(orderDate__gte=firstDate, orderDate__lt=secondDate)
            data[0].append(_(firstDate.strftime("%a")))
            data[1].append(len(dayOrders))
            data[2].append(round(self.getSalesAmount(dayOrders),2))

            firstDate = secondDate
            
        return data

    def getMonthsSales(self, orders):
        endThisMonth = datetime.now().replace(hour=0,minute=0,second=0, microsecond=0)
        startThisMonth = endThisMonth - timedelta(days=30)

        return orders.filter(orderDate__gte=startThisMonth, orderDate__lt=endThisMonth), orders.filter(orderDate__gte=startThisMonth-timedelta(weeks=1), orderDate__lt=startThisMonth)

    def getMonthsSalesGraph(self, orders):
        today = datetime.now().replace(hour=0,minute=0,second=0, microsecond=0)
        firstDate = today - timedelta(days=30)

        data = [[],[],[]]

        while firstDate < today:
            secondDate = firstDate + timedelta(days=1)
            dayOrders = orders.filter(orderDate__gte=firstDate, orderDate__lt=secondDate)
            data[0].append("{}/{}".format(firstDate.day, firstDate.month))
            data[1].append(len(dayOrders))
            data[2].append(round(self.getSalesAmount(dayOrders),2))

            firstDate = secondDate
            
        return data

    def getSalesAmount(self, orders):
        total = 0
        for order in orders:
            total +=order.totalPrice
        return total

    def getDifference(self, firstOrders, secondOrders):
        return (firstOrders - secondOrders) / secondOrders * 100
     