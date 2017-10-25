import os

from config import PICKLE_BLM_INTERVALS_DIR, BLM_DATA_DIR
from source.BLM_dose_calculation_exceptions import BLMDataEmpty, BLMIntervalsEmpty, BLMNoRawData
from source.Loaders.BLMsRawPandasDataLoader import BLMsRawPandasDataLoader
from source.Loaders.BLMsCalculatedLoader import BLMsCalculatedLoader
import logging
import traceback


class BLMProcess:
    def __init__(self, start, end, field, calculators, should_return_blm=False):
        self.start = start
        self.end = end
        self.field = field
        self.calculators = calculators
        self.should_return_blm = should_return_blm

    def run(self, blm):
        logging.info('{}\t start'.format(blm.name))

        try:
            self.load_pickled_raw_blm_data(blm)
            calculated_blm_loader = BLMsCalculatedLoader(names=[blm.name], remove_raw_data=True)
            is_calculated_blm_existing = self.check_if_blm_already_calculated(calculated_blm_loader)
            if is_calculated_blm_existing:
                blm_calculated = self.load_calculated_blm(blm, calculated_blm_loader)
                missing_blm_intervals = blm.get_missing_blm_intervals(blm_calculated.blm_intervals)
                if not missing_blm_intervals:
                    logging.info('{}\t not missing anything'.format(blm.name))
                    return blm_calculated if self.should_return_blm else None
                else:
                    self.set_calculators_for_missing_intervals(blm, missing_blm_intervals)
            else:
                self.set_blm_calculators(blm)

            file_path = self.save_blm_as_pickle(blm)
            self.remove_old_pickles(calculated_blm_loader, file_path)
            logging.info('{}\t done'.format(blm.name))
            return blm if self.should_return_blm else None

        except (BLMDataEmpty, BLMIntervalsEmpty) as e:
            e.logging_func('{} {}'.format(blm.name, e))
        except Exception as e:
            logging.critical('{} {} {}'.format(blm.name, traceback.format_exc(), e))
            raise e

    def remove_old_pickles(self, blm_calculated, new_pickle_file_path):
        if blm_calculated is not None:
            files_to_be_removed = filter(lambda f_path: f_path != new_pickle_file_path, blm_calculated.file_paths)
            for file_path in files_to_be_removed:
                os.remove(file_path)
                logging.info('{}\t removed'.format(file_path))

    def save_blm_as_pickle(self, blm):
        blm.clean_blm_intervals_from_temporary_data(clean_blm_data=True)
        blm.name = blm.name + ':' + self.field
        return blm.to_pickle(PICKLE_BLM_INTERVALS_DIR, self.start, self.end)

    def set_calculators_for_missing_intervals(self, blm, missing_intervals):
        logging.info('{}\t missing {} intervals'.format(blm.name, len(missing_intervals)))
        blm_already_calculated_blms = blm.blm_intervals
        blm.blm_intervals = missing_intervals
        self.set_blm_calculators(blm)
        self.merge_already_and_new_calculated_blm_intervals(blm, blm_already_calculated_blms)

    def merge_already_and_new_calculated_blm_intervals(self, blm, blm_already_calculated_blms):
        blm.blm_intervals = blm_already_calculated_blms | blm.blm_intervals

    def load_calculated_blm(self, blm, calculated_blm_loader):
        logging.info('{}\t exists'.format(blm.name))
        blm_calculated = calculated_blm_loader.load_pickles()
        return blm_calculated

    def check_if_blm_already_calculated(self, calculated_blms_loader):
        calculated_blms_loader.set_files_paths(PICKLE_BLM_INTERVALS_DIR, self.start, self.end, self.field)
        is_calculated_blms_existing = bool(calculated_blms_loader.file_paths)
        return is_calculated_blms_existing

    def load_pickled_raw_blm_data(self, blm):
        blm_names_list = [blm.name]
        blm_loader = BLMsRawPandasDataLoader(blm_names_list)
        blm_loader.set_files_paths(BLM_DATA_DIR, self.start, self.end, self.field)
        blm_loader.load_pickles()
        loaded_blms = list(blm_loader.get_blms())
        if len(loaded_blms) != 1:
            raise BLMNoRawData('No or too many files for {}'.format(blm.name))
        blm.data = loaded_blms[0].data

    def set_blm_calculators(self, blm):
        for calc in self.calculators:
            blm.set(calc)
