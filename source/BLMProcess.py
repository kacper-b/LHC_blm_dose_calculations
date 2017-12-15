import os

from config import PICKLE_BLM_INTERVALS_DIR, BLM_DATA_DIR
from source.BLM_dose_calculation_exceptions import BLMDataEmpty, BLMIntervalsEmpty, BLMInvalidRawData
from source.Loaders.BLMsRawPandasDataLoader import BLMsRawPandasDataLoader
from source.Loaders.BLMsCalculatedLoader import BLMsCalculatedLoader
import logging
import traceback
import copy

class BLMProcess:
    """
    This class encapsulates whole data processing for a one BLM. It reads the data, then conducts calculations (if needed) and saves a analysed BLM class
    object to a pickle file.
    """
    def __init__(self, start, end, field, calculators, should_return_blm=False, blm_raw_data_dir=BLM_DATA_DIR, pickled_blm_dir=PICKLE_BLM_INTERVALS_DIR):
        """
        :param datetime start: end of analysed period
        :param datetime end: beginning of analysed period
        :param str field: ex. LOSS_RS12
        :param list calculators: calculators, which set appropriate fields in a BLM class object
        :param bool should_return_blm: if set to True, after calculation and saving to a pickle file a BLM will be returned (for example to make plots)
        :param str blm_raw_data_dir: a path to the directory with a stored raw BLM data
        :param str pickled_blm_dir: a path to the directory with already calculated BLM pickles
        """
        self.start = start
        self.end = end
        self.field = field
        self.calculators = calculators
        self.should_return_blm = should_return_blm
        self.blm_raw_data_dir = blm_raw_data_dir
        self.pickled_blm_dir = pickled_blm_dir

    def run(self, blm_scratch):
        """
        This method is the main method for that class. It takes a raw BLM's class object (which contains name,position, not integrated blm_intervals and subintervals),
        then it checks if the BLM has already been calculated (pickle file exists). If yes, it reads the pickled BLM and compares BLM's intervals. Then calculations
        are performed only for missing BLM's intervals. If any calculations are performed, the updated pickle file will be saved.
        :param BLM blm_scratch: BLM object without assigned data and calculated partial doses for subintervals
        :return:
        """
        blm_name = blm_scratch.name
        logging.info('{}\t start'.format(blm_name))

        try:
            # Load pickled BLM raw data
            blm_scratch.data = self.load_pickled_raw_blm_data(blm_name)
            blm_scratch.interpolate_data()
            # Load the pickled BLM if it exists
            calculated_blm_loader = BLMsCalculatedLoader(names=[blm_name], remove_raw_data=True)
            is_any_already_calculated_blm_exists = self.check_if_blm_already_calculated(calculated_blm_loader)

            if is_any_already_calculated_blm_exists:
                loaded_blm_intervals = self.load_calculated_blm(blm_scratch, calculated_blm_loader).blm_intervals
                missing_blm_intervals = blm_scratch.get_missing_blm_intervals(loaded_blm_intervals)
                blm_scratch.blm_intervals = self.get_only_needed_blm_intervals(blm_scratch, loaded_blm_intervals)

                if not missing_blm_intervals:
                    logging.info('{}\t not missing anything'.format(blm_name))
                    # return blm_scratch.get_beam_mode_doses_as_dataframe()
                    return blm_scratch if self.should_return_blm else None
                else:
                    self.set_calculators_for_missing_intervals(blm_scratch, missing_blm_intervals)

            else:
                loaded_blm_intervals = None
                self.set_blm_calculators(blm_scratch)

            self.update_pickled_blm(blm_scratch, loaded_blm_intervals, calculated_blm_loader.file_paths)
            logging.info('{}\t done'.format(blm_name))
            # x= blm_scratch.get_beam_mode_doses_as_dataframe()
            # return x
            return blm_scratch if self.should_return_blm else None

        except (BLMDataEmpty, BLMIntervalsEmpty) as e:
            e.logging_func('{} {}'.format(blm_name, e))
        except Exception as e:
            logging.critical('{} {} {}'.format(blm_name, traceback.format_exc(), e))
            raise e

    def update_pickled_blm(self, blm_scratch, all_already_calculated_intervals, files_to_be_deleted):
        """
        It saves BLM's pickle updated version and removes the old pickle file.
        :param BLM blm_scratch: A BLM with intervals that has been calculated during current program execution.
        :param SortedSet all_already_calculated_intervals: collection of BLM intervals which have been already calculated
        :param list files_to_be_deleted: list of files paths
        :return:
        """
        blm_to_be_saved = blm_scratch
        if all_already_calculated_intervals:
            blm_to_be_saved = copy.deepcopy(blm_scratch)
            blm_to_be_saved.blm_intervals.update(all_already_calculated_intervals)
        file_path = self.save_blm_as_pickle(blm_to_be_saved)
        # self.remove_old_pickles(files_to_be_deleted, file_path)

    def get_only_needed_blm_intervals(self, blm_scratch, all_calculated_blm_intervals):
        """
        It returns only those blm intervals, that haven't been calculated yet.
        :param BLM blm_scratch: BLM with non calculated intervals
        :param SortedSet all_calculated_blm_intervals: list of already calculated BLM intervals
        :return:
        """
        return blm_scratch.blm_intervals.intersection(all_calculated_blm_intervals)

    def remove_old_pickles(self, files_to_be_deleted, new_pickle_file_path):
        """
        It deletes all files from the files_to_be_deleted list. If new_pickle_file_path appears in files_to_be_deleted it won't be deleted.
        :param list files_to_be_deleted: files with those paths will be removed.
        :param str new_pickle_file_path: file with that path won't be deleted
        :return:
        """
        if files_to_be_deleted is not None:
            files_to_be_removed = filter(lambda f_path: f_path != new_pickle_file_path, files_to_be_deleted)
            for file_path in files_to_be_removed:
                os.remove(file_path)
                logging.info('{}\t removed'.format(file_path))

    def save_blm_as_pickle(self, blm):
        """
        It saves the BLM to a pickle file.
        :param BLM blm: a calculated BLM class object
        :return:
        """
        blm.clean_blm_intervals_from_temporary_data(clean_blm_data=True)
        blm.name = blm.name + ':' + self.field
        return blm.to_pickle(self.pickled_blm_dir, self.start, self.end)

    def set_calculators_for_missing_intervals(self, blm_scratch, missing_intervals):
        """
        It sets calculators (offset estimation, integration etc.) only to missing BLM intervals.
        :param BLM blm_scratch: BLM
        :param SortedSet missing_intervals: BLM intervals, that haven't been already calculated (integrated dose + offsets are not calculated)
        :return:
        """
        logging.info('{}\t missing {} intervals'.format(blm_scratch.name, len(missing_intervals)))
        blm_already_calculated_blm_intervals = blm_scratch.blm_intervals
        blm_scratch.blm_intervals = missing_intervals
        self.set_blm_calculators(blm_scratch)
        blm_scratch.blm_intervals = self.merge_already_and_new_calculated_blm_intervals(blm_scratch.blm_intervals, blm_already_calculated_blm_intervals)

    def merge_already_and_new_calculated_blm_intervals(self, blm_new_calculated_intervals, blm_already_calculated_blms):
        """
        It merges BLM intervals SortedSets, which are passed as arguments.
        :param SortedSet blm_new_calculated_intervals:
        :param SortedSet blm_already_calculated_blms:
        :return SortedSet: merged BLM intervals
        """
        return blm_already_calculated_blms | blm_new_calculated_intervals

    def load_calculated_blm(self, blm, calculated_blm_loader):
        """
        It
        :param BLM blm:
        :param BLMsCalculatedLoader calculated_blm_loader:
        :return :
        """
        logging.info('{}\t exists'.format(blm.name))
        blm_calculated = calculated_blm_loader.load_pickles()
        return blm_calculated

    def check_if_blm_already_calculated(self, calculated_blms_loader):
        """
        It checks if any pickle file with a calculated BLM intervals already exists.
        :param BLMsCalculatedLoader calculated_blms_loader:
        :return bool:
        """
        calculated_blms_loader.set_files_paths(self.pickled_blm_dir, self.start, self.end, self.field)
        is_calculated_blms_existing = bool(calculated_blms_loader.file_paths)
        return is_calculated_blms_existing

    def load_pickled_raw_blm_data(self, blm_scratch_name):
        """
        It loads a raw (timestamp + dose readouts) data from pickle files.
        :param blm_scratch_name: the BLM name
        :return pandas.DataFrame: loaded data
        """
        blm_names_list = [blm_scratch_name]
        blm_loader = BLMsRawPandasDataLoader(blm_names_list)
        blm_loader.set_files_paths(self.blm_raw_data_dir, self.start, self.end, self.field)
        blm_loader.load_pickles()
        loaded_blms = list(blm_loader.get_blms())
        if len(loaded_blms) != 1:
            raise BLMInvalidRawData('No or too many files for {}'.format(blm_scratch_name))
        return loaded_blms[0].data

    def set_blm_calculators(self, blm):
        """
        It sets calculators to the BLM.
        :param BLM blm: a BLM class object which needs to be calculated.
        :return:
        """
        for calc in self.calculators:
            blm.set(calc)
