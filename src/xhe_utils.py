import sys

def updateProgress(ncur, ntotal):
    perc = '{0:.0%}'.format(float(ncur)/ntotal)
    sys.stdout.write('\rfinished=%d/total=%d, %s finished' %(ncur, ntotal, perc))
    sys.stdout.flush()
