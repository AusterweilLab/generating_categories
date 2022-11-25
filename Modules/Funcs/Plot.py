import numpy as np

def save_as_pgf(fh, path, 
    texpath = '/Library/TeX/texbin/',
    custom_opts = None,
    pad_inches = 0.01):
    """ 
    Wrapper to save a pgf file. 
    """
    
    opts = {
        'pgf.texsystem': 'pdflatex', 
        'pgf.rcfonts': True,
        }
    if custom_opts is not None:
        opts.update(textsettings)

    import os, matplotlib
    os.environ["PATH"] += os.pathsep + texpath
    matplotlib.rcParams.update(opts)
    fh.savefig(path, bbox_inches='tight', pad_inches=pad_inches)


def plotclasses(h, stimuli, alphas, betas,
    textsettings = None, 
                spinewidth = 0.5, betastr = 'B', betacol = [0,0,.5]):

    final_textsettings = dict(
        verticalalignment='center', 
        horizontalalignment='center',
        fontsize = 12.0,
        fontname = 'sans-serif')

    if textsettings is not None:
        final_textsettings.update(textsettings)

    h.axis(np.array([-1, 1, -1, 1])*1.2)
    for i in alphas:
        x, y = stimuli[i,0], stimuli[i,1]
        h.text(x, y, 'A', color = [0.5,0,0], **final_textsettings)

    for idx,i in enumerate(betas):
        x, y = stimuli[i,0], stimuli[i,1]
        if len(betas) == len(betastr):
            #Specific style for each beta - useful for multiple categories
            h.text(x, y, betastr[idx], color = betacol[idx], **final_textsettings)
        else:
            #Else just default
            h.text(x, y, betastr, color = betacol, **final_textsettings)

    h.set_yticks([])
    h.set_xticks([])
    h.set_aspect('equal', adjustable='box')
    [i.set_linewidth(spinewidth) for i in iter(h.spines.values())]


def plotgradient(h, G, alphas, betas, 
                                clim = (), 
                                cmap = 'Blues',
                                alpha_col = 'red',
                                beta_col = 'black',
                 gammas=[]):
    """
    Plot a gradient using matplotlib.
     - h is the handle to the axis
     - G is the matrix being plotted, 
     - alphas/betas are the [-1 +1] coordinates of category memebers
     - clim (optional) defines the limits of the colormap.
     - cmap (optional) deinfes the colormap
     - [alpha/beta]_col: color of alpha and beta markers     
     - gammas are [-1 +1] coordinates of gamma cat members
    """

    # generate clims if not provided
    if not clim:
        clim = (0, np.max(G))

    # make sure G is 2D
    if G.ndim > 2:
        raise Exception("G has too many dimensions. Size: " + str(G.shape))

    # plot gradient
    im = h.imshow(np.flipud(G), 
        clim = clim, 
        origin='lower', 
        interpolation="nearest", 
        cmap = cmap
    )

    # show annotations
    textsettings = dict(va = 'center', ha = 'center', fontsize = 10.0)

    coords = gradientspace(alphas, G.shape[0])
    #If number of elements in alpha_col doesn't match numel A,
    #take the first element and expand it to fit A
    alpha_col = checkcolors(alpha_col,coords.shape[0])
    for j in range(coords.shape[0]):        
        h.text(coords[j,0],coords[j,1], 'A',color = alpha_col[j], **textsettings)

    if len(betas)>0:
        coords = gradientspace(betas, G.shape[0])
        #If number of elements in beta_col doesn't match numel B,
        #take the first element and expand it to fit B
        beta_col = checkcolors(beta_col,coords.shape[0])
        for j in range(coords.shape[0]):
            h.text(coords[j,0],coords[j,1], 'B', color = beta_col[j], **textsettings)

    if len(gammas)>0:
        coords = gradientspace(gammas, G.shape[0])
        for j in range(coords.shape[0]):
            h.text(coords[j,0],coords[j,1], 'C', color = 'orange', **textsettings)

    h.set_yticks([])
    h.set_xticks([])
    h.set_aspect('equal', adjustable='box')
    h.axis([-0.5, G.shape[1]-0.5, -0.5, G.shape[0]-0.5])
    return im

def checkcolors(colvector,length):
    """
    Simple code to check that the color vector supplied is some 
    desired length. If it isn't, the first element is repeated 
    to that length.
    """
    import collections
    if not isinstance(colvector,str) and isinstance(colvector,collections.Sequence): #check that it is a list or sequence type but not str
        if not len(colvector) == length:
            colvector_t = colvector[:] #clone list
            cv0 = colvector_t[0]
            colvector = [cv0 for i in range(length)]
        #else: 
            #cv0 = colvector #clone 
            #colvector = [cv0 for i in range(length)]

    if isinstance(colvector,str):
        colvector = [colvector for i in range(length)]
    return colvector

def gradientspace(coords, side):
    """
    Converts a set of coordinates into integer locations within a
    gradient space from 0:side.
    
    In the returned space, the first dimension is the X axis,
    and the second dimension is the Y axis.
    """
    result = np.array(coords) / 2 + 0.5
    result = result * (side - 1)
    # result = np.fliplr(result)
    return result

