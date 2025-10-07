import os
from pathlib import Path
import logging
import tempfile
import concurrent.futures as confu 
import sys


import cobra
import gempipe


from .pruner import load_input_universe
from .pruner import load_input_eggnog
from .pruner import parse_eggnog
from .pruner import subtract_kos
from .pruner import translate_remaining_kos
from .pruner import restore_gene_annotations

from .gapfillutils import include_forced

from .gapfill import gapfill_on_media

from .polishing import remove_universal_orphans
from .polishing import remove_forced
from .polishing import remove_disconnected
from .polishing import remove_sinks_demands

from .biologcuration import biolog_on_media

from ..commons import get_logger
from ..commons import get_databases
from ..commons import adjust_biomass_precursors
from ..commons import adjust_biomass_coefficients
from ..commons import force_id_on_sbml
from ..commons import write_excel_model
from ..commons import log_metrics
from ..commons import log_unbalances
from ..commons import format_expansion
from ..commons import comparative_table

from ..runsims.biosynth import biosynthesis_on_media



def create_model_incore(params):
    universe, eggpath, dbexp, args, multistrain = params
    logger = get_logger('gsrap_queued', args.verbose)  # loggers can't be pickled!
    if multistrain:
        # only errors will be recorded
        logger.setLevel(logging.ERROR)  


    # load the annotation
    eggnog = load_input_eggnog(logger, eggpath)


    # create a copy of the universe
    model = universe.copy()
    model.id = Path(eggpath).stem 


    ###### POLISHING 1
    # remove universal orphans
    model = remove_universal_orphans(logger, model)

    

    ###### PRUNING
    logger.info("Reading provided eggnog-mapper annotation...")
    # get important dictionaries: 'eggnog_ko_to_gids' and 'eggonog_gid_to_kos'
    eggnog_ko_to_gids, eggonog_gid_to_kos = parse_eggnog(eggnog)    

    # prune reactions
    subtract_kos(logger, model, eggnog_ko_to_gids)

    # translate KOs to the actual genes
    translate_remaining_kos(logger, model, eggnog_ko_to_gids)
    restore_gene_annotations(logger, model, universe, eggonog_gid_to_kos)

    

    ###### GAPFILLING
    # force inclusion of reactions:  
    include_forced(logger, model, universe, args.force_inclusion)

    # remove missing conditional precursors + get the 'cond_col_dict' dict.
    # 'cond_col_dict' is str-to-str: {'pheme_c': 'M00868: 1/8; M00121: 2/12;', 'hemeO_c': 'gr_HemeO: 0/1'}
    cond_col_dict = adjust_biomass_precursors(logger, model, universe, args.conditional) 

    # adjust biomass coefficients
    response = adjust_biomass_coefficients(logger, model, universe, dbexp, args.biomass)
    if response == 1: return 1

    # gap-fill based on media:
    df_B = gapfill_on_media(logger, model, universe, dbexp, args.gap_fill, cond_col_dict, args.exclude_orphans)
    if type(df_B)==int: return 1

    # force removal of reactions
    setattr(args, 'force_removal', '-')  # experimental feature, not public. It's main purpose was to test gap-filling in biolog_on_media().
    remove_forced(logger, model, universe, args.force_removal)

    # perform Biolog(R) curation based on media
    df_P = biolog_on_media(logger, model, universe, dbexp, args.gap_fill, args.biolog, args.exclude_orphans, args.cnps)
    if type(df_P)==int: return 1



    ###### POLISHING 2
    # remove unsed sinks and demands
    model = remove_sinks_demands(logger, model)  
    
    # remove disconnected metabolites
    model = remove_disconnected(logger, model)

    

    # # # # #   DERIVATION ENDS HERE   # # # # #
    log_metrics(logger, model)
    log_unbalances(logger, model)


    
    ###### CHECKS
    # check blocked metabolites / dead-ends
    df_S = biosynthesis_on_media(logger, model, dbexp, args.gap_fill, args.biosynth)
    if type(df_S)==int: return 1



    ###### POLISHING 3
    # reset growth environment befor saving the model
    gempipe.reset_growth_env(model)


    
    # output the model:
    logger.info("Writing strain-specific model...")
    cobra.io.save_json_model(model, f'{args.outdir}/{model.id}.json')        # JSON
    logger.info(f"'{args.outdir}/{model.id}.json' created!")
    cobra.io.write_sbml_model(model, f'{args.outdir}/{model.id}.xml')        # SBML   # groups are saved only to SBML
    logger.info(f"'{args.outdir}/{model.id}.xml' created!")
    force_id_on_sbml(f'{args.outdir}/{model.id}.xml', model.id)   # force introduction of the 'id=""' field
    sheets_dict = write_excel_model(model, f'{args.outdir}/{model.id}.mkmodel.xlsx', None, df_B, df_P, df_S)  
    logger.info(f"'{args.outdir}/{model.id}.mkmodel.xlsx' created!")
        
        
    return sheets_dict    



def main(args, logger):
    
    
    # adjust out folder path                      
    while args.outdir.endswith('/'):              
        args.outdir = args.outdir[:-1]
    os.makedirs(f'{args.outdir}/', exist_ok=True)
    
    
    # determine available cores
    cpu_count = os.cpu_count()
    if cpu_count == None: 
        logger.debug("Failed to count cpus. Reset to 1.")
        cpu_count = 1  
    if args.cores == 0:
        args.cores = cpu_count
    elif args.cores > cpu_count:
        logger.debug(f"Parameter --cores {args.cores} is greater than the maximum available ({cpu_count}): reset to {cpu_count}.")
        args.cores = cpu_count
    
    
    # format the --eggnog param
    args.eggnog = format_expansion(logger, args.eggnog)
    if args.eggnog == '-':
        logger.error("No valid eggnog-mapper annotations provided.")
        return 1
    if args.cores > len(args.eggnog):
        logger.debug(f"Parameter --cores {args.cores} is greater than the number of strains ({len(args.eggnog)}): reset to {len(args.eggnog)}.")
        args.cores = len(args.eggnog)
        
    
    # check compatibility of input parameters:
    if args.cnps == '-' and args.biolog != '-':
        logger.error("Missing starting C/N/P/S sources: --biolog must be used in conjunction with --cnps.")
        return 1
    
    
    # get dbexp (dbuni not really used):
    logger.info("Downloading gsrap experimental data...")
    response = get_databases(logger)
    if type(response)==int: return 1
    else: dbuni, dbexp, lastmap = response 
    
    
    # load universe:
    universe = load_input_universe(logger, args.universe)
    if type(universe)==int:
        return 1
    
    

    # disable logging (swith to txt) if strains are more than 1:
    multistrain = len(args.eggnog) > 1
    if multistrain:
        logger.info(f"Number of provided strains is >1: logging will be disabled.")
        logger.info(f"Performing {len(args.eggnog)} reconstructions relying on {args.cores} cores... ")
        # actualy this is done inside child processess!
            
    # create strain-specific GSMMs using multi-core
    error_raised = False
    sheets_dicts = []
    executor =  confu.ProcessPoolExecutor(max_workers=args.cores)
    futures = [executor.submit(create_model_incore, (universe, eggpath, dbexp, args, multistrain)) for eggpath in args.eggnog]
    for f in confu.as_completed(futures):
        sheets_dict = f.result() 
        
        # error raised in one of the cores:
        if type(sheets_dict) == int: 
            error_raised = True
            break   # a single error from a child process is sufficient to shutdown all the executor

        # this strain reached the end:
        else:
            if multistrain:
                sheets_dicts.append(sheets_dict)
                print(f"{len(sheets_dicts)}/{len(args.eggnog)} ({int(len(sheets_dicts)/len(args.eggnog)*100)}%) completed!", end='\r', file=sys.stderr)
    
    # hide last progress trace ('sheets_dicts' unused if not in multi-strain mode):
    if multistrain and sheets_dicts != []:
        last_trace = f"{len(sheets_dicts)}/{len(args.eggnog)} ({int(len(sheets_dicts)/len(args.eggnog)*100)}%) completed!"
        whitewash = ''.join([' ' for i in range(len(last_trace))])
        print(whitewash, end='\r', file=sys.stderr)   
    
    # multiproces part terminated: safely shut down the executor
    executor.shutdown(wait=True)
    
    # propagate errors if any:
    if error_raised:
        return 1
    
        
            
    # everything went fine, and there are > 1 strains: time to make the comparison table:
    if multistrain:
        
        logger.info("Collecting comparative tables...")
        comparative_table(logger, args.outdir, sheets_dicts)
            
        
        
    return 0