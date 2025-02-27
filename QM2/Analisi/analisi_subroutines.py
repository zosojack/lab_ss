'''
    SUBROUTINES PER L'ANALISI DEI CAMPIONI C240830 E C240920
    
    Nelle funzioni si inserisce anche la possibilità di fittare con Varshni
'''

import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from varshni_subroutines import varshni

# per le iterazioni
d_o_emi = ['0', '0o5', '1', '1o5', '2', '2o5', '3']#, '3o5']
d_o_ass = ['1', '0']
arr_temperatura = [15, 30, 45, 70, 100, 150]

# singola gaussiana
def gaussiana(x, a, mu, sigma):
        if sigma == 0:
            sigma = 0.1
        return a * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
    
# per un tocco di colore
col = ['red', 'green', 'magenta', 'purple', 'peru', 'cyan', 'olive', 
       'goldenrod', 'black', 'sienna', 'steelblue', 'crimson', 'violet',
       'darkorange', 'rosybrown', 'cadetblue', 'navy', 'royalblue', 
       'slategrey', 'forestgreen', 'lightcoral', 'hotpink']

# conversione lambda (nm) in E (eV)
def lambda_to_E (wavelength: float):
    h_in_ev = 4.1357e-15
    c_luce  = 299792458
    
    if isinstance(wavelength, (int, float)):  # Caso scalare
        return h_in_ev * c_luce / (wavelength * 1e-09) if wavelength != 0 else 0

    elif isinstance(wavelength, np.ndarray):  # Caso np.array
        return h_in_ev * c_luce / (wavelength * 1e-09)

    elif isinstance(wavelength, list):  # Caso lista
        return np.array([h_in_ev * c_luce / (wv * 1e-09) for wv in wavelength])

    else:
        raise TypeError("Input non supportato. Usa float, list o np.ndarray.")

# propagazione errore lambda (nm) in E (eV)
def err_lambda_to_E(wavelength, err_wavelength):
    h_in_ev = 4.1357e-15
    c_luce = 299792458

    wavelength = np.asarray(wavelength)
    err_wavelength = np.asarray(err_wavelength)

    return np.where(wavelength != 0, h_in_ev * c_luce * err_wavelength / (wavelength**2 * 1e-09), 0)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## PER ANALISI FIT VARSHNI ##
def analisi_fit_varshni (x, y, popt, yerr):

        ## Residui del picco SX
        residui1 = y - varshni(x, *popt)
        chi2 = np.sum((residui1 / yerr) ** 2)

        # Gradi di libertà (numero dati - numero parametri del fit)
        gdl = len(y) - len(popt)
        
        return chi2, gdl

def media_pesata (x, err):
    x = np.array(x)
    err = np.array(err)
    
    pesi = 1 / err**2  # I pesi sono l'inverso del quadrato degli errori
    media = np.sum(x * pesi) / np.sum(pesi)
    errore_media = np.sqrt(1 / np.sum(pesi))
    
    return media, errore_media

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## PER I PLOT ##

# SU TEMPERATURA
def plot_su_T (picchi, option, x=None, d_o_ass=None, d_o_emi=None, arr_temperatura=None, 
               col=None, materiale=None, campione=None, VARSHNI=False):
    """
    Genera un grafico della dipendenza di una grandezza fisica dalla temperatura per diversi stati di assorbimento ed emissione.

    Args:
        picchi (dict): Dizionario contenente i dati dei picchi per diverse condizioni.
        option (str): Specifica la grandezza da plottare. Può essere:
                      - 'mu' per l'energia del picco (eV)
                      - 'fwhm' per la larghezza a metà altezza (FWHM) (eV)
                      - 'area' per l'area del picco (a.u.)
        x (list, optional): Valori della temperatura da usare come ascisse. Se None, viene determinato automaticamente.
        d_o_ass (list, optional): Livelli di assorbimento considerati. Default ['1', '0'].
        d_o_emi (list, optional): Livelli di emissione considerati. Default ['0', '0o5', ..., '3'].
        arr_temperatura (list, optional): Valori della temperatura. Default in base al materiale.
        col (list, optional): Colori per le curve nel grafico.
        materiale (str, optional): Nome del materiale (es. 'GaAs', 'AlGaAs', 'QD').

    Raises:
        KeyError: Se 'option' non è tra 'mu', 'fwhm' o 'area'.

    """
    
    if d_o_ass is None:
        d_o_ass = ['1', '0']
    if d_o_emi is None:
        d_o_emi = ['0', '0o5', '1', '1o5', '2', '2o5', '3']#, '3o5']
    if arr_temperatura is None:
        if materiale == 'AlGaAs':
            arr_temperatura = [15, 30, 45]
        elif materiale == 'QD':
            arr_temperatura = [15, 30, 45, 70, 100]
        elif materiale == 'Difetto':
            arr_temperatura = [15]
            if isinstance(arr_temperatura, (int, float, np.float64)):  # Se è un singolo numero
                arr_temperatura = [arr_temperatura]  # Lo converto in lista
        else:
            arr_temperatura = [15, 30, 45, 70, 100, 150] # comprende il caso GaAs
            
    x = arr_temperatura
    
    if VARSHNI:
        # printo un messaggio
        print("RISULTATI FIT VARSHNI")
        # predispongo due vettori per la media pesata
        e_gap = []
        err_e_gap = [] 
    
    plt.figure(figsize=(6, 4), dpi=200)
    j=0
    for ass in d_o_ass:
        ass = 'ass=' + ass 
        emi_list = d_o_emi[1:] if ass == 'ass=0' else ['0']  # Per ass=1 usa solo emi='0'
        
        # Per ciascuno degli emi > 0 se ass=0, solo emi=0 se ass=1
        for emi in emi_list:
            emi = 'emi=' + emi
            
            y1 = []
            err1 = []
            
            # estraggo le info
            for i, temp in enumerate(arr_temperatura):
                
                if option == 'mu':
                    y1.append(picchi[ass+emi][i][1])
                    err1.append(picchi[ass+emi][i][3])
                elif option == 'fwhm':
                    y1.append(picchi[ass+emi][i][2]*2.35482004503)
                    err1.append(0)
                elif option == 'area':
                    y1.append(picchi[ass+emi][i][0]*picchi[ass+emi][i][2]*np.sqrt(2*np.pi))
                    err1.append(0)
                else:
                    raise KeyError ("Le opzioni sono 'mu', 'fwhm' o 'area'")
                                                
            # li inverto poi li ri-inverto
            help = emi
            emi = ass
            ass = help

            # plotto
            plt.errorbar(x, y1, yerr=err1, ecolor=col[j], fmt='none', elinewidth=1, capsize=1)
            plt.scatter(x, y1, color=col[j], marker='x', label=ass+'|'+emi, s=25)
            plt.plot(x, y1, linestyle='--', color=col[j], linewidth=0.5) # unisce i punti
            
            # --- # OPZIONE VARSHNI # --- # OPZIONE VARSHNI # --- # OPZIONE VARSHNI # --- # OPZIONE VARSHNI # --- #
            
            # Se l'opzione VARSHNI è su True, il plot su temperatura viene fittato con la legge di Varshni
            if VARSHNI:
                # Fit Varshni
                popt, pcov = curve_fit(varshni, x, y1, sigma=err1, absolute_sigma=True, p0=[x[0], 3, 1], 
                            bounds=([0, -np.inf, 0], [np.inf, np.inf, np.inf]))
                # Errori sui parametri
                perr = np.sqrt(np.diag(pcov))  # Errori per il primo picco
                
                # Creazione del grafico
                x_fit = np.linspace(x[0], x[-1], x[-1]-x[0])  # Creazione di un intervallo continuo per il grafico
                # Plot del fit
                plt.plot(x_fit, varshni(x_fit, *popt), color=col[j], linewidth=0.25)
                
                chi2, gdl = analisi_fit_varshni(x, y1, popt, err1)
                
                # raccolta dei risultati e print
                # Stampa dei risultati
                print(F"- - - - - - - - - - - - - - - - < {ass} & {emi} > - - - - - - - - - - - - - - - -")
                print(f"E_0 = {popt[0]:.4f} ± {perr[0]:.4f} | alpha = {popt[1]:.4f} ± {perr[1]:.4f} | beta = {popt[2]:.4f} ± {perr[2]:.4f}")
                
                e_gap.append(popt[0])
                err_e_gap.append(perr[0])
                
                if gdl != 0:
                    print(f"• Chi quadro ridotto: {chi2:.3f}/{gdl}={chi2/gdl:.3f}")    
                else: 
                    print(f"• Chi quadro ridotto: {chi2:.3f}/0=inf") 
                
             # --- # OPZIONE VARSHNI # --- # OPZIONE VARSHNI # --- # OPZIONE VARSHNI # --- # OPZIONE VARSHNI # --- #
            
            # ri-inverto
            ass = emi
            emi = help
            
            j += 1
    
    # SE L'OPZIONE VARSHNI È ATTIVA, CALCOLO LA MEDIA PESATA DEGLI E_0    
    if VARSHNI:
        # calcolo
        media_gap, errore_media_gap = media_pesata(e_gap, err_e_gap)
        # stampo a schermo
        print(F"- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        print(f'\nMEDIA PESATA E_GAP = {media_gap} ± {errore_media_gap}')

    # li inverto poi li ri-inverto
    help = emi
    emi = ass
    ass = help
        
    # Aggiungere etichette e legenda
    if campione:
        materiale = campione + ' | ' + materiale
    
    if option == 'mu':
        plt.title(materiale+': ENERGIA su T')
        plt.ylabel('Energia (eV)')
    elif option == 'fwhm':
        plt.title(materiale+': FWHM su T')
        plt.ylabel('FWHM (eV)')
    elif option == 'area':
        plt.title(materiale+': AREA su T')
        plt.ylabel('Area (a.u.)')
        
    plt.xlabel('Temperatura (K)')
    
    plt.grid(linestyle='--')
    plt.legend()
    # ri-inverto
    ass = emi
    emi = help

    # Mostrare il grafico
    plt.tight_layout()
    plt.show()
    
# SU INTENSITÀ
def plot_su_int (picchi, option, x=None, d_o_ass=None, d_o_emi=None, arr_temperatura=None, 
                 col=None, materiale=None, campione=None):
    """
    Genera un grafico della dipendenza di una grandezza fisica dall'intensità per diverse temperature.

    Args:
        picchi (dict): Dizionario contenente i dati dei picchi per diverse condizioni.
        option (str): Specifica la grandezza da plottare. Può essere:
                      - 'mu' per l'energia del picco (eV)
                      - 'fwhm' per la larghezza a metà altezza (FWHM) (eV)
                      - 'area' per l'area del picco (a.u.)
        x (list, optional): Indici delle intensità da usare come ascisse. Default numerico.
        d_o_ass (list, optional): Livelli di assorbimento considerati. Default ['1', '0'].
        d_o_emi (list, optional): Livelli di emissione considerati. Default ['0', '0o5', ..., '3'].
        arr_temperatura (list, optional): Valori della temperatura. Default in base al materiale.
        col (list, optional): Colori per le curve nel grafico.
        materiale (str, optional): Nome del materiale (es. 'GaAs', 'AlGaAs', 'QD').

    Raises:
        KeyError: Se 'option' non è tra 'mu', 'fwhm' o 'area'.
    """
    
    if d_o_ass is None:
        d_o_ass = ['1', '0']
    if d_o_emi is None:
        d_o_emi = ['0', '0o5', '1', '1o5', '2', '2o5', '3']#, '3o5']
    if arr_temperatura is None:
        if materiale == 'AlGaAs':
            arr_temperatura = [15, 30, 45]
        elif materiale == 'QD':
            arr_temperatura = [15, 30, 45, 70, 100]
        elif materiale == 'Difetto':
            arr_temperatura = [15]
            if isinstance(arr_temperatura, (int, float, np.float64)):  # Se è un singolo numero
                arr_temperatura = [arr_temperatura]  # Lo converto in lista
        else:
            arr_temperatura = [15, 30, 45, 70, 100, 150] # comprende il caso GaAs
    
    etichette_x = ["ass=0\nemi=1", 
                   "ass=0.5\nemi=0", 
                   "ass=1\nemi=0", 
                   "ass=1.5\nemi=0", 
                   "ass=2\nemi=0", 
                   "ass=2.5\nemi=0", 
                   "ass=3\nemi=0"]
    
    x = np.arange(1,8)
    
    plt.figure(figsize=(6, 4), dpi=200)
    j=0
    for i, temp in enumerate(arr_temperatura):
                
        y1 = []
        err1 = [] 
                
        for ass in d_o_ass:
            ass = 'ass=' + ass 
            emi_list = d_o_emi[1:] if ass == 'ass=0' else ['0']  # Per ass=1 usa solo emi='0'
            
            # Per ciascuno degli emi > 0 se ass=0, solo emi=0 se ass=1
            for emi in emi_list:
                emi = 'emi=' + emi
            
                # estraggo le info, eliminando punti brutti
                if emi in ('emi=2o5','emi=3') and temp == 45:
                    y1.append(np.nan)
                    err1.append(np.nan)
                else:
    
                    if option == 'mu':
                        y1.append(picchi[ass+emi][i][1])
                        err1.append(picchi[ass+emi][i][3])
                    elif option == 'fwhm':
                        y1.append(picchi[ass+emi][i][2]*2.35482004503)
                        err1.append(0)
                    elif option == 'area':
                        y1.append(picchi[ass+emi][i][0]*picchi[ass+emi][i][2]*np.sqrt(2*np.pi))
                        err1.append(0)
                    else:
                        raise KeyError ("Le opzioni sono 'mu', 'fwhm' o 'area'")
        
        # li inverto poi li ri-inverto
        help = emi
        emi = ass
        ass = help

        # plotto
        plt.errorbar(x, y1, yerr=err1, ecolor=col[j], fmt='none', elinewidth=1, capsize=1)
        plt.scatter(x, y1, color=col[j], marker='x', label='T='+str(temp), s=25)
        plt.plot(x, y1, linestyle='--', color=col[j], linewidth=0.5) # unisce i punti        
        
        # ri-inverto
        ass = emi
        emi = help
        
        j += 1

    # li inverto poi li ri-inverto
    help = emi
    emi = ass
    ass = help
    
    # Aggiungere etichette e legenda
    if campione:
        materiale = campione + ' | ' + materiale
        
    if option == 'mu':
        plt.title(materiale+': ENERGIA su Intensità')
        plt.ylabel('Energia (eV)')
    elif option == 'fwhm':
        plt.title(materiale+': FWHM su Intensità')
        plt.ylabel('FWHM (eV)')
    elif option == 'area':
        plt.title(materiale+': AREA su Intensità')
        plt.ylabel('Area (a.u.)')
            
    plt.xlabel('Intensità')
    plt.xticks(range(1, 8), etichette_x)
    plt.grid(linestyle='--')
    plt.legend()
    # ri-inverto
    ass = emi
    emi = help

    # Mostrare il grafico
    plt.tight_layout()
    plt.show()