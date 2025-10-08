# for data/pha.rst

import os

import numpy as np
import matplotlib.pyplot as plt

from sherpa.utils.testing import get_datadir

from sherpa.astro.data import DataPHA
from sherpa.astro.io import read_pha
from sherpa.astro.plot import DataPHAPlot

def report(name):
    print("# print({})".format(name))
    print(eval(name))
    print("----------------------------------------")


def dump(name):
    print("# dump")
    print("{}".format(name))
    print(repr(eval(name)))
    print("----------------------------------------")


def savefig(name):
    plt.savefig(name)
    print("# Created: {}".format(name))


basedir = get_datadir()
if basedir is None:
    raise IOError("No test data directory")

# Temporarily jump to the directory to get the paths right
cwd = os.getcwd()

os.chdir(basedir)
print(f'--> jumping to {basedir}')
pha = read_pha('3c273.pi')
os.chdir(cwd)

report('pha')
report('pha.get_background()')
report('pha.get_arf()')
report('pha.get_rmf()')


chans = np.arange(1, 1025, dtype=int)
counts = np.ones(1024, dtype=int)
test = DataPHA('example', chans, counts)
report('test')

plot = DataPHAPlot()
plot.histo_prefs['linestyle'] = '-'
plot.prepare(pha)
plot.plot()
savefig('pha_initial.png')

# units

dump('pha.get_analysis()')
report('pha.units')

# filtering

report("pha.mask")
report("pha.grouped")

y1 = pha.get_dep()
y2 = pha.get_dep(filter=True)
report('y1.size')
report('y2.size')

pha.notice(0.5, 7)
report('pha.get_dep(filter=True).size')
plot.prepare(pha)
plot.plot()
savefig('pha_filtered.png')

report('pha.get_filter()')

pha.units = 'channel'
report('pha.get_filter()')
plot.prepare(pha)
plot.plot(xlog=True, ylog=True)
pha.units = 'energy'
savefig('pha_filtered_channel.png')

# Grouping

os.chdir(basedir)
print(f'--> jumping to {basedir}')
from sherpa.utils.logging import SherpaVerbosity
with SherpaVerbosity('ERROR'):
    pha1 = read_pha('3c273.pi')
    pha2 = read_pha('3c273.pi')
    pha3 = read_pha('3c273.pi')

os.chdir(cwd)

pha1.notice(0.5, 7)
pha2.notice(0.5, 7)
pha3.notice(0.5, 7)

pha1.ungroup()
pha3.group_counts(40)

plt.subplot(2, 1, 1)
plot.prepare(pha1)
plot.plot(clearwindow=False)

plt.subplot(2, 1, 2)
plot.prepare(pha2)
plot.plot(xlog=True, alpha=0.7, clearwindow=False)
plot.prepare(pha3)
plot.overplot(alpha=0.7)
plt.title('')
plt.subplots_adjust(hspace=0.4)

savefig('pha_grouping_comparison.png')
plt.clf()

report('pha1.get_filter()')
report('pha2.get_filter()')
report('pha3.get_filter()')

# Manipulating data

d1 = pha.get_dep(filter=True)
d2 = pha.apply_filter(pha.counts)
report('np.all(d1 == d2)')

clo = pha.apply_filter(pha.channel, groupfunc=pha._min)
chi = pha.apply_filter(pha.channel, groupfunc=pha._max)
report('clo[0:7]')
report('chi[0:7]')

alo = pha.apply_grouping(pha.channel, pha._min)
ahi = pha.apply_grouping(pha.channel, pha._max)
report('alo[0:7]')
report('ahi[0:7]')

# Background

report('pha.background_ids')
bkg = pha.get_background()
report('bkg')


report('pha.get_dep(filter=True)')
pha.subtract()
report('pha.get_dep(filter=True)')
