
def dabax_f0_files():
    return ["f0_InterTables.dat", "f0_WaasKirf.dat", "f0_xop.dat"]

def dabax_f1f2_files():
    return ["f1f2_Windt.dat",
            "f1f2_Sasaki.dat",
            "f1f2_Henke.dat",
            "f1f2_EPDL97.dat",
            "f1f2_CromerLiberman.dat",
            "f1f2_Chantler.dat",
            "f1f2_BrennanCowan.dat",
            "f1f2_asf_Kissel.dat",
            ]

def dabax_crosssec_files():
    return ["CrossSec_EPDL97.dat",
            "CrossSec_XCOM.dat",
            "CrossSec_BrennanCowan.dat",
            "CrossSec_StormIsrael.dat",
            "CrossSec_McMaster.dat",
            # "CrossSec_NISTxaamdi.dat",   # they do not contain partial cross sections (compton, rayl, photo)
            # "CrossSec_PE_Scofield.dat",   # they do not contain partial cross sections (compton, rayl, photo)
            ]