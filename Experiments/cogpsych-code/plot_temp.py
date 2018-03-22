#Temporary file to generate ps plots

#Close figures
plt.close()
paramsT = dict(params)
models = [Packer,CopyTweak]
#paramsP = dict(determinism = 2,specificity=.5,tradeoff=.5,wts=[.5,.5])
#paramsCT = dict(paramsP)
#paramsCT.pop('tradeoff')
paramsP = best_params[Packer.model]
paramsP['wts'] = paramsT['wts']
paramsCT = best_params[CopyTweak.model]
paramsCT['wts'] = paramsT['wts']
paramSet = [paramsP,paramsCT]
STAT_LIMS =  (-1.0, 1.0)

trials = 4
plt.ioff()
plt.ion()
f,ax = plt.subplots(trials,2,figsize = (6.7, 7.5))
for trial in range(trials):
    plotct = 0
    categories = [pptTrialObj.stimuli[i,:] for i in pptTrialObj.Set[trial]['categories'] if any(i)]
    A = categories[0]
    resp = pptTrialObj.stimuli[pptTrialObj.Set[trial]['response'],:]
    if len(categories)>1:
        #include the response
        B = np.append(categories[1],resp,axis=0)
    else:
        B = resp

    ps = []
    for i,model in enumerate(models):
        params = paramSet[i]
        #reverse-transform
        #params = model.parmxform(params, direction = -1)
        ps += [model(categories,params).get_generation_ps(pptTrialObj.stimuli,1,'generate')]
        
    plotVals = []
    psMax = 0
    psMin = 1
    #Get range
    for ps_el in ps:
        psMax = max(psMax,ps_el.max())
        psMin = min(psMin,ps_el.min())

    #Normalise all values
    psRange = psMax-psMin
    for i,ps_el in enumerate(ps):
        plotct += 1
        gps = funcs.gradientroll(ps_el,'roll')[:,:,0]
        plotVals += [(gps-psMin)/psRange]
        #ax = f.add_subplot(trials,2,plotct)
        #print B
        im = funcs.plotgradient(ax[trial,i], plotVals[i], A, B, clim = STAT_LIMS, cmap = 'PuOr')
        ax[trial,i].set_ylabel('Trial {}'.format(trial))
        # cbar = f.add_axes([0.21, .1, 0.55, 0.12])
        # f.colorbar(im, cax=cbar, ticks=[0, 1], orientation='horizontal')

    #Print probabilities up to trial num
    nll = np.zeros(2)
    for m,model in enumerate(models):
        params = paramSet[m]
        #params = model.parmxform(params, direction = -1)                        
        for t in range(trial+1):    
            categoriesT = [pptTrialObj.stimuli[i,:] for i in pptTrialObj.Set[t]['categories'] if any(i)]    
            psT = model(categoriesT,params).get_generation_ps(pptTrialObj.stimuli,1,'generate')
            psT_raw = psT[pptTrialObj.Set[t]['response']]
            nll[m] += -np.log(psT_raw)
    print nll

#plt.tight_layout(w_pad=-4.0, h_pad= 0.5)
plt.draw()
plt.ioff()
