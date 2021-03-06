# This script creates datasets as #
# .npy tensors out of raw .txt    #
# data made of CERN .root files   #
# FINAL PARSER                    #
###################################



import numpy as np
import os


def eventSepFinder():
    """Search for event separator."""
    srch_str = "*"
    event_separators = np.array([])
    for ef_st_iter, ef_st in enumerate(ef_strings):
        if srch_str in ef_st:
            event_separators = np.append(
                event_separators, int(ef_st_iter))
    #event_separators = np.append(event_separators, last_string_index)  # cuz no * in the end
    return event_separators


def lafDatSepFinder():
    """Search for label-feature separator."""
    srch_str = "module 1\t"
    lafdat_separators = np.array([])
    ef_st_iter = 0
    for ef_st in ef_strings:
        if srch_str in ef_st:
            lafdat_separators = np.append(
                lafdat_separators, int(ef_st_iter))
        ef_st_iter = ef_st_iter + 1
    return lafdat_separators


def remapCenPer(ev_mat, in_depth):
    """Separate the central modules from the peripheral ones."""
    cen_tensor = np.zeros((4, 4, in_depth), dtype=np.float32)
    per_tensor = np.zeros_like(cen_tensor)
    for i in range(4):
        for j in range(4):
            cen_tensor[i, j] = ev_mat[4*i + j]
    per_tensor[0, 1] = ev_mat[17]
    per_tensor[0, 2] = ev_mat[18]
    per_tensor[1, 0] = ev_mat[27]
    per_tensor[2, 0] = ev_mat[26]
    per_tensor[1, 3] = ev_mat[20]
    per_tensor[2, 3] = ev_mat[21]
    per_tensor[3, 1] = ev_mat[24]
    per_tensor[3, 2] = ev_mat[23]
    return cen_tensor, per_tensor


class Event:
    """Class Of a Single Event."""
    def __init__(self, in_psd_depth, label_start, mul_str, data_start, data_end):
        self._l_start = label_start
        self._m_str = mul_str
        self._d_start = data_start
        self._d_end = data_end
        self._p_depth = in_psd_depth

    def getPdata(self):
        srch_start = self._l_start + 1
        srch_end = self._d_start - 2
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        pdata = []
        for ev_p_string in srch_area_of_strings:
            particle_id = ev_p_string.split('	')[3]
            particle_id = particle_id[0:len(particle_id)]
            particle_id = int(particle_id)
            particle_energy = ev_p_string.split('	')[1]
            particle_energy = float(particle_energy)
            particle_stopv = ev_p_string.split('	')[4]
            particle_stopv = float(particle_stopv[0:len(particle_stopv)-1])
            pdata.append({particle_id : [particle_energy, particle_id, particle_stopv]})
        return pdata

    def getStopVs(self, e_thrsh):
        srch_start = self._l_start + 1
        srch_end = self._d_start - 2
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        stopvs = []
        for ev_p_string in srch_area_of_strings:
            particle_id = ev_p_string.split('	')[3]
            particle_id = particle_id[0:len(particle_id)]
            particle_id = int(particle_id)
            particle_energy = ev_p_string.split('	')[1]
            particle_energy = float(particle_energy)
            particle_stopv = ev_p_string.split('	')[4]
            particle_stopv = float(particle_stopv[0:len(particle_stopv)-1])
            if (particle_energy > e_thrsh) and (dict_of_particles.get(particle_id)):
                stopvs.append(particle_stopv)
        return stopvs

    def getPartNrgs(self, e_thrsh):
        srch_start = self._l_start + 1
        srch_end = self._d_start - 2
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        nrgs = []
        for ev_p_string in srch_area_of_strings:
            particle_id = ev_p_string.split('	')[3]
            particle_id = particle_id[0:len(particle_id)]
            particle_id = int(particle_id)
            particle_energy = ev_p_string.split('	')[1]
            particle_energy = float(particle_energy)
            particle_stopv = ev_p_string.split('	')[4]
            particle_stopv = float(particle_stopv[0:len(particle_stopv)-1])
            if (particle_energy > e_thrsh) and (dict_of_particles.get(particle_id)):
                nrgs.append(particle_energy)
        return nrgs 

    def getSpectNrgs(self, e_thrsh):
        srch_start = self._l_start + 1
        srch_end = self._d_start - 2
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        spect_nrg = 0
        for ev_p_string in srch_area_of_strings:
            particle_id = ev_p_string.split('	')[3]
            particle_id = particle_id[0:len(particle_id)]
            particle_id = int(particle_id)
            particle_energy = ev_p_string.split('	')[1]
            particle_energy = float(particle_energy)
            particle_stopv = ev_p_string.split('	')[4]
            particle_stopv = float(particle_stopv[0:len(particle_stopv)-1])
            if (particle_energy > e_thrsh) and (dict_of_particles.get(particle_id)):
                spect_nrg += particle_energy
        return spect_nrg 

    def findSpecLabel(self, bound, e_thrsh):
        srch_start = self._l_start + 1
        srch_end = self._d_start - 2
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        spect_number = 0
        for ev_p_string in srch_area_of_strings:
            particle_id = ev_p_string.split('	')[3]
            particle_id = particle_id[0:len(particle_id)]
            particle_id = int(particle_id)
            particle_energy = ev_p_string.split('	')[1]
            particle_energy = float(particle_energy)
            particle_stopv = ev_p_string.split('	')[4]
            particle_stopv = float(particle_stopv[0:len(particle_stopv)-1])
            #if particle_stopv == 100500.0:                                 # BE CAREFUL
            if (particle_energy > e_thrsh) and (dict_of_particles.get(particle_id)):
                spect_number = spect_number + dict_of_particles.get(particle_id)
        if spect_number <= bound:
            event_class = 0
        else:
            event_class = 1
        return event_class

    def getSpec(self, e_thrsh):
        srch_start = self._l_start + 1
        srch_end = self._d_start - 2
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        spect_number = 0
        for ev_p_string in srch_area_of_strings:
            particle_id = ev_p_string.split('	')[3]
            particle_id = particle_id[0:len(particle_id)]
            particle_id = int(particle_id)
            particle_energy = ev_p_string.split('	')[1]
            particle_energy = float(particle_energy)
            particle_stopv = ev_p_string.split('	')[4]
            particle_stopv = float(particle_stopv[0:len(particle_stopv)-1])
            #if particle_stopv == 100500.0:
            if (particle_energy > e_thrsh) and (dict_of_particles.get(particle_id)):
                spect_number = spect_number + dict_of_particles.get(particle_id)
        return spect_number

    def findNrgLabel(self, bound):
        srch_start = self._l_start + 1
        srch_end = self._d_start - 2
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        nrg = 0
        for ev_p_string in srch_area_of_strings:
            particle_energy = ev_p_string.split('	')[1]
            nrg += float(particle_energy)
        if nrg <= bound:   # 777.5 at 23.9% centrality on the 1st MC (SHIELD); 759.4 at 24.9% centrality on the 2nd MC (EPOS)
            event_class = 0
        else:
            event_class = 1
        return event_class

    def getNrg(self):
        srch_start = self._l_start + 1
        srch_end = self._d_start - 2
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        nrg = 0
        for ev_p_string in srch_area_of_strings:
            particle_energy = ev_p_string.split('	')[1]
            nrg += float(particle_energy)
        return nrg 

    def findMul(self):
        string_num = self._m_str
        srch_srt = ef_strings[string_num]
        mul_n = srch_srt.split(' ')[-1]
        mul_n = int(mul_n)
        return mul_n

    def findDataTensor(self):
        srch_start = self._d_start
        srch_end = self._d_end
        depth = self._p_depth
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        event_mat = np.zeros((44, depth), dtype=np.float32)

        dps_iter = 0
        for data_p_string in srch_area_of_strings:
            mat_string = data_p_string.split()
            del mat_string[0:2]
            mat_string = [float(ms_iter) for ms_iter in mat_string]
            event_mat[dps_iter] = np.asarray(mat_string)
            dps_iter = dps_iter + 1

        event_tens = remapCenPer(event_mat, depth)   # choose wisely
        return event_tens

    def findDataMat(self):
        srch_start = self._d_start
        srch_end = self._d_end
        depth = self._p_depth
        srch_area_of_strings = ef_strings[srch_start:srch_end]
        event_mat = np.zeros((44, depth), dtype=np.float32)

        dps_iter = 0
        for data_p_string in srch_area_of_strings:
            mat_string = data_p_string.split()
            del mat_string[0:2]
            mat_string = [float(ms_iter) for ms_iter in mat_string]
            event_mat[dps_iter] = np.asarray(mat_string)
            dps_iter = dps_iter + 1

        return event_mat



"""!!!HERE WE GO!!!"""

if __name__ == '__main__':

    dict_of_particles = {2212:1, 2112:1,
                     1000010020:2, 1000010030:3, 
                     1000020030:3, 1000020040:4, 1000020060:6, 
                     1000030060:6, 1000030070:7, 1000030080:8, 
                     1000040070:7}

    #events_file_path = './txtData/2018_10_15_MLPSDHandler_LiBe_150_ready.txt' # old dataset
    #events_file_path = './txtData/2018_11_27_MLPSDHandler_LiBe_150_ready.txt'
    #events_file_path = '../../DATASETS/txtData/EPOS/BeBe150EPOS_SimPSD_3.txt'
    events_file_path = '../../DATASETS/txtData/EPOS/20200915_400kevents.txt'
    #events_file_path = './txtData/t3e.txt'

    events_file = open(events_file_path, "r")
    ef_strings = events_file.readlines()
    events_file.close()
    last_string_index = len(ef_strings)

    psd_depth = 10
    dat_dim = 8
    e_thrsh = 120

    ev_sep_arr = eventSepFinder().astype(int)
    ld_sep_arr = lafDatSepFinder().astype(int)
    mul_sep_arr = lafDatSepFinder().astype(int) - 1

    n_of_events = len(ld_sep_arr)
    n_of_events = 100 * (n_of_events // 100)
    print(n_of_events)

    noe_range = list(range(n_of_events))

    cen_ft = np.zeros((n_of_events, dat_dim//2, dat_dim//2, psd_depth, 1), dtype=np.float32)
    per_ft = np.zeros((n_of_events, dat_dim//2, dat_dim//2, psd_depth, 1), dtype=np.float32)
    sum_ft = np.zeros((n_of_events, 1, 1), dtype=np.float32)
    lab_spec = np.zeros((n_of_events, 2), dtype=np.float32)
    lab_nrg = np.zeros((n_of_events, 2), dtype=np.float32)
    all_mul = np.zeros((n_of_events), dtype=np.int32)
    ev_mat = np.zeros((n_of_events, 44, psd_depth), dtype=np.float32)

    nrgz = np.zeros((n_of_events))
    specz = np.zeros((n_of_events))

    ## FOR TEST 2
    #stopvs_all = np.array([])

    ## FOR TEST 3
    #part_nrgs_all = np.array([])

    print('Fill nrgz, specz')
    for i in range(n_of_events):
        if i % 1000 == 0:
            print('Event: %i' % i)
        ev_sep = ev_sep_arr[i]
        mul_sep = mul_sep_arr[i]
        lf_sep = ld_sep_arr[i]
        lf_end = ev_sep_arr[i+1]
        single_event = Event(psd_depth, ev_sep, mul_sep, lf_sep, lf_end)
        
        nrgz[i] = single_event.getNrg()
        specz[i] = single_event.getSpec(e_thrsh)
        
        ## FOR TEST
        #if i == 1174:
        #    if spec == 0:
        #        pids = single_event.getPdata()
        #        cen, per = single_event.findDataTensor()
        #        emeas = np.sum(cen) + np.sum(per)
        #        print(pids)
        #        print('E_meas {}'.format(emeas))
        #        print('E_forward {}'.format(nrg))

        ## FOR TEST 2
        #stopvs_all = np.concatenate((stopvs_all, single_event.getStopVs(e_thrsh)))

        ## FOR TEST 3
        #part_nrgs_all = np.concatenate((part_nrgs_all, single_event.getPartNrgs(e_thrsh)))

    spec_bound = 3
    bound_perc = np.size(specz[specz <= spec_bound]) / np.size(specz)
    nrgz_sorted = np.sort(nrgz)
    nrg_bound = nrgz_sorted[int(n_of_events * bound_perc)]

    print('Find other data')
    for i in range(n_of_events):
        if i % 1000 == 0:
            print('Event: %i' % i)
        ev_sep = ev_sep_arr[i]
        mul_sep = mul_sep_arr[i]
        lf_sep = ld_sep_arr[i]
        lf_end = ev_sep_arr[i+1]
        single_event = Event(psd_depth, ev_sep, mul_sep, lf_sep, lf_end)
        all_mul[i] = single_event.findMul()
        lab_spec[i, single_event.findSpecLabel(spec_bound, e_thrsh)] = 1
        lab_nrg[i, single_event.findNrgLabel(nrg_bound)] = 1
        cen_ft[i, :, :, :, 0], per_ft[i, :, :, :, 0] = single_event.findDataTensor()
        v_mat = single_event.findDataMat()

    sum_ft = (np.sum(cen_ft, (1, 2, 3, 4)).flatten() + np.sum(per_ft, (1, 2, 3, 4)).flatten()).reshape((-1, 1))

    dataset_name = 'EPOS_400k'
    dataset_dir = '../../DATASETS/NA61_{}/'.format(dataset_name)
    os.makedirs(dataset_dir, exist_ok=True)
    np.save(dataset_dir + 'features_central.npy', cen_ft)
    np.save(dataset_dir + 'features_peripheral.npy', per_ft)
    np.save(dataset_dir + 'features_sum.npy', sum_ft)
    np.save(dataset_dir + 'labels_nrg.npy', lab_nrg)
    np.save(dataset_dir + 'labels_spec.npy', lab_spec)
    np.save(dataset_dir + 'mul.npy', all_mul)
    np.save(dataset_dir + 'nrg24.npy', nrgz)
    np.save(dataset_dir + 'spec24.npy', specz)
    np.save(dataset_dir + 'ev_mat.npy', ev_mat)

    ## FOR TEST 2
    #np.save(dataset_dir + 'stopvs.npy', stopvs_all)

    ## FOR TEST 3
    #np.save(dataset_dir + 'part_nrgs_all.npy', part_nrgs_all)

