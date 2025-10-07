"""

dabax: python module for processing remote files containing dabax

"""

import numpy
import os
from urllib.request import urlretrieve, build_opener, HTTPSHandler, install_opener
from silx.io.specfile import SpecFile
import ssl

from dabax.common_tools import calculate_f0_from_f0coeff, f0_interpolate_coefficients
from dabax.common_tools import atomic_symbols, atomic_names, atomic_number
from dabax.common_tools import parse_formula

try:
    # create an "unverified" SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # build and install an opener that uses the unverified context for HTTPS
    install_opener(build_opener(HTTPSHandler(context=context)))
except:
    pass

class DabaxBase(object):
    def __init__(self,
                 dabax_repository=None,
                 verbose=False,
                 file_f0="f0_InterTables.dat",
                 file_f1f2="f1f2_Windt.dat",
                 file_CrossSec = "CrossSec_EPDL97.dat",
                 file_Crystals="Crystals.dat",
                 ):

        self._dabax_repository = dabax_repository
        self._verbose = verbose
        self._file_f0 = file_f0
        self._file_f1f2 = file_f1f2
        self._file_CrossSec = file_CrossSec
        self._file_Crystals = file_Crystals

        if dabax_repository is None:
            self._dabax_repository = self.get_dabax_default_repository()
        else:
            self._dabax_repository = dabax_repository

    def get_dabax_default_repository(self):
        return "https://raw.githubusercontent.com/oasys-kit/DabaxFiles/main/"

    def set_dabax_repository(self, repo):
        self._dabax_repository = repo

    def get_dabax_repository(self):
        return self._dabax_repository

    def set_verbose(self, value=True):
        self._verbose = value

    def verbose(self):
        return self._verbose

    def set_file_f0(self, filename):
        self._file_f0 = filename

    def get_file_f0(self):
        return self._file_f0

    def set_file_f1f2(self, filename):
        self._file_f1f2 = filename

    def get_file_f1f2(self):
        return self._file_f1f2

    def set_file_CrossSec(self, filename):
        self._file_CrossSec = filename

    def get_file_CrossSec(self):
        return self._file_CrossSec

    def set_file_Crystals(self, filename):
        self._file_Crystals = filename

    def get_file_Crystals(self):
        return self._file_Crystals

    def info(self):
        txt = "################  DABAX info ###########\n"
        txt += "dabax repository: %s\n" % self.get_dabax_repository()
        txt += "dabax f0 file: %s\n" % self.get_file_f0()
        txt += "dabax f1f2 file: %s\n" % self.get_file_f1f2()
        txt += "dabax CrossSec file: %s\n" % self.get_file_CrossSec()
        txt += "dabax Crystals file: %s\n" % self.get_file_Crystals()
        txt += "########################################\n"
        return txt


    def is_remote(self):
        if "http" in self.dabax_repository:
            return True
        else:
            return False


    #########################
    # common access tools
    #########################
    def get_dabax_file(self, filename):
        #
        # file exists in current directory
        #
        dabax_repository = self.get_dabax_repository()

        if os.path.exists(filename):
            if self.verbose(): print("Dabax file exists in local directory: %s " % filename)
            return filename
        #
        # download remote file
        #
        if dabax_repository[0:3] == "htt" or dabax_repository[0:3] == "ftp":
            try:
                filepath, http_msg = urlretrieve(dabax_repository + filename,
                                                 filename=filename,
                                                 reporthook=None,
                                                 data=None)

                if self.verbose(): print("Dabax file %s downloaded from %s" % (filepath, dabax_repository + filename))
                return filename
            except:
                try: # in case there are write permissions issues
                    filepath, http_msg = urlretrieve(dabax_repository + filename,
                                                     filename=None, # will create a temp file
                                                     reporthook=None,
                                                     data=None)

                    if self.verbose(): print("Dabax file %s downloaded from %s" % (filepath, dabax_repository + filename))
                    return filepath
                except:
                    raise Exception("Failed to download file %s from %s" % (filename, dabax_repository))
        #
        # file exists in local repository
        #
        f1 = os.path.join(dabax_repository, filename)
        if os.path.exists(f1):
            if self.verbose(): print("Dabax file exists in local directory: %s " % f1)
            return f1

        print("Error trying to access file: %s" % f1)
        raise Exception(FileNotFoundError)


    #########################
    # f0
    #########################

    def get_f0_coeffs_from_dabax_file(self, entry_name="Y3+"):
        filename = self.get_file_f0()
        file1 = self.get_dabax_file(filename)
        if self.verbose(): print("Accessing file: %s" % file1)
        sf = SpecFile(file1)

        flag_found = False

        for index in range(len(sf)):
            s1 = sf[index]
            name = s1.scan_header_dict["S"]

            if name.split('  ')[1] == entry_name:
                flag_found = True
                index_found = index

        if flag_found:
            return (sf[index_found].data)[:, 0]
        else:
            return []


    def f0_with_fractional_charge(self, Z, charge=0.0):
        filename = self.get_file_f0()

        symbol = atomic_symbols()[Z]

        if charge == 0.0:
            return self.get_f0_coeffs_from_dabax_file(entry_name=symbol)
        else:
            # retrieve all entries
            filename = self.get_dabax_file(filename)
            if self.verbose(): print("Accessing file: %s" % filename)
            sf = SpecFile(filename)
            # retrieve all entries
            entries = []
            for index in range(len(sf)):
                s1 = sf[index]
                name = s1.scan_header_dict["S"]
                entries.append(name.split('  ')[1])

            # identify the entries that match the symbol
            interesting_entries = []
            charge_list = []
            index_list = []
            for i, entry in enumerate(entries):
                if entry.find(symbol) == 0:
                    if entry == symbol:
                        interesting_entries.append(entry)
                        charge_list.append(0.0)
                        index_list.append(i)
                    else:
                        entry2 = entry.replace(symbol, '')
                        try:
                            charge_item = int(entry2[::-1])  # convert to integer the reversed string
                            charge_list.append(charge_item)
                            interesting_entries.append(entry)
                            index_list.append(i)
                        except:
                            pass

            # retrieve coefficients from these interesting entries
            coefficient_list = []
            for i in index_list:
                coefficient_list.append((sf[i].data)[:, 0])

            # return self.__f0_interpolate_coefficients(charge, interesting_entries, charge_list, coefficient_list)
            return f0_interpolate_coefficients(charge, charge_list, coefficient_list)

    #
    #
    #

    def _f0_with_fractional_charge_get_entries(self, Z, charge=0.0):
        filename = self.get_file_f0()

        symbol = atomic_symbols()[Z]

        if charge == 0.0:
            return None
        else:
            # retrieve all entries
            filename = self.get_dabax_file(filename)
            if self.verbose(): print("Accessing file: %s" % filename)
            sf = SpecFile(filename)
            # retrieve all entries
            entries = []
            for index in range(len(sf)):
                s1 = sf[index]
                name = s1.scan_header_dict["S"]
                entries.append(name.split('  ')[1])

            # identify the entries that match the symbol
            interesting_entries = []
            charge_list = []
            index_list = []
            for i, entry in enumerate(entries):
                if entry.find(symbol) == 0:
                    if entry == symbol:
                        interesting_entries.append(entry)
                        charge_list.append(0.0)
                        index_list.append(i)
                    else:
                        entry2 = entry.replace(symbol, '')
                        try:
                            charge_item = int(entry2[::-1])  # convert to integer the reversed string
                            charge_list.append(charge_item)
                            interesting_entries.append(entry)
                            index_list.append(i)
                        except:
                            pass

            # retrieve coefficients from these interesting entries
            coefficient_list = []
            for i in index_list:
                coefficient_list.append((sf[i].data)[:, 0])

            # return self.__f0_interpolate_coefficients(charge, interesting_entries, charge_list, coefficient_list)
            return interesting_entries, charge_list, coefficient_list


    ######################
    # f1f2
    ######################

    def f1f2_extract(self, entry_name="Y3+"):
        filename = self.get_file_f1f2()
        file1 = self.get_dabax_file(filename)
        if self.verbose(): print("Accessing file: %s" % filename)
        sf = SpecFile(file1)

        flag_found = False

        for index in range(len(sf)):
            s1 = sf[index]
            name1 = s1.scan_header_dict["S"]
            name = ' '.join(name1.split())
            if name.split(' ')[1] == entry_name:
                flag_found = True
                index_found = index

        if not flag_found:
            if self.verbose():
                print("Entry name %s not found in DABAX file: %s" % (entry_name, filename))
            return None

        # energy
        energy_in_eV = (sf[index_found].data)[0,:].copy()
        if filename == 'f1f2_asf_Kissel.dat' or \
            filename == 'f1f2_Chantler.dat':
            if self.verbose(): print('f1f2_extract: Changing Energy from keV to eV for DABAX file '+filename)
            energy_in_eV *= 1e3

        # f1f2
        if filename == 'f1f2_asf_Kissel.dat':
            f1 = sf[index_found].data[4,:].copy()
            f2 = numpy.abs(sf[index_found].data[1,:].copy())
        else:
            f1 = sf[index_found].data[1,:].copy()
            f2 = sf[index_found].data[2,:].copy()

        return energy_in_eV, f1, f2

    def f1f2_interpolate(self, entry_name, energy,
                         method=2, # 0: lin-lin, 1=lin-log, 2=log-lin, 3:log-log
                         ):

        energy0, f1, f2 = self.f1f2_extract(entry_name)
        if method == 0:
            f1_interpolated = numpy.interp(energy, energy0, f1)
            f2_interpolated = numpy.interp(energy, energy0, f2)
        elif method == 1:
            f1_interpolated = 10 ** numpy.interp((energy),
                                                 (energy0),
                                                 numpy.log10(f1))
            f2_interpolated = 10 ** numpy.interp((energy),
                                                 (energy0),
                                                 numpy.log10(f2))
        elif method == 2:
            f1_interpolated = numpy.interp(numpy.log10(energy),
                                                 numpy.log10(energy0),
                                                 f1)
            f2_interpolated = numpy.interp(numpy.log10(energy),
                                                 numpy.log10(energy0),
                                                 f2)
        elif method == 3:
            f1_interpolated = 10 ** numpy.interp(numpy.log10(energy),
                                                 numpy.log10(energy0),
                                                 numpy.log10(f1))
            f2_interpolated = 10 ** numpy.interp(numpy.log10(energy),
                                                 numpy.log10(energy0),
                                                 numpy.log10(f2))

        return f1_interpolated, f2_interpolated

    ######################
    # crosssec
    ######################

    def crosssec_extract(self, entry_name="Si", partial='TotalCrossSection[barn/atom]'):
        filename = self.get_file_CrossSec()
        file1 = self.get_dabax_file(filename)
        if self.verbose(): print("Accessing file: %s" % filename)
        sf = SpecFile(file1)

        flag_found = False

        for index in range(len(sf)):
            s1 = sf[index]
            name1 = s1.scan_header_dict["S"]
            name = ' '.join(name1.split())
            if name.split(' ')[1] == entry_name:
                flag_found = True
                index_found = index

        if not flag_found:
            if self.verbose():
                print("Entry name %s not found in DABAX file: %s" % (entry_name, filename))
            return None

        data = sf[index_found].data
        labels = sf[index_found].labels

        energy_column_index = -1
        for i in range(len(labels)):
            if 'PhotonEnergy' in labels[i]:
                energy_column_index = i
        if energy_column_index == -1:
            raise Exception("Column with PhotonEnergy not found in scan index %d of %s" % (index_found, file1))

        cs_column_index = -1
        for i in range(len(labels)):
            if partial in labels[i]:
                cs_column_index = i
        if cs_column_index == -1:
            raise Exception("Column with %s not found in scan index %d of %s" % (partial, index_found, file1))

        energy = data[energy_column_index, :].copy()
        cs = data[cs_column_index, :].copy()

        # print("\n>>>>")
        if '[EV]' in labels[energy_column_index].upper():
            pass
        elif '[KEV]' in labels[energy_column_index].upper():
            energy *= 1e3
            # print(">>> energy changed from keV to eV")
        elif '[MEV]' in labels[energy_column_index].upper():
            energy *= 1e6
            # print(">>> energy changed from MeV to eV")

        # print(">>>> %s (col %d)\n     %s (col %d): " % (labels[energy_column_index], energy_column_index, labels[cs_column_index], cs_column_index))

        return energy, cs

    def crosssec_interpolate(self, entry_name, energy,
                         method=2, # 0: lin-lin, 1=lin-log, 2=log-lin, 3:log-log
                         partial='TotalCrossSection[barn/atom]',
                         ):

        out = self.crosssec_extract(entry_name, partial=partial)
        if out is None:
            raise Exception("Descriptor %s not in file %s" % (entry_name, self.get_file_CrossSec()))
        else:
            energy0, cs = out

        if method == 0:
            cs_interpolated = numpy.interp(energy, energy0, cs)
        elif method == 1:
            cs_interpolated = 10 ** numpy.interp((energy),
                                                 (energy0),
                                                 numpy.log10(cs))
        elif method == 2:
            cs_interpolated = numpy.interp(numpy.log10(energy),
                                                 numpy.log10(energy0),
                                                 cs)
        elif method == 3:
            cs_interpolated = 10 ** numpy.interp(numpy.log10(energy),
                                                 numpy.log10(energy0),
                                                 numpy.log10(cs))

        return cs_interpolated

    ######################
    # miscellaneous
    ######################

    def atomic_weights(self, descriptor,
                             filename="AtomicWeights.dat",
                             ):
        """
        ;       Returns atomic weights from DABAX.
        ;
        ; INPUTS:
        ;       id: an identifier string (i.e. 'Si', '70Ge)
        ;
        ;       If descriptor is the symbol (e.g., Ge),
        ;         the averaged atomic mass is returned.
        ;       If descriptor contains the isotope (number of nucleons) (e.g., 70Ge),
        ;         the atomic mass for the isotope is returned.
        ;
        ;       filename = the DABAX  inout file (default AtomicWeights.dat)

        """

        if isinstance(descriptor, str):
            descriptor = [descriptor]
            descriptor_is_string = 1
        else:  # is list
            descriptor_is_string = 0

        # access spec file
        file1 = self.get_dabax_file(filename)
        if self.verbose(): print("Accessing file: %s" % file1)
        sf = SpecFile(file1)

        out = []

        for idescriptor in descriptor:
            flag_found = False
            index_found = []
            for index in range(len(sf)):
                s1 = sf[index]
                name = s1.scan_header_dict["S"]
                line = " ".join(name.split())
                scan_name = line.split(' ')[1]
                if scan_name[-len(idescriptor):] == idescriptor:
                    flag_found = True
                    index_found.append(index)

            if not flag_found:
                raise (Exception("Entry name not found: %s" % idescriptor))

            data = sf[index_found[0]].data

            if idescriptor[0].isdigit():
                out.append(data[0, 0])
            else:
                out.append(data[2, 0])

        if descriptor_is_string:
            return out[0]
        else:
            return out


    def atomic_constants(self, descriptor,
                         filename="AtomicConstants.dat",
                         return_item=0,
                         return_label=None,
                         ):
        """
        ;	Returns atomic constants from DABAX.
        ;
        ; CALLING SEQUENCE:
        ;	out = atomic_constants(id,file,return=return)
        ; INPUTS:
        ;	id: an identifier (or an array of identifiers) to be found in the
        ;	scan title (i.e. 'Si')
        ;
        ; KEYWORDS:
        ;	File = the DABAX  inout file (default: AtomicConstants.dat)
        ;	return_label and return_item  define the variable to be returned.
        ;   If return_name is not None, it has priority over retirn_index
        ;		number of the column in the DABAX file, or a text
        ;		identifier (case insensitive) listed below:
        ;		return_label='AtomicRadius'	             or return_item=0
        ;		return_label='CovalentRadius'	         or return_item=1
        ;		return_label='AtomicMass'	             or return_item=2
        ;		return_label='BoilingPoint'	             or return_item=3
        ;		return_label='MeltingPoint'	             or return_item=4
        ;		return_label='Density'	                 or return_item=5
        ;		return_label='AtomicVolume'	             or return_item=6
        ;		return_label='CoherentScatteringLength'	 or return_item=7
        ;		return_label='IncoherentX-section'	     or return_item=8
        ;		return_label='Absorption@1.8A'	         or return_item=9
        ;		return_label='DebyeTemperature'          or return_item=10
        ;		return_label='ThermalConductivity'       or return_item=11
        ;
        ; OUTPUT:
        ;	out: the value of the selected parameter
        ;
        ; EXAMPLES:
        ;	print(atomic_constants('Si',return='AtomicMass'))
        ;	    28.085500
        ;	print(atomic_constants(14,return='AtomicMass'))
        ;           28.085500
        ;	print(atomic_constants([14,27],return='AtomicMass'))
        ;	    28.085500       58.933200
        ;
        ;-

        """

        if isinstance(descriptor, str):
            descriptor = [descriptor]
            descriptor_is_string = 1
        else:  # is list
            descriptor_is_string = 0

        return_index = -1
        if return_label is None:
            return_index = return_item
        else:
            if return_label == 'AtomicRadius'	: return_index = 0
            if return_label == 'CovalentRadius'	            : return_index = 1
            if return_label == 'AtomicMass'	                : return_index = 2
            if return_label == 'BoilingPoint'	            : return_index = 3
            if return_label == 'MeltingPoint'	            : return_index = 4
            if return_label == 'Density'	                : return_index = 5
            if return_label == 'AtomicVolume'	            : return_index = 6
            if return_label == 'CoherentScatteringLength'	: return_index = 7
            if return_label == 'IncoherentX-section'	    : return_index = 8
            if return_label == 'Absorption@1.8A'	        : return_index = 9
            if return_label == 'DebyeTemperature'           : return_index = 10
            if return_label == 'ThermalConductivity'        : return_index = 11


        if return_index == -1: raise Exception("Bad item index")
        # access spec file

        file1 = self.get_dabax_file(filename)
        if self.verbose(): print("Accessing file: %s" % file1)
        sf = SpecFile(file1)

        out = []

        for idescriptor in descriptor:

            for index in range(len(sf)):
                flag_found = False
                s1 = sf[index]
                name = s1.scan_header_dict["S"]
                scan_name = name.split('  ')[1]
                if scan_name == idescriptor:
                    flag_found = True
                    index_found = index
                    break

            if flag_found:
                out.append((sf[index_found].data)[return_index, 0])
            else:
                raise Exception("Data not found for %s " % idescriptor)

        if descriptor_is_string:
            return out[0]
        else:
            return out


    def element_density(self, descriptor,
                        filename="AtomicConstants.dat"):

        return self.atomic_constants(descriptor, filename=filename, return_label="Density")


    def compound_parser(self, descriptor):

        zetas, fatomic = parse_formula(formula=descriptor, verbose=self.verbose())

        elements = []
        atomic_weight = []
        massFractions = []

        for i ,z in enumerate(zetas):
            symbol = atomic_symbols()[z]
            atw = self.atomic_weights(symbol)
            elements.append(z)
            atomic_weight.append(atw)
            massFractions.append(fatomic[i ] *atw)

        mweight = 0.0
        for i in range(len(fatomic)):
            mweight += atomic_weight[i] * fatomic[i]

        for i in range(len(massFractions)):
            massFractions[i] /= mweight

        new_dict = {
            "nElements": len(elements),
            "nAtomsAll": float(numpy.array(fatomic).sum()),
            "Elements" :zetas,
            "massFractions": massFractions,
            "nAtoms" :fatomic,
            "molarMass": mweight,
        }

        return new_dict

if __name__ == '__main__':
    dx = DabaxBase(dabax_repository="https://gitlab.esrf.fr/srio/dabaxfiles/-/raw/main/")
    print(dx.info())
    #
    # f0
    #
    if False:
        #
        # test f0 data for B3+
        #
        q = numpy.array([0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9])
        f0_B3plus = numpy.array([2,1.995,1.979,1.954,1.919,1.875,1.824,1.766,1.703,1.566,1.42,1.274,1.132,0.999,0.877,0.767,0.669,0.582,0.507,0.441,0.384,0.335,0.293,0.256])

        #
        # plot
        #
        from srxraylib.plot.gol import plot

        plot(q, f0_B3plus,
             q, calculate_f0_from_f0coeff(dx.f0_with_fractional_charge(5, 3.0), q),
             q, calculate_f0_from_f0coeff(dx.f0_with_fractional_charge(5, 2.8), q),
             xtitle=r"q (sin $\theta$ / $\lambda$)", ytitle="f0 [electron units]",
             legend=["B3plus original",
                     "B3plus from f0_with_fractional_charge(5,+3)",
                     "B3plus from f0_with_fractional_charge(5,+2.8)"],
             marker=['+', None, None],
             title="")

    #
    # f0 another test
    #
    if False:
        #
        # test f0 data for B3+
        #
        q = numpy.array(
            [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6,
             1.7, 1.8, 1.9])
        f0_B3plus = numpy.array(
            [2, 1.995, 1.979, 1.954, 1.919, 1.875, 1.824, 1.766, 1.703, 1.566, 1.42, 1.274, 1.132, 0.999, 0.877, 0.767,
             0.669, 0.582, 0.507, 0.441, 0.384, 0.335, 0.293, 0.256])

        #
        # plot
        #
        from srxraylib.plot.gol import plot

        plot(q, f0_B3plus,
             q, calculate_f0_from_f0coeff(dx.f0_with_fractional_charge(5, 3.0), q),
             q, calculate_f0_from_f0coeff(dx.f0_with_fractional_charge(5, 2.8), q),
             xtitle=r"q (sin $\theta$ / $\lambda$)", ytitle="f0 [electron units]",
             legend=["B3plus original",
                     "B3plus from f0_with_fractional_charge(5,+3)",
                     "B3plus from f0_with_fractional_charge(5,+2.8)"],
             marker=['+',None,None],
             title="", show=1)


    if False:
        #
        # misc
        #
        print("Ge, Si: ", dx.atomic_weights(["Ge","Si"]))
        print("70Ge: ", dx.atomic_weights("70Ge"))

        print(atomic_symbols()[14], atomic_names()[14])

        print("Si atomic mass", dx.atomic_constants("Si", return_item=2))
        print("Si,Ge atomic mass", dx.atomic_constants(["Si", "Ge"], return_item=2))
        print("Si,Co atomic mass", dx.atomic_constants(["Si", "Co"], return_label='AtomicMass'))

        print("Z=27", atomic_symbols()[27])
        print("Ge Z=%d" % atomic_number("Ge"))

        print("Density Si: ", dx.element_density("Si"))

    if False:
        energy, f1, f2 = dx.f1f2_extract("Si")

        energy_i = numpy.linspace(10,15000,200)
        f1_i, f2_i = dx.f1f2_interpolate("Si", energy=energy_i)
        print(">>>>", energy.shape, f1.shape, f2.shape)
        from srxraylib.plot.gol import plot
        plot(energy, f1,
             energy, f2,
             energy_i, f1_i,
             energy_i, f2_i,
             xlog=True, ylog=True, title="f1f2 Si",
             legend=['f1','f2','f1_i','f2_i'],
             marker=[None,None,'+','+'],
             linestyle=[None,None,'',''])


    if False: # used to create f0_xop_with_fractional_charge_data() in common_tools
        filename = dx.get_file_f0()
        file1 = dx.get_dabax_file(filename)
        if self.verbose(): print("Accessing file: %s" % filename)
        sf = SpecFile(file1)
        for Z in range(1,99):
            interesting_entries, charge_list, coefficient_list = dx._f0_with_fractional_charge_get_entries(Z, charge=1)

            for i,iel in enumerate(coefficient_list):
                coefficient_list[i] = iel.tolist()

            print("    a.append({'Z':",Z,",'charge_list':",charge_list,",'coefficient_list':",coefficient_list,"})" )

    if False:
        from common_tools import f0_xop_with_fractional_charge
        print("f0 coeffs for Z=14 charge=1.5 DABAX/common_tools: ",
              dx.f0_with_fractional_charge(14, charge=1.5),
              f0_xop_with_fractional_charge(14, charge=1.5),)


    if True:
        energy, cs = dx.crosssec_extract("Si")

        energy_i = numpy.linspace(10,15000,200)
        cs_i = dx.crosssec_interpolate("Si", energy=energy_i)
        print(">>>>", energy.shape, cs.shape)
        from srxraylib.plot.gol import plot
        plot(energy, cs,
             energy_i, cs_i,
             xlog=True, ylog=True, title="crosssec Si",
             legend=['cs','cs_i'],
             marker=[None,'+'],
             linestyle=[None,''])


        print(">>>> cs of Si at 10 kev %g barn/atom ", dx.crosssec_interpolate("Si", energy=50000.0))