import os

from config import PICKLE_BLM_INTERVALS_DIR, BLM_DATA_DIR
from source.BLM_dose_calculation_exceptions import BLMDataEmpty, BLMIntervalsEmpty, BLMInvalidRawData
from source.Loaders.BLMsRawPandasDataLoader import BLMsRawPandasDataLoader
from source.Loaders.BLMsCalculatedLoader import BLMsCalculatedLoader
import logging
import traceback
import copy

class BLMProcess:
    def __init__(self, start, end, field, calculators, should_return_blm=False, blm_raw_data_dir=BLM_DATA_DIR, pickled_blm_dir=PICKLE_BLM_INTERVALS_DIR):
        self.start = start
        self.end = end
        self.field = field
        self.calculators = calculators
        self.should_return_blm = should_return_blm
        self.blm_raw_data_dir = blm_raw_data_dir
        self.pickled_blm_dir = pickled_blm_dir

    def run(self, blm_scratch):
        blm_name = blm_scratch.name
        logging.info('{}\t start'.format(blm_name))

        try:
            blm_scratch.data = self.load_pickled_raw_blm_data(blm_name)
            calculated_blm_loader = BLMsCalculatedLoader(names=[blm_name], remove_raw_data=True)
            is_any_already_calculated_blm_exists = self.check_if_blm_already_calculated(calculated_blm_loader)

            if is_any_already_calculated_blm_exists:
                loaded_blm_intervals = self.load_calculated_blm(blm_scratch, calculated_blm_loader).blm_intervals
                missing_blm_intervals = blm_scratch.get_missing_blm_intervals(loaded_blm_intervals)
                blm_scratch.blm_intervals = self.get_only_needed_blm_intervals(blm_scratch, loaded_blm_intervals)

                if not missing_blm_intervals:
                    logging.info('{}\t not missing anything'.format(blm_name))
                    return blm_scratch if self.should_return_blm else None
                else:
                    self.set_calculators_for_missing_intervals(blm_scratch, missing_blm_intervals)

            else:
                loaded_blm_intervals = None
                self.set_blm_calculators(blm_scratch)

            self.update_pickled_blm(blm_scratch, loaded_blm_intervals, calculated_blm_loader.file_paths)
            logging.info('{}\t done'.format(blm_name))
            return blm_scratch if self.should_return_blm else None

        except (BLMDataEmpty, BLMIntervalsEmpty) as e:
            e.logging_func('{} {}'.format(blm_name, e))
        except Exception as e:
            logging.critical('{} {} {}'.format(blm_name, traceback.format_exc(), e))
            raise e

    def update_pickled_blm(self, blm_scratch, all_already_calculated_intervals, files_to_be_deleted):
        blm_to_be_saved = blm_scratch
        if all_already_calculated_intervals:
            blm_to_be_saved = copy.deepcopy(blm_scratch)
            blm_to_be_saved.blm_intervals.update(all_already_calculated_intervals)
        file_path = self.save_blm_as_pickle(blm_to_be_saved)
        self.remove_old_pickles(files_to_be_deleted, file_path)

    def get_only_needed_blm_intervals(self, blm_scratch, all_calculated_blm_intervals):
        return blm_scratch.blm_intervals.intersection(all_calculated_blm_intervals)

    def remove_old_pickles(self, files_to_be_deleted, new_pickle_file_path):
        if files_to_be_deleted is not None:
            files_to_be_removed = filter(lambda f_path: f_path != new_pickle_file_path, files_to_be_deleted)
            for file_path in files_to_be_removed:
                os.remove(file_path)
                logging.info('{}\t removed'.format(file_path))

    def save_blm_as_pickle(self, blm):
        blm.clean_blm_intervals_from_temporary_data(clean_blm_data=True)
        blm.name = blm.name + ':' + self.field
        return blm.to_pickle(self.pickled_blm_dir, self.start, self.end)

    def set_calculators_for_missing_intervals(self, blm, missing_intervals):
        logging.info('{}\t missing {} intervals'.format(blm.name, len(missing_intervals)))
        blm_already_calculated_blm_intervals = blm.blm_intervals
        blm.blm_intervals = missing_intervals
        self.set_blm_calculators(blm)
        blm.blm_intervals = self.merge_already_and_new_calculated_blm_intervals(blm.blm_intervals, blm_already_calculated_blm_intervals)

    def merge_already_and_new_calculated_blm_intervals(self, blm_new_calculated_intervals, blm_already_calculated_blms):
        return blm_already_calculated_blms | blm_new_calculated_intervals

    def load_calculated_blm(self, blm, calculated_blm_loader):
        logging.info('{}\t exists'.format(blm.name))
        blm_calculated = calculated_blm_loader.load_pickles()
        return blm_calculated

    def check_if_blm_already_calculated(self, calculated_blms_loader):
        calculated_blms_loader.set_files_paths(self.pickled_blm_dir, self.start, self.end, self.field)
        is_calculated_blms_existing = bool(calculated_blms_loader.file_paths)
        return is_calculated_blms_existing

    def load_pickled_raw_blm_data(self, blm_scratch_name):
        blm_names_list = [blm_scratch_name]
        blm_loader = BLMsRawPandasDataLoader(blm_names_list)
        blm_loader.set_files_paths(self.blm_raw_data_dir, self.start, self.end, self.field)
        blm_loader.load_pickles()
        loaded_blms = list(blm_loader.get_blms())
        if len(loaded_blms) != 1:
            raise BLMInvalidRawData('No or too many files for {}'.format(blm_scratch_name))
        return loaded_blms[0].data

    def set_blm_calculators(self, blm):
        for calc in self.calculators:
            blm.set(calc)
