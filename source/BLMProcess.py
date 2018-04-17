

import psycopg2

from Common_classes.BLMClasses.BLM_exceptions import BLMDataEmpty, BLMIntervalsEmpty

import logging
import traceback
import copy
from datetime import timedelta
from time import time

from sortedcontainers import SortedSet

from Common_classes.DBConnector import BLMInterval,  SingleBeamModeBLMSubInterval, BLM

class BLMProcess:
    """
    This class encapsulates whole data processing for a one BLM. It reads the data, then conducts calculations (if needed) and saves a analysed BLM class
    object to a pickle file.
    """
    def __init__(self, requested_run, field, calculators, should_return_blm, db_connector, beam_intervals):
        """
        :param datetime start: end of analysed period
        :param datetime end: beginning of analysed period
        :param str field: ex. LOSS_RS12
        :param list calculators: calculators, which set appropriate fields in a BLM class object
        :param bool should_return_blm: if set to True, after calculation and saving to a pickle file a BLM will be returned (for example to make plots)
        :param str blm_raw_data_dir: a path to the directory with a stored raw BLM data
        :param str pickled_blm_dir: a path to the directory with already calculated BLM pickles
        """
        self.requested_run = requested_run
        self.field = field
        self.calculators = calculators
        self.should_return_blm = should_return_blm
        self.db_connector = db_connector
        self.beam_intervals = beam_intervals
        self.beam_subintervals = {beam_interval.start_time: beam_interval.beam_subintervals for beam_interval in self.beam_intervals}



    def run(self, blm):
        """
        This method is the main method for that class. It takes a raw BLM's class object (which contains name,position, not integrated blm_intervals and subintervals),
        then it checks if the BLM has already been calculated (pickle file exists). If yes, it reads the pickled BLM and compares BLM's intervals. Then calculations
        are performed only for missing BLM's intervals. If any calculations are performed, the updated pickle file will be saved.
        :param BLM blm_scratch: BLM object without assigned data and calculated partial doses for subintervals
        :return:
        """

        logging.info('{}\t start'.format(blm.name))

        try:
            self.db_connector.connect_to_db()
            blm = self.db_connector.session.query(type(blm)).populate_existing().get(blm.name)

            blm_intervals = blm.blm_intervals.filter(BLMInterval.start_time >= self.requested_run.get_earliest_date()). \
                filter(BLMInterval.start_time <= self.requested_run.get_latest_date()).all()
            existing_blm_intervals = SortedSet(blm_intervals)

            needed_blm_intervals = SortedSet(BLMInterval(start=bi.start_time,
                                                         end=bi.end_time,
                                                         variable=self.field,
                                                         beam_interval_id=bi.id,
                                                         blm_name=blm.name)
                                             for bi in self.beam_intervals)
            self.set_blm_subintervals(needed_blm_intervals)
            missing_blm_intervals = needed_blm_intervals - existing_blm_intervals

            if missing_blm_intervals:
                earliest_interval_start = missing_blm_intervals[0].start_time
                latest_interval_end = missing_blm_intervals[-1].end_time
                self.set_blm_data(blm, earliest_interval_start - timedelta(days=1), latest_interval_end + timedelta(days=1))
                self.set_calculators_for_missing_intervals(blm, missing_blm_intervals)
                self.update_blm_in_db(blm)
            logging.info('{}\t done'.format(blm.name))
            return blm if self.should_return_blm else None

        except (BLMDataEmpty, BLMIntervalsEmpty) as e:
            e.logging_func('{} {}'.format(blm.name, e))
        except Exception as e:
            logging.critical('{} {} {}'.format(blm.name, traceback.format_exc(), e))
            raise e
        finally:
            self.db_connector.close()

    def set_blm_subintervals(self, blm_intervals):
        for blm_interval in blm_intervals:
            blm_interval.blm_subintervals = list(SingleBeamModeBLMSubInterval(
                bs.start_time,
                bs.end_time,
                bs.beam_mode_id,
                None,
                bs.id,
                blm_interval.id
            ) for bs in self.beam_subintervals[blm_interval.start_time])

    def update_blm_in_db(self, blm):

        logging.info('to be updated {}'.format(str(blm)))

        try:
            self.db_connector.session.merge(blm)
        except psycopg2.IntegrityError as e:
            # logging.warning('{}: {} duplicated rows'.format(PyTimberIntensityDownloader.class_name, task_description))
            raise e

        else:
            self.db_connector.session.commit()
            logging.info('{} saved to db'.format(str(blm)))
        finally:
            self.db_connector.close()


    def set_blm_data(self, blm, start=None, end=None):
        if start is None:
            start = self.requested_run.get_earliest_date() - timedelta(days=1)
        if end is None:
            end = self.requested_run.get_latest_date() + timedelta(days=1),
        blm.data = self.db_connector.get_raw_blm_data(start,
                                                      end,
                                                      id_blm=blm.id, table_name='raw_blm_data_loss_rs12')
        blm.interpolate_data()

    # def update_pickled_blm(self, blm_scratch, all_already_calculated_intervals, files_to_be_deleted):
    #     """
    #     It saves BLM's pickle updated version and removes the old pickle file.
    #     :param BLM blm_scratch: A BLM with intervals that has been calculated during current program execution.
    #     :param SortedSet all_already_calculated_intervals: collection of BLM intervals which have been already calculated
    #     :param list files_to_be_deleted: list of files paths
    #     :return:
    #     """
    #     blm_to_be_saved = blm_scratch
    #     if all_already_calculated_intervals:
    #         blm_to_be_saved = copy.deepcopy(blm_scratch)
    #         blm_to_be_saved.blm_intervals.update(all_already_calculated_intervals)
    #     file_path = self.save_blm_as_pickle(blm_to_be_saved)
    #     # self.remove_old_pickles(files_to_be_deleted, file_path)

    # def get_only_needed_blm_intervals(self, blm_scratch, all_calculated_blm_intervals):
    #     """
    #     It returns only those blm intervals, that haven't been calculated yet.
    #     :param BLM blm_scratch: BLM with non calculated intervals
    #     :param SortedSet all_calculated_blm_intervals: list of already calculated BLM intervals
    #     :return:
    #     """
    #     return blm_scratch.blm_intervals.intersection(all_calculated_blm_intervals)
    #
    # def remove_old_pickles(self, files_to_be_deleted, new_pickle_file_path):
    #     """
    #     It deletes all files from the files_to_be_deleted list. If new_pickle_file_path appears in files_to_be_deleted it won't be deleted.
    #     :param list files_to_be_deleted: files with those paths will be removed.
    #     :param str new_pickle_file_path: file with that path won't be deleted
    #     :return:
    #     """
    #     if files_to_be_deleted is not None:
    #         files_to_be_removed = filter(lambda f_path: f_path != new_pickle_file_path, files_to_be_deleted)
    #         for file_path in files_to_be_removed:
    #             os.remove(file_path)
    #             logging.info('{}\t removed'.format(file_path))
    #

    def set_calculators_for_missing_intervals(self, blm, missing_intervals):
        """
        It sets calculators (offset estimation, integration etc.) only to missing BLM intervals.
        :param BLM blm_scratch: BLM
        :param SortedSet missing_intervals: BLM intervals, that haven't been already calculated (integrated dose + offsets are not calculated)
        :return:
        """
        logging.info('{}\t missing {} intervals'.format(blm.name, len(missing_intervals)))
        if not blm.data.empty:
            for calc in self.calculators:
                calc.run(blm.data, missing_intervals)
        blm.blm_intervals.extend(missing_intervals)

    # def merge_already_and_new_calculated_blm_intervals(self, blm_new_calculated_intervals, blm_already_calculated_blms):
    #     """
    #     It merges BLM intervals SortedSets, which are passed as arguments.
    #     :param SortedSet blm_new_calculated_intervals:
    #     :param SortedSet blm_already_calculated_blms:
    #     :return SortedSet: merged BLM intervals
    #     """
    #     return SortedSet(blm_already_calculated_blms) | SortedSet(blm_new_calculated_intervals)

    # def load_calculated_blm(self, blm, calculated_blm_loader):
    #     """
    #     It
    #     :param BLM blm:
    #     :param BLMsCalculatedLoader calculated_blm_loader:
    #     :return :
    #     """
    #     logging.info('{}\t exists'.format(blm.name))
    #     blm_calculated = calculated_blm_loader.load_pickles()
    #     return blm_calculated



    def set_blm_calculators(self, blm):
        """
        It sets calculators to the BLM.
        :param BLM blm: a BLM class object which needs to be calculated.
        :return:
        """
        for calc in self.calculators:
            blm.set(calc)
    #
    # def set_blm_calculators_for_missing_intervals(self, data, blm_name, blm_intervals):
    #     """
    #     It sets calculators to the BLM.
    #     :param BLM blm: a BLM class object which needs to be calculated.
    #     :return:
    #     """
    #
    #     for calc in self.calculators:
    #         blm.set(calc)
