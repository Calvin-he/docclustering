# encoding=utf8

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

font = mpl.font_manager.FontProperties(family='WenQuanYi Zen Hei',fname='/usr/share/matplotlib/mpl-data/fonts/wqy/wqy-zenhei.ttc')
#mpl.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei'] 
#mpl.rcParams['axes.unicode_minus'] = False
#mpl.rc('font', **{'family':'WenQuanYi Zen Hei'})
#rc('text',usetex=False)
#print mpl.get_configdir()

dtype = np.dtype([('ndocs','i4'),('time','f4')])
data = np.loadtxt('../result/time.log', dtype=dtype, skiprows=1)
x,y = data['ndocs'],data['time']
plt.plot(x,y,"ro")
plt.xlabel(u'#文本数', fontproperties=font)
plt.ylabel(u'运行时间(秒)', fontproperties=font)

x2 = np.arange(min(x)-1,max(x)+1,1)
c = np.polyfit(x,y,2)
y2= np.polyval(c,x2)
plt.plot(x2,y2, label=u'deg=2')
plt.legend(loc='upper left')
plt.show()










