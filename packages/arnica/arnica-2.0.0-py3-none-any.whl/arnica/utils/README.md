# Utils 

## temporal\_analysis\_tools
This tools contains several functions. These functions aim at:

- handling and analyzing a temporal signal,
- transforming and analyzing it in frequencial domain,
- perform a [ks-test](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test),
- plot density distributions,
- calculate and plot the confidence interval of the mean of the signal,
- estimate the duration and the sampling rate of a simulation given the desired amplitude for the confidence interval.

For further information, please refer to [Arnica's documentation](http://open-source.pg.cerfacs.fr/arnica) 

### Script example


#### Loading data
In the following example, we assume two source files of temperatures.

The file `temperature_probe1.txt` is an ASCII file

```
blibla blo
```

One can read it using the basic Numpy `numpy.genfromtxt()` function:

```
probe_record = np.genfromtxt('temperature_probe1.txt')
```

Then clean the signal to get a regular sampling in time, with Arnica's `resample_signal()` :

```
clean_time, clean_signal = tat.resample_signal(time_vector, signal_vector)
```

#### Estimation of sampling and duration needed for convergence

Sampling can be estimated with the autocorrelation_time function Arnica's `tat.autocorrelation_time`:

```
smallest_dt = tat.autocorrelation_time(clean_time, clean_signal)
```

Duration can be estimated afterward with `tat.duration_for_uncertainty()`:

```
duration = tat.duration_for_uncertainty(clean_time, clean_signal, interval_amplitude)
```

#### Testing the Normal distribution

We test the distribution with the KS_test function `ks_test_distrib()`
```
score, position, height, scale = ks_test_distrib(plane_record)
```

### Full script

A possible final full script:

```python
from arnica import utils.temporal_analysis_tools as tat
import numpy as np

plane_record = np.genfromtxt('temperature_plane1.txt')

score, position, height, scale = ks_test_distrib(plane_record)
print('The worst agreement of data with a normal distribution is at height %s with a p-value of %s.' %(height, score))

##Data definition##
probe_record = np.genfromtxt('temperature_probe1.txt')
time_vector = probe_record[0]
signal = probe_record[1]
interval_amplitude = 0.5

clean_time, clean_signal = tat.resample_signal(time_vector, signal_vector)
smallest_dt = tat.autocorrelation_time(clean_time, clean_signal)
duration = tat.duration_for_uncertainty(clean_time, clean_signal, interval_amplitude)
print('My simulation should last %s seconds with a snapshot every %s seconds' %(duration,smallest_dt))

```