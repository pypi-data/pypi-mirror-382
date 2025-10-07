#
# dabax functions with the same interface as xraylib
#
import numpy
import scipy.constants as codata
from silx.io.specfile import SpecFile
from dabax.common_tools import atomic_symbols, atomic_names, atomic_number
from dabax.common_tools import bragg_metrictensor
from dabax.common_tools import calculate_f0_from_f0coeff

class DabaxXraylibDecorator(object):

    #########################
    # crystals
    #########################
    def Crystal_GetCrystal(self, entry_name='YB66'):
        """
        parse a complex crystal structure file into a dictionary (like xraylib.Crystal_GetCrystal('Si'))

        it has an additional fiels for each atom: the charge

        return a dictionary containing crystal infomation
        """
        dabax_repository = self.get_dabax_repository()

        filename = self.get_file_Crystals()

        file1 = self.get_dabax_file(filename)

        if self.verbose(): print("Accessing file: %s" % file1)
        sf = SpecFile(file1)

        flag_found = False

        for index in range(len(sf)):
            s1 = sf[index]
            name = s1.scan_header_dict["S"]
            if name.split(' ')[1] == entry_name:
                flag_found = True
                index_found = index

        if not flag_found:
            raise (Exception("Entry name not found: %s" % entry_name))

        cryst = {'name': entry_name}  # returned dictionary like that one created by xraylib.Crystal_GetCrystal(descriptor)

        cell_parameters = sf[index_found].scan_header_dict["UCELL"]
        cell_parameters = ' '.join(cell_parameters.split())  # remove multiple blanks

        a = cell_parameters.split(' ')
        cryst['a'] = float(a[0])
        cryst['b'] = float(a[1])
        cryst['c'] = float(a[2])
        cryst['alpha'] = float(a[3])
        cryst['beta'] = float(a[4])
        cryst['gamma'] = float(a[5])

        volume = bragg_metrictensor(float(a[0]), float(a[1]), float(a[2]),
                                    float(a[3]), float(a[4]), float(a[5]), RETURN_VOLUME=1)

        cryst['volume'] = volume

        cell_data = numpy.array(sf[index_found].data)

        cryst['n_atom'] = cell_data.shape[1]
        atom = []

        for i in range(cell_data.shape[1]):
            if cell_data.shape[0] == 5:  # standard 5 columns
                # not here, this info is not in the dabax file
                # s = symbol_to_from_atomic_number(int(cell_data[0,i]))
                atom.append({
                    'Zatom': int(cell_data[0, i]),
                    'fraction': cell_data[1, i],
                    'x': cell_data[2, i],
                    'y': cell_data[3, i],
                    'z': cell_data[4, i],
                    'charge': 0.0, })
            else:  # 6 columns (charge)
                # 'AtomicName' required to compatible my current code
                # s = symbol_to_from_atomic_number(int(cell_data[0,i]))
                # if cell_data[5, i] != 0:  #charged
                #     s = s + f'%+.6g'%cell_data[5, i]
                atom.append({
                    # 'AtomicName': s,
                    'Zatom': int(cell_data[0, i]),
                    'fraction': cell_data[1, i],
                    'x': cell_data[2, i],
                    'y': cell_data[3, i],
                    'z': cell_data[4, i],
                    'charge': cell_data[5, i], })

        cryst['atom'] = atom
        cryst['cpointer'] = None

        ANISO_KEY = "UANISO_COFF"  # prefix for a line with anisotropic coefficients
        d = sf[index_found].scan_header_dict
        AnisoItem = {'Name': '       ',
                     'start': 0,
                     'end': 0,
                     'beta11': 0.0,
                     'beta22': 0.0,
                     'beta33': 0.0,
                     'beta12': 0.0,
                     'beta13': 0.0,
                     'beta23': 0.0}

        a = [(x, d[x].split()) for x in d if x[:len(ANISO_KEY)] == ANISO_KEY]
        if len(a) > 0:  # found Anisotropic coefficients in the header, process it
            a = sorted(a, key=lambda x: int(x[1][0]),
                       reverse=False)  # sort 'Start' ascendant, avoid order changed by the SpecFile
            n = 0
            Aniso = []
            for x in a:  # tuple('UANISO_COFF_B1',[1 96 0.00038 0.00044 0.00039 0 0 0])
                AnisoItem['Name'] = x[0][len(ANISO_KEY) + 1:]  # get site atom name starting from 13th character 'B1', etc
                AnisoItem['start'] = int(x[1][0])
                AnisoItem['end'] = int(x[1][1])
                AnisoItem['beta11'] = float(x[1][2])
                AnisoItem['beta22'] = float(x[1][3])
                AnisoItem['beta33'] = float(x[1][4])
                AnisoItem['beta12'] = float(x[1][5])
                AnisoItem['beta13'] = float(x[1][6])
                AnisoItem['beta23'] = float(x[1][7])
                Aniso.append(AnisoItem.copy())
                n = n + 1
            cryst['Aniso'] = Aniso  # if having key 'Ansio' when there is anisotropic data,otherwise no
            cryst['n_aniso'] = n
        else:  # create a dummy Aniso to compatible with xraylib
            cryst['Aniso'] = [AnisoItem.copy()]
            cryst['n_aniso'] = 1

        return cryst


    def Crystal_GetCrystalsList(self):
        """
        get crystal names from crystals.dat
        """
        file1 = self.get_dabax_file(self.get_file_Crystals())
        if self.verbose(): print("Accessing file: %s" % file1)
        sf = SpecFile(file1)
        crystals = []
        for index in range(len(sf)):
            s1 = sf[index]
            name = s1.scan_header_dict["S"]
            crystals.append(name.split(' ')[1])

        return crystals

    def Crystal_dSpacing(self, cryst, h, k, l):
        return bragg_metrictensor(cryst['a'], cryst['b'], cryst['c'],
                                  cryst['alpha'], cryst['beta'], cryst['gamma'],
                                  HKL=[h, k, l])

    def Bragg_angle(self, cryst, E_keV, h, k, l):
        dspacing = self.Crystal_dSpacing(cryst, h, k, l)  # in A
        wavelength = codata.h * codata.c / codata.e / (E_keV * 1e3) * 1e10  # in A
        return numpy.arcsin(wavelength / 2 / dspacing)

    def Crystal_F_H_StructureFactor(self,
                                    crystal_id,
                                    energy_in_kev,
                                    millerH,
                                    millerK,
                                    millerL,
                                    debyeWaller,
                                    ratio_theta_thetaB=1.0):
        energy = energy_in_kev * 1e3
        wavelength = codata.h * codata.c / codata.e / energy * 1e10
        # print(crystal_id["n_atom"])
        atom = crystal_id['atom']
        natom = len(atom)
        list_fraction = [atom[i]['fraction'] for i in range(natom)]
        list_x = [atom[i]['x'] for i in range(natom)]
        list_y = [atom[i]['y'] for i in range(natom)]
        list_z = [atom[i]['z'] for i in range(natom)]

        F_H = numpy.zeros(numpy.array(energy).size, dtype=complex)

        for i in range(natom):
            atom_i = atom[i]
            if (i > 0) and (atom_i['Zatom'] == Z_i) and (atom_i['charge'] == charge_i):
                pass # avoid re-calculating f0 if inputs are identical to previous call
            else:
                Z_i = atom_i['Zatom']
                charge_i = atom_i['charge']
                coeffs = self.f0_with_fractional_charge(Z_i, charge=charge_i)
                if (millerH == 0 and millerK == 0 and millerL == 0):
                    ratio = 0.0
                else:
                    angle = self.Bragg_angle(crystal_id, energy_in_kev,
                                             millerH, millerK, millerL) * ratio_theta_thetaB
                    ratio = numpy.sin(angle) / wavelength
                f0_i = calculate_f0_from_f0coeff(coeffs, ratio)
                Fi  = self.Fi(Z_i, energy_in_kev)
                Fii = self.Fii(Z_i, energy_in_kev)

            F_H += (f0_i + Fi - Fii * 1j) * list_fraction[i] * \
                   numpy.exp(2j*numpy.pi*(millerH*list_x[i]+millerK*list_y[i]+millerL*list_z[i]))

        return F_H * debyeWaller

    #########################
    #  misc
    #########################
    def CompoundParser(self, descriptor):
        return self.compound_parser(descriptor)

    def SymbolToAtomicNumber(self, symbol):
        return atomic_number(symbol)

    def AtomicNumberToSymbol(self, Z):
        return atomic_symbols()[Z]

    def ElementDensity(self, Z):
        return self.element_density(self.AtomicNumberToSymbol(Z))

    def AtomicWeight(self, Z):
        return self.atomic_weights(self.AtomicNumberToSymbol(Z))

    #########################
    #  scattering functions
    #########################
    def Fi(self, Z, energy):
        return self.FiAndFii(Z, energy)[0]

    def Fii(self, Z, energy):
        return self.FiAndFii(Z, energy)[1]

    def FF_Rayl(self, Z, q):

        coeffs = self.f0_with_fractional_charge(Z, charge=0.0)
        return calculate_f0_from_f0coeff(coeffs, q)

    #########################
    #  cross sections
    #########################

    # main (barns)
    def CSb_Total(self, Z, energy):
        return self.crosssec_interpolate(self.AtomicNumberToSymbol(Z), energy * 1e3,
                                         partial='TotalCrossSection[barn/atom]',)

    def CSb_Photo(self, Z, energy):
        return self.crosssec_interpolate(self.AtomicNumberToSymbol(Z), energy * 1e3,
                                         partial='PhotoElectric[barn/atom]',)
    def CSb_Rayl(self, Z, energy):
        return self.crosssec_interpolate(self.AtomicNumberToSymbol(Z), energy * 1e3,
                                         partial='Rayleigh(coherent)[barn/atom]',)

    def CSb_Compt(self, Z, energy):
        return self.crosssec_interpolate(self.AtomicNumberToSymbol(Z), energy * 1e3,
                                         partial='Compton(incoherent)[barn/atom]',)

    # in cm2/g

    def CS_Total(self, Z, energy):
        return self.CSb_Total(Z, energy) * (codata.Avogadro * 1e-24 / self.AtomicWeight(Z))

    def CS_Photo(self, Z, energy):
        return self.CSb_Photo(Z, energy) * (codata.Avogadro * 1e-24 / self.AtomicWeight(Z))

    def CS_Rayl(self, Z, energy):
        return self.CSb_Rayl(Z, energy) * (codata.Avogadro * 1e-24 / self.AtomicWeight(Z))

    def CS_Compt(self, Z, energy):
        return self.CSb_Compt(Z, energy) * (codata.Avogadro * 1e-24 / self.AtomicWeight(Z))


    # for compounds


    def CS_Total_CP(self, descriptor, energy):
        cp = self.CompoundParserCheckingNIST(descriptor,)
        out = 0.0
        for i in range(cp["nElements"]):
            out += self.CS_Total(cp["Elements"][i], energy) * cp["massFractions"][i]
        return out

    def CSb_Total_CP(self, descriptor, energy):
        cp = self.CompoundParserCheckingNIST(descriptor,)
        out = 0.0
        for i in range(cp["nElements"]):
            out += self.CSb_Total(cp["Elements"][i], energy) * cp["massFractions"][i]
        return out

    def CS_Photo_CP(self, descriptor, energy):
        cp = self.CompoundParserCheckingNIST(descriptor,)
        out = 0.0
        for i in range(cp["nElements"]):
            out += self.CS_Photo(cp["Elements"][i], energy) * cp["massFractions"][i]
        return out

    def CSb_Photo_CP(self, descriptor, energy):
        cp = self.CompoundParserCheckingNIST(descriptor,)
        out = 0.0
        for i in range(cp["nElements"]):
            out += self.CSb_Photo(cp["Elements"][i], energy) * cp["massFractions"][i]
        return out

    def CS_Rayl_CP(self, descriptor, energy):
        cp = self.CompoundParserCheckingNIST(descriptor,)
        out = 0.0
        for i in range(cp["nElements"]):
            out += self.CS_Rayl(cp["Elements"][i], energy) * cp["massFractions"][i]
        return out

    def CSb_Rayl_CP(self, descriptor, energy):
        cp = self.CompoundParserCheckingNIST(descriptor,)
        out = 0.0
        for i in range(cp["nElements"]):
            out += self.CSb_Rayl(cp["Elements"][i], energy) * cp["massFractions"][i]
        return out

    def CS_Compt_CP(self, descriptor, energy):
        cp = self.CompoundParserCheckingNIST(descriptor,)
        out = 0.0
        for i in range(cp["nElements"]):
            out += self.CS_Compt(cp["Elements"][i], energy) * cp["massFractions"][i]
        return out

    def CSb_Compt_CP(self, descriptor, energy):
        cp = self.CompoundParserCheckingNIST(descriptor,)
        out = 0.0
        for i in range(cp["nElements"]):
            out += self.CSb_Compt(cp["Elements"][i], energy) * cp["massFractions"][i]
        return out

    #########################
    #  refractive index
    #########################

    def Refractive_Index(self, descriptor, energy, density):
        cp = self.compound_parser(descriptor)
        KD = 4.15179082788e-4  # TODO: recalculate with codata....
        rv_re = 0.0
        rv_im = 0.0
        for i in range(cp["nElements"]):
            Z = cp["Elements"][i]
            rv_re += cp["massFractions"][i] * KD * (Z + self.Fi(Z, energy)) / self.AtomicWeight(Z) / energy / energy
            rv_im += self.CS_Total(Z, energy) * cp["massFractions"][i]

        return (1 - rv_re * density) + 1j*(rv_im * density * 9.8663479e-9 / energy)

    def Refractive_Index_Re(self, descriptor, energy, density):
        cp = self.compound_parser(descriptor)
        KD = 4.15179082788e-4  # TODO: recalculate with codata....
        rv = 0.0
        for i in range(cp["nElements"]):
            Z = cp["Elements"][i]
            rv += cp["massFractions"][i] * KD * (Z + self.Fi(Z, energy)) / \
                self.AtomicWeight(Z) / energy / energy
        return (1 - rv * density)

    def Refractive_Index_Im(self, descriptor, energy, density):
        cp = self.compound_parser(descriptor)
        rv = 0.0
        for i in range(cp["nElements"]):
            Z = cp["Elements"][i]
            rv += self.CS_Total(Z, energy) * cp["massFractions"][i]
        # /*9.8663479e-9 is calculated as planck's constant * speed of light / 4Pi */
        # return rv * density * 9.8663479e-9 / E;
        return rv * density * 9.8663479e-9 / energy

    #
    # NIST compounds
    #

    def GetCompoundDataNISTList(self):
        file1 = self.get_dabax_file("CompoundsNIST.dat")
        if self.verbose(): print("Accessing file: %s" % file1)
        sf = SpecFile(file1)

        list1 = []
        for index in range(len(sf)):
            list1.append(sf[index].scan_header_dict["Uname"])

        return list1

    def GetCompoundDataNISTByIndex(self, index_found):
        file1 = self.get_dabax_file("CompoundsNIST.dat")
        if self.verbose(): print("Accessing file: %s" % file1)
        sf = SpecFile(file1)

        s1 = sf[index_found]
        data = s1.data

        name = s1.scan_header_dict["Uname"]
        nElements = int(s1.scan_header_dict["UnElements"])
        density = float(s1.scan_header_dict["Udensity"])

        Elements = []
        massFractions = []
        for i in range(nElements):
            Elements.append(int(data[0][i]))
            massFractions.append(data[1][i])

        return {"name": name, 'nElements': nElements, 'density': density, 'Elements': Elements,
                'massFractions': massFractions}

    def GetCompoundDataNISTByName(self, entry_name):
        list1 = self.GetCompoundDataNISTList()
        return self.GetCompoundDataNISTByIndex(list1.index(entry_name))




    #
    #
    #   DONE:
    #
    #
    #  (used in xoppy_xraylib_util):
    #  xraylib.Crystal_GetCrystal(descriptor)
    #  xraylib.Crystal_dSpacing(cryst, hh, kk, ll)
    #  xraylib.Crystal_dSpacing
    #  xraylib.CompoundParser(descriptor)
    #  xraylib.SymbolToAtomicNumber(descriptor)
    #  xraylib.AtomicNumberToSymbol(zi)
    #  xraylib.ElementDensity(Z)
    #  xraylib.AtomicWeight
    #  xraylib.FF_Rayl(xraylib.SymbolToAtomicNumber(descriptor), iqscale)
    #  xraylib.Fi(Z,1e-3*ienergy)
    #  xraylib.Fii(Z,1e-3*ienergy)
    #  xraylib.Crystal_F_H_StructureFactor(_crystal, E_keV, h, k, l, _debyeWaller, 1.0)
    #  xraylib.Crystal_F_H_StructureFactor(_crystal, E_keV, h, k, l, _debyeWaller, 1.0)

    #
    #  (used in power/power3d)
    #
    #  xraylib.CS_Total(Z,1e-3*ienergy)
    #  xraylib.CSb_Total(Z,1e-3*ienergy)
    #  xraylib.CS_Total_CP(Z,1e-3*ienergy)
    #  xraylib.CSb_Total_CP(Z,1e-3*ienergy)
    #  xraylib.Refractive_Index_Re(descriptor, energy_in_keV, density)
    #  xraylib.Refractive_Index_Im(descriptor, energy_in_keV, density)
    #

    #  (used in calc_cross_sec)
    #  xraylib.CS_Phot()
    #  xraylib.CSb_Photo(Z,1e-3*ienergy)
    #  xraylib.CS_Phot_CP()
    #  xraylib.CSb_Photo_CP(descriptor,1e-3*ienergy)
    #  xraylib.CSb_Photo_CP(descriptor,1e-3*ienergy)
    #  xraylib.CS_Rayl(Z,1e-3*ienergy)
    #  xraylib.CSb_Rayl(Z,1e-3*ienergy)
    #  xraylib.CS_Rayl_CP(descriptor,1e-3*ienergy)
    #  xraylib.CSb_Rayl_CP(descriptor,1e-3*ienergy)
    #  xraylib.CS_Compt(Z,1e-3*ienergy)
    #  xraylib.CSb_Compt(Z,1e-3*ienergy)
    #  xraylib.CS_Compt_CP(descriptor,1e-3*ienergy)
    #  xraylib.CSb_Compt_CP(descriptor,1e-3*ienergy)
    #  xraylib.GetCompoundDataNISTList()
    #  xraylib.GetCompoundDataNISTByName(DESCRIPTOR)
    #  xraylib.GetCompoundDataNISTByIndex(DESCRIPTOR)

    #
    #   TODO
    #






    #
    # auxiliar methods
    # there are not in xraylib, but accelerate the calculation
    #
    def CompoundParserCheckingNIST(self, descriptor):
        try:
            out_dict = self.compound_parser(descriptor)

        except:
            try:
                out_dict = self.GetCompoundDataNISTByName(descriptor)
            except:
                raise Exception("Error processing compound descriptor: %s" % descriptor)

        return out_dict

    def FiAndFii(self, Z, energy):
        symbol = self.AtomicNumberToSymbol(Z)
        f1, f2 = self.f1f2_interpolate(symbol, energy*1e3)
        if self.get_file_f1f2() in ['f1f2_Windt.dat','f1f2_Henke.dat','f1f2_EPDL97.dat','f1f2_Chantler.dat','f1f2_asf_Kissel.dat']:
            f1 -= Z
        f2 *= -1.0
        return f1,f2

    def Crystal_F_0_F_H_F_H_bar_StructureFactor(self,
                                    crystal_id,
                                    energy_in_kev,
                                    millerH,
                                    millerK,
                                    millerL,
                                    debyeWaller,
                                    rel_angle=1.0):
        energy = energy_in_kev * 1e3
        wavelength = codata.h * codata.c / codata.e / energy * 1e10
        # print(crystal_id["n_atom"])
        atom = crystal_id['atom']
        natom = len(atom)
        list_fraction = [atom[i]['fraction'] for i in range(natom)]
        list_x = [atom[i]['x'] for i in range(natom)]
        list_y = [atom[i]['y'] for i in range(natom)]
        list_z = [atom[i]['z'] for i in range(natom)]

        F_0 = numpy.zeros(numpy.array(energy).size, dtype=complex)
        F_H = numpy.zeros(numpy.array(energy).size, dtype=complex)
        F_H_bar = numpy.zeros(numpy.array(energy).size, dtype=complex)

        for i in range(natom):
            atom_i = atom[i]
            if (i > 0) and (atom_i['Zatom'] == Z_i) and (atom_i['charge'] == charge_i):
                pass # avoid re-calculating f0 if inputs are identical to previous call
            else:
                Z_i = atom_i['Zatom']
                charge_i = atom_i['charge']
                coeffs = self.f0_with_fractional_charge(Z_i, charge=charge_i)


                if (millerH == 0 and millerK == 0 and millerL == 0):
                    ratio = 0.0
                else:
                    angle = self.Bragg_angle(crystal_id, energy_in_kev,
                                             millerH, millerK, millerL)
                    ratio = numpy.sin(angle * rel_angle) / wavelength

                f0_i_zero = calculate_f0_from_f0coeff(coeffs, 0.0)
                f0_i = calculate_f0_from_f0coeff(coeffs, ratio)
                Fi  = self.Fi(Z_i, energy_in_kev)
                Fii = self.Fii(Z_i, energy_in_kev)

            F_0 += (f0_i_zero + Fi - Fii * 1j) * list_fraction[i] * debyeWaller

            F_H += (f0_i + Fi - Fii * 1j) * list_fraction[i] * debyeWaller * \
                   numpy.exp(2j*numpy.pi*(millerH*list_x[i]+millerK*list_y[i]+millerL*list_z[i]))

            F_H_bar += (f0_i + Fi - Fii * 1j) * list_fraction[i] * debyeWaller * \
                   numpy.exp(2j*numpy.pi*(-millerH*list_x[i]-millerK*list_y[i]-millerL*list_z[i]))

        return F_0, F_H, F_H_bar



