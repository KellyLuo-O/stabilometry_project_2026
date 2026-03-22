import numpy as np

def build_mask_cfar_dp(Data_range_MTI, range_axis, dt, vmax, **kwargs):
    """
    Détection range x time + suivi par programmation dynamique.
    """
    # Paramètres par défaut
    opt = {
        'MinRange': np.min(range_axis),
        'MaxRange': np.max(range_axis),
        'Mode': 'SOCA',
        'Train': 8,
        'Guard': 2,
        'Pfa': 1e-3,
        'Beta': 5.0,
        'Lambda1': 1.0,
        'Lambda2': 0.1,
        'BandHalfWidth': 0.4,
        'SoftSigma': 0.4,
        'SoftFloor': 0.05
    }
    opt.update(kwargs)

    Rlin = np.abs(Data_range_MTI)**2
    Nr, Nt = Rlin.shape
    dR = np.median(np.diff(range_axis))

    # Masque de portée
    range_mask = (range_axis >= opt['MinRange']) & (range_axis <= opt['MaxRange'])
    
    # --- CFAR ---
    B = np.zeros((Nr, Nt), dtype=bool)
    Thr = np.zeros((Nr, Nt))
    
    for t in range(Nt):
        x = Rlin[:, t]
        cs = np.concatenate(([0], np.cumsum(x)))
        for r in range(Nr):
            L2 = r - opt['Guard'] - 1
            L1 = max(0, L2 - opt['Train'] + 1)
            R1 = r + opt['Guard'] + 1
            R2 = min(Nr - 1, R1 + opt['Train'] - 1)

            SL, NL = 0, 0
            if L2 >= L1:
                SL = cs[L2+1] - cs[L1]
                NL = L2 - L1 + 1
            
            SR, NRi = 0, 0
            if R2 >= R1:
                SR = cs[R2+1] - cs[R1]
                NRi = R2 - R1 + 1

            if opt['Mode'] == 'SOCA':
                if NL == 0 and NRi == 0:
                    Thr[r, t] = np.inf
                elif NL == 0: Sside, Nside = SR, NRi
                elif NRi == 0: Sside, Nside = SL, NL
                else:
                    if SL <= SR: Sside, Nside = SL, NL
                    else: Sside, Nside = SR, NRi
                
                kfac = (opt['Pfa']**(-1.0/max(Nside, 1)) - 1)
                Thr[r, t] = kfac * Sside
            else: # CA-CFAR
                N = NL + NRi
                if N < 4: Thr[r, t] = np.inf
                else:
                    kfac = (opt['Pfa']**(-1.0/N) - 1)
                    Thr[r, t] = kfac * (SL + SR)
        
        B[:, t] = Rlin[:, t] > Thr[:, t]

    B[~range_mask, :] = False

    # --- Programmation Dynamique ---
    # Coût d'observation
    # movmean approximé par une convolution simple
    kernel = np.ones(25) / 25
    Rnorm = np.zeros_like(Rlin)
    for t in range(Nt):
        Rnorm[:, t] = Rlin[:, t] / (np.convolve(Rlin[:, t], kernel, mode='same') + 1e-12)
    
    C = -np.log(Rnorm + 1e-6)
    C[~B] += opt['Beta']
    C[~range_mask, :] = np.inf

    w = max(1, int(np.ceil((vmax * dt) / dR)))
    D = np.full((Nr, Nt), np.inf)
    Prev = np.zeros((Nr, Nt), dtype=int)
    D[:, 0] = C[:, 0]

    for t in range(1, Nt):
        for r in range(Nr):
            rmin = max(0, r - w)
            rmax = min(Nr - 1, r + w)
            rr = np.arange(rmin, rmax + 1)
            
            dr = rr - r
            transition_costs = D[rr, t-1] + opt['Lambda1']*np.abs(dr) + opt['Lambda2']*(dr**2)
            idx = np.argmin(transition_costs)
            D[r, t] = C[r, t] + transition_costs[idx]
            Prev[r, t] = rmin + idx

    # Backtracking
    rhat = np.zeros(Nt, dtype=int)
    rhat[-1] = np.argmin(D[:, -1])
    for t in range(Nt-1, 0, -1):
        rhat[t-1] = Prev[rhat[t], t]

    # --- Masques de sortie ---
    k = max(1, int(round(opt['BandHalfWidth'] / dR)))
    M = np.zeros((Nr, Nt), dtype=bool)
    for t in range(Nt):
        r1 = max(0, rhat[t] - k)
        r2 = min(Nr - 1, rhat[t] + k)
        M[r1:r2+1, t] = True

    sigmaBins = max(1, opt['SoftSigma'] / dR)
    rr_grid = np.arange(Nr)[:, None]
    W = np.exp(-(rr_grid - rhat)**2 / (2 * sigmaBins**2))
    W = np.maximum(W, opt['SoftFloor'])

    return M, W, rhat, Thr, B