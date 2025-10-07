"""
eos reduces measurements performed on Amor@SINQ, PSI

Author: Jochen Stahn (algorithms, python draft),
        Artur Glavic (structuring and optimisation of code)
"""

import logging

# need to do absolute import here as pyinstaller requires it
from eos.options import EOSConfig, ReaderConfig, ExperimentConfig, ReductionConfig, OutputConfig
from eos.command_line import commandLineArgs
from eos.logconfig import setup_logging, update_loglevel

def main():
    setup_logging()

    # read command line arguments and generate classes holding configuration parameters
    clas = commandLineArgs([ReaderConfig, ExperimentConfig, ReductionConfig, OutputConfig],
                           'eos')
    update_loglevel(clas.verbose)

    reader_config = ReaderConfig.from_args(clas)
    experiment_config = ExperimentConfig.from_args(clas)
    reduction_config = ReductionConfig.from_args(clas)
    output_config = OutputConfig.from_args(clas)
    config = EOSConfig(reader_config, experiment_config, reduction_config, output_config)

    logging.warning('######## eos - data reduction for Amor ########')

    # only import heavy module if sufficient command line parameters were provided
    from eos.reduction import AmorReduction
    # Create reducer with these arguments
    reducer = AmorReduction(config)
    # Perform actual reduction
    reducer.reduce()

    logging.info('######## eos - finished ########')

if __name__ == '__main__':
    main()
