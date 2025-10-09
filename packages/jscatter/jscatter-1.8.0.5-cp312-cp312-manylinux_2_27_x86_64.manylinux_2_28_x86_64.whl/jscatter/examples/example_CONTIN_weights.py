# Example showing different distribution and weights
# Particular the distribution='vradius' gives unstable results


import jscatter as js
import numpy as np
t=js.loglist(1,10000,1000)   #times in microseconds
q=4*np.pi*1.333/632*np.sin(np.deg2rad(90)/2) # 90 degrees for 632 nm , unit is 1/nm**2
D=0.05*1000  # nm**2/ns * 1000 = units nm**2/microseconds
noise=0.0001  # typical < 1e-3
data=js.dA(np.c_[t,0.95*np.exp(-q**2*D*t)+noise*np.random.randn(len(t))].T)

# add attributes to overwrite defaults
data.Angle      =90    # scattering angle in degrees
data.Temperature=293   # Temperature of measurement  in K
data.Viscosity  =1     # viscosity cPoise
data.Refractive =1.333 # refractive index
data.Wavelength =632   # wavelength

# do CONTIN in different weights
drx=js.dls.contin(data,distribution='x')  # intensity weight relaxation time distribution
dri=js.dls.contin(data,distribution='i')  # intensity weight radius distribution
drv=js.dls.contin(data,distribution='v')  # volume/mass weight radius distribution

# same to demonstrate access to distributions
bfx = drx[0].contin_bestFit
bfi = dri[0].contin_bestFit
bfv = drv[0].contin_bestFit

p=js.grace()
p.multi(2,1,vgap=0.25)

# access correlation function and relaxation time distribution
p[0].plot(drx[0],sy=[1,0.4,1],legend='contin data')
p[0].plot(drx[0].contin_result_fit,sy=[1,0.15,5],legend='x contin_result_fit')
p[0].plot(drv[0].contin_result_fit,sy=[1,0.05,4],legend='v contin_result_fit')

# relaxation times
p[0].plot(bfx._relaxationtimes,bfx._massweightci*10,sy=[2,0.5,2],le='x relaxation time distribution')
p[0].plot(bfi._relaxationtimes,bfi._massweightci*10,sy=[3,0.2,5],le='iradius ')
p[0].plot(bfv._relaxationtimes,bfv._massweightci*10,sy=[3,0.2,4],le='vradius ')


p[0].xaxis(scale='log',label=r'\xG\f{} / µs',min=1e-6,max=0.1)
p[0].yaxis(label=r'G\s1\N / P(\xG\f{})',min=0,max=1.1)
p[0].legend(x=300,y=0.7)
p[0].title('Comparison different weights')
p[0].subtitle('volume weight can lead to artificial peaks')

# Hydrodynamic radius distribution in different weights
# p[1].plot(bfx._hydrodynamicradii,bfx._intensityweightci,sy=[2,0.5,2],li=[1,1,''],le='x intensity weight')
p[1].plot(bfx._hydrodynamicradii,bfx._massweightci,sy=[2,0.5,3],li=[1,1,''],le='x mass weight')
p[1].plot(bfx._hydrodynamicradii,bfx._numberweightci,sy=[2,0.5,4],li=[1,1,''],le='x number weight')

# p[1].plot(bfi._hydrodynamicradii,bfi._intensityweightci,sy=[3,0.25,5],li=[1,1,''],le='i intensity weight')
p[1].plot(bfi._hydrodynamicradii,bfi._massweightci,sy=[3,0.25,6],li=[1,1,''],le='i mass weight')
p[1].plot(bfi._hydrodynamicradii,bfi._numberweightci,sy=[3,0.25,7],li=[1,1,''],le='i number weight')

p[1].plot(bfi._radius,bfv._volumeweightci,sy=[4,0.25,5],li=[1,1,''],le='i intensity weight')
p[1].plot(bfi._hydrodynamicradii,bfv._volumeweightci,sy=[4,0.25,5],li=[1,1,''],le='i volume weight')

p[1].plot(bfv._radius,bfv._massweightci,sy=[2,0.25,6],li=[1,1,''],le='v mass weight')
if 0:
    # number weight can overweight small radii
    # leading to artificial peak
    p[1].plot(bfv._hydrodynamicradii,bfv._numberweightci,sy=[2,0.25,7],li=[1,1,''],le='v number weight')
p[0].text(fr'artificial peaks',x=2e-6,y=0.2,charsize=0.7,rot=90)


p[1].xaxis(scale='log',label=r'R\sh\N / cm',min=5e-9,max=1e-5)
p[1].yaxis(label=r'P(R\sh\N)',min=0,max=0.1)
p[1].legend(x=1.5e-6,y=0.1,charsize=0.5)
p[1].text(fr'Rh from contin [cm] \nx-> {bfx.ipeaks[0,6]:.3g} \ni-> {bfi.ipeaks[0,1]:.3g} \nv-> {bfv.ipeaks[0,1]:.3g}',x=1.3e-6,y=0.02,charsize=0.7)
# p.save(js.examples.imagepath+'/contin_weights.jpg')



