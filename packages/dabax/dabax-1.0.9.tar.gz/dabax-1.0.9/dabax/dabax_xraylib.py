import numpy
from dabax.dabax_base import DabaxBase
from dabax.dabax_xraylib_decorator import DabaxXraylibDecorator

class DabaxXraylib(DabaxBase, DabaxXraylibDecorator):
    """
    Dabax decorated with xraylib interface (warning: not all xraylib functions are implemented)
    """
    def __init__(self,
                 dabax_repository=None,
                 file_f0="f0_InterTables.dat",
                 file_f1f2="f1f2_Windt.dat",
                 file_CrossSec = "CrossSec_EPDL97.dat",
                 file_Crystals="Crystals.dat",
                 ):

        DabaxBase.__init__(self,
                           dabax_repository=dabax_repository,
                           file_f0=file_f0,
                           file_f1f2=file_f1f2,
                           file_CrossSec=file_CrossSec,
                           file_Crystals=file_Crystals)

if __name__ == "__main__":

    import xraylib
    dx = DabaxXraylib()

    if False:
        #
        # dabax vs xraylib tests
        #

        #
        # crystal tests
        #

        print("DABAX crystal list: \n",        dx.Crystal_GetCrystalsList())
        print("XRAYLIB crystal list: \n", xraylib.Crystal_GetCrystalsList())

        siD =      dx.Crystal_GetCrystal('Si')
        siX = xraylib.Crystal_GetCrystal('Si')

        print("DABAX crystal si: \n",        dx.Crystal_GetCrystal('Si'))
        print("XRAYLIB crystal si: \n", xraylib.Crystal_GetCrystal('Si'))

        print("Si 111 d-spacing: DABAX: %g, XRAYLIB: %g "% \
              (dx.Crystal_dSpacing(siD,1,1,1),xraylib.Crystal_dSpacing(siX,1,1,1)))

        print("Si 111 bragg angle at 10 keV [deg]: DABAX: %g, XRAYLIB: %g "% (\
              180 / numpy.pi * dx.Bragg_angle(siD,10, 1,1,1), \
              180 / numpy.pi * xraylib.Bragg_angle(siX, 10, 1, 1, 1)))

        # F0 = dx.Crystal_F_H_StructureFactor(siD,8.0,0,0,0,1.0,ratio_theta_thetaB=1.0)
        dabax_all_F = dx.Crystal_F_0_F_H_F_H_bar_StructureFactor(siD,8.0,1,1,1,1.0,rel_angle=1.0)

        print("F0 dabax, xraylib: ",
              dx.Crystal_F_H_StructureFactor(siD,8.0,0,0,0,1.0,1.0), dabax_all_F[0],
              xraylib.Crystal_F_H_StructureFactor(siX,8.0,0,0,0,1.0,1.0))

        print("F111 dabax, xraylib: ",
              dx.Crystal_F_H_StructureFactor     (siD,8.1,1,1,1,1.0,1.0), dabax_all_F[1],
              xraylib.Crystal_F_H_StructureFactor(siX,8.1,1,1,1,1.0,1.0))

        print("F-1-1-1 dabax, xraylib: ",
              dx.Crystal_F_H_StructureFactor     (siD,8.1,-1,-1,-1,1.0,1.0), dabax_all_F[2],
              xraylib.Crystal_F_H_StructureFactor(siX,8.1,-1,-1,-1,1.0,1.0))

        #
        # basic tools
        #
        # TODO: does not work for double parenthesis "Ga2(F(KI))3"
        for descriptor in ["H2O","Eu2H2.1O1.3","PO4", "Ca5(PO4)3.1F"]:
            print("\ncompound parsing for %s" % descriptor)
            print("DABAX: ",        dx.CompoundParser(descriptor))
            print("XRAYLIB: ", xraylib.CompoundParser(descriptor))

        print("Si is Z= %d (DABAX)  %d (XRAYLIB)" % (dx.SymbolToAtomicNumber("Si"),xraylib.SymbolToAtomicNumber("Si")))
        print("Z=23 is %s (DABAX)  %s (XRAYLIB)" % (dx.AtomicNumberToSymbol(23),xraylib.AtomicNumberToSymbol(23)))
        print("Density Z=30 %g (DABAX)  %g (XRAYLIB)" % (dx.ElementDensity(30),xraylib.ElementDensity(30)))
        print("AtWeight Z=30 %g (DABAX)  %g (XRAYLIB)" % (dx.AtomicWeight(30),xraylib.AtomicWeight(30)))


        #
        # NIST compounds
        #

        nist_x = xraylib.GetCompoundDataNISTList()
        nist_d = dx.GetCompoundDataNISTList()

        for i in range(len(nist_x)):
            # print("\n")
            # print("\n**%s**  **%s**" % (nist_x[i],nist_d[i]))
            # print (type(nist_x[i]) , type(nist_d[i]))
            if not ( nist_x[i]  in nist_d[i]):
                print(">>>> Error processing %s" % (nist_x[i]))
            print (dx.GetCompoundDataNISTByName(nist_x[i]))


        for i in range(len(nist_x)):
            print(nist_d[i], nist_x[i])
            a_d =      dx.GetCompoundDataNISTByIndex(i)
            a_x = xraylib.GetCompoundDataNISTByIndex(i)
            print("\n\n\n", i, "\n", a_d, "\n", a_x,)
            name_x = a_x["name"]
            name_d = a_d["name"]

            print(name_d, name_x)
            b_d =      dx.GetCompoundDataNISTByName(name_d)
            b_x = xraylib.GetCompoundDataNISTByName(name_x)
            print("\n", b_d, "\n", b_x,)


        print(dx.CompoundParserCheckingNIST("H2O"))
        print(dx.CompoundParserCheckingNIST("Water, Liquid"))

        #
        # scattering factors
        #

        print("Fi  dabax,xraylib: ",  dx.Fi (14,18.0), xraylib.Fi (14,18.0))
        print("Fii dabax,xraylib: ", dx.Fii(14,18.0), xraylib.Fii(14,18.0))

        print("FF_rayl dabax, xraylib: ",
              dx.FF_Rayl(17, 2.2),xraylib.FF_Rayl(17, 2.2) )
        print("FF_Rayl  dabax,xraylib: ", dx.FF_Rayl(14, 2.0), xraylib.FF_Rayl(14, 2.0))

        # loops
        energies = numpy.linspace(15,18,10)
        f1f2_d = numpy.array(dx.FiAndFii(14,energies))
        print(f1f2_d.shape)
        for i,energy in enumerate(energies):
            print("energy = %g" %energy)
            print("   Fi  dabax,xraylib: ",  f1f2_d[0,i], xraylib.Fi (14,energy))
            print("   Fii dabax,xraylib: ",  f1f2_d[1,i], xraylib.Fii(14,energy))


        from dabax.dabax_files import dabax_f1f2_files
        for file in dabax_f1f2_files():
            dx1 = DabaxXraylib(file_f1f2=file)
            print("\nFi  dabax (%s): %g ,xraylib: %g" % (file, dx1.Fi(14, 18.0), xraylib.Fi(14, 18.0)))
            print("Fii  dabax (%s): %g ,xraylib: %g" % (file, dx1.Fii(14, 18.0), xraylib.Fii(14, 18.0)))


        #
        # cross sections
        #

        from dabax.dabax_files import dabax_crosssec_files

        for file in dabax_crosssec_files():
            dx1 = DabaxXraylib(file_CrossSec=file)
            print(">>>>>>>>>>>>>>>  file: ", file)
            try:
                print("CSb_Total Si dabax,xraylib: ",  dx1.CSb_Total(14, 18.0), xraylib.CSb_Total(14, 18.0))
                print("CSb_Photo Si dabax,xraylib: ",  dx1.CSb_Photo(14,18.0),  xraylib.CSb_Photo(14,18.0))
                print("CSb_Rayl  Si dabax,xraylib: ",  dx1.CSb_Rayl (14,18.0),  xraylib.CSb_Rayl (14,18.0))
                print("CSb_Compt Si dabax,xraylib: ",  dx1.CSb_Compt(14,18.0),  xraylib.CSb_Compt(14,18.0))

                print("CS_Total Si dabax,xraylib: ",  dx1.CS_Total(14, 18.0), xraylib.CS_Total(14, 18.0))
                print("CS_Photo Si dabax,xraylib: ",  dx1.CS_Photo(14,18.0),  xraylib.CS_Photo(14,18.0))
                print("CS_Rayl  Si dabax,xraylib: ",  dx1.CS_Rayl (14,18.0),  xraylib.CS_Rayl (14,18.0))
                print("CS_Compt Si dabax,xraylib: ",  dx1.CS_Compt(14,18.0),  xraylib.CS_Compt(14,18.0))
            except:
                print("!!!!!!!!!!Errors with file", file)


        for file in dabax_crosssec_files():
            dx1 = DabaxXraylib(file_CrossSec=file)
            print(">>>>>>>>>>>>>>>  file: ", file)

            try:
                print("CSb_Total SiO2 dabax,xraylib: ",  dx1.CSb_Total_CP("SiO2", 18.0), xraylib.CSb_Total_CP("SiO2", 18.0))
                print("CSb_Photo SiO2 dabax,xraylib: ",  dx1.CSb_Photo_CP("SiO2",18.0),  xraylib.CSb_Photo_CP("SiO2",18.0))
                print("CSb_Rayl  SiO2 dabax,xraylib: ",   dx1.CSb_Rayl_CP("SiO2",18.0),   xraylib.CSb_Rayl_CP("SiO2",18.0))
                print("CSb_Compt SiO2 dabax,xraylib: ",  dx1.CSb_Compt_CP("SiO2",18.0),  xraylib.CSb_Compt_CP("SiO2",18.0))

                print("CS_Total SiO2 dabax,xraylib: ",  dx1.CS_Total_CP("SiO2", 18.0), xraylib.CS_Total_CP("SiO2", 18.0))
                print("CS_Photo SiO2 dabax,xraylib: ",  dx1.CS_Photo_CP("SiO2",18.0),  xraylib.CS_Photo_CP("SiO2",18.0))
                print("CS_Rayl  SiO2 dabax,xraylib: ",   dx1.CS_Rayl_CP("SiO2",18.0),   xraylib.CS_Rayl_CP("SiO2",18.0))
                print("CS_Compt SiO2 dabax,xraylib: ",  dx1.CS_Compt_CP("SiO2",18.0),  xraylib.CS_Compt_CP("SiO2",18.0))
            except:
                print("!!!!!!!!!!Errors with file", file)


        #
        # refractive index
        #
        dens = dx.element_density("Be")
        print("Refractive_Index_Re Be  dabax,xraylib: ",  dx.Refractive_Index_Re ("Be",18.0, dens), xraylib.Refractive_Index_Re ("Be",18.0, dens))
        print("Refractive_Index_Im Be  dabax,xraylib: ",  dx.Refractive_Index_Im ("Be",18.0, dens), xraylib.Refractive_Index_Im ("Be",18.0, dens))
        print("Refractive_Index Be  dabax,xraylib: ",  dx.Refractive_Index ("Be",18.0, dens), xraylib.Refractive_Index ("Be",18.0, dens))

        # loops
        energies = numpy.linspace(15,18,10)
        r1 = dx.Refractive_Index_Re("Be", energies, dens)
        for i,energy in enumerate(energies):
            print("   delta @ %g keV, dabax: %g ,xraylib: %g" % (energy, 1-r1[i], 1-xraylib.Refractive_Index_Re ("Be",energy, dens)))

    else:
        pass


