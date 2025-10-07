import shutil
import os
import pickle


from .kdown import download_raw_txtfiles
from .kdown import create_dict_ko
from .kdown import create_dict_c
from .kdown import create_dict_r
from .kdown import create_dict_map
from .kdown import create_dict_md
from .kdown import create_idcollection_dict
from .kdown import create_summary_dict



def do_kdown(logger, outdir, usecache, keeptmp): 
    
    
    logger.info(f"Respectfully retrieving metabolic information from KEGG. Raw data are being saved into '{outdir}/kdown/'. Be patient, could take a couple of days...")
    os.makedirs(f'{outdir}/kdown/', exist_ok=True)
    
    response = download_raw_txtfiles(logger, outdir, usecache)
    if type(response) == int: return 1
    else: RELEASE_kegg = response
    
    
    logger.info("Parsing downloaded KEGG information...")

    response = create_dict_ko(logger, outdir)
    if type(response) == int: return 1
    else: dict_ko = response
    
    response = create_dict_c(logger, outdir)
    if type(response) == int: return 1
    else: dict_c = response
    
    response = create_dict_r(logger, outdir)
    if type(response) == int: return 1
    else: dict_r = response
    
    response = create_dict_map(logger, outdir)
    if type(response) == int: return 1
    else: dict_map = response
    
    response = create_dict_md(logger, outdir)
    if type(response) == int: return 1
    else: dict_md = response
    
    
    # create 'idcollection_dict' and 'summary_dict' dictionaries
    idcollection_dict = create_idcollection_dict(dict_ko, dict_c, dict_r, dict_map, dict_md)
    summary_dict = create_summary_dict(dict_c, dict_r, dict_map, dict_md)
    
        
    return (RELEASE_kegg, idcollection_dict, summary_dict)




def main(args, logger):
    
    
    # adjust out folder path                      
    while args.outdir.endswith('/'):              
        args.outdir = args.outdir[:-1]
    os.makedirs(f'{args.outdir}/', exist_ok=True)
    
    
    # KEGG
    response = do_kdown(logger, args.outdir, args.usecache, args.keeptmp)
    if type(response) == int: return 1
    else: RELEASE_kegg, idcollection_dict, summary_dict = response[0], response[1], response[2]


    # create 'gsrap.maps':
    with open(f'{args.outdir}/gsrap.maps', 'wb') as wb_handler:
        pickle.dump({
            'RELEASE_kegg': RELEASE_kegg, 'idcollection_dict': idcollection_dict, 'summary_dict': summary_dict,
        }, wb_handler)
    logger.info(f"'{args.outdir}/gsrap.maps' created!")
    
        
    # clean temporary files:
    if not args.keeptmp:
        shutil.rmtree(f'{args.outdir}/kdown', ignore_errors=True)
        logger.info(f"Temporary raw files deleted!")
    
    
    return 0