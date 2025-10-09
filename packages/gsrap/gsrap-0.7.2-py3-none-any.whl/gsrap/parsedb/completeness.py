from pathlib import Path


import pandas as pnd



def parse_eggnog(model, eggnog, idcollection_dict):
    
    
    eggnog = pnd.read_csv(eggnog, sep='\t', comment='#', header=None)
    eggnog.columns = 'query	seed_ortholog	evalue	score	eggNOG_OGs	max_annot_lvl	COG_category	Description	Preferred_name	GOs	EC	KEGG_ko	KEGG_Pathway	KEGG_Module	KEGG_Reaction	KEGG_rclass	BRITE	KEGG_TC	CAZy	BiGG_Reaction	PFAMs'.split('\t')
    eggnog = eggnog.set_index('query', drop=True, verify_integrity=True)
    
    
    # PART 1. get KO codes available
    kos_org = set()
    for gid, kos in eggnog['KEGG_ko'].items():
        if kos == '-': 
            continue
        kos = kos.split(',')
        kos = [i.replace('ko:', '') for i in kos]
        for ko in kos: 
            kos_org.add(ko)
            
            
    # PART 2. get reactions in the organism (even the GPR is not complete)
    kr_to_kos = idcollection_dict['kr_to_kos']
    krs_org = set()
    for kr, kos in kr_to_kos.items(): 
        if any([ko in kos_org for ko in kos]):
            krs_org.add(kr)
    
    
    return krs_org
    
    
    
def check_completeness(logger, model, progress, module, focus, eggnog, idcollection_dict, summary_dict): 
    # check KEGG annotations in the universe model to get '%' of completeness per pathway/module.
    
            
    # get the reference set of kr codes (all kegg or organism specific): 
    kr_uni = set()
    if eggnog != '-':
        for eggfile in eggnog:
            eggset = parse_eggnog(model, eggfile, idcollection_dict)
            kr_uni = kr_uni.union(eggset)
        kr_uni_label = f"{len(eggnog)} eggnog annotations"
    else: 
        kr_uni = idcollection_dict['kr']
        kr_uni_label = "whole KEGG"
    
    
    # get all the 'kr' annotations in the model
    kr_ids_modeled = set()
    for r in model.reactions: 
        if 'kegg.reaction' in r.annotation.keys():
            for kr_id in r.annotation['kegg.reaction']:
                kr_ids_modeled.add(kr_id)
    kr_uni_missing = kr_uni - kr_ids_modeled
    kr_uni_coverage = len(kr_ids_modeled.intersection(kr_uni)) / len(kr_uni) * 100
    logger.info(f"Coverage for '{kr_uni_label}': {round(kr_uni_coverage, 0)}% ({len(kr_uni_missing)} missing).")
    
    
    # define the map?????, containing krs not included in maps
    krs_in_maps = set()
    for i in summary_dict: krs_in_maps = krs_in_maps.union(i['kr_ids']) 
    krs_not_in_maps = idcollection_dict['kr'] - krs_in_maps
    summary_dict.append({
        'map_id': 'map?????',
        'map_name': 'Not included in maps',
        'kr_ids': krs_not_in_maps,
        'cnt_r': len(krs_not_in_maps),
        'mds': []
    })    
    
    
    # get all the map / md codes:
    map_ids = set()
    md_ids = set()
    for i in summary_dict:
        map_ids.add(i['map_id'])
        for j in i['mds']:
            md_ids.add(j['md_id'])
            
            
    # check if 'focus' exist
    if focus != '-' and focus not in map_ids and focus not in md_ids:
        logger.error(f"The ID provided with --focus does not exist: {focus}.")
        return 1
    if focus.startswith('map'):
        logger.debug(f"With --focus {focus}, --module will switch to False.")
        module = False
    if focus != '-':
        missing_logger = ()
    
    
    # define some counters:
    maps_finished = set()
    maps_noreac = set()
    maps_missing = set()
    maps_partial = set()

    
    list_coverage  = []
    
    
    # iterate over each map:
    for i in summary_dict:
        
        
        # get ID and name: 
        map_id = i['map_id']
        map_name_short = f"{i['map_name'][:20]}"
        if len(i['map_name']) > 20: 
            map_name_short = map_name_short + '...'
        else:  # add spaces as needed: 
            map_name_short = map_name_short + ''.join([' ' for i in range(23-len(map_name_short))])
            
            
        # check if this map was (at least partially) covered:
        map_krs = set([kr for kr in i['kr_ids'] if kr in kr_uni])
        missing = map_krs - kr_ids_modeled
        present = kr_ids_modeled.intersection(map_krs)
        if focus == map_id: 
            missing_logger = (map_id, missing)

        
        # put the map in the right bucket:
        if missing == set() and map_krs != set():
            maps_finished.add(map_id)
        elif map_krs == set():
            maps_noreac.add(map_id)
        elif missing == map_krs:
            maps_missing.add(map_id)
        elif len(missing) < len(map_krs):
            maps_partial.add(map_id)
            
            
        # get '%' of completeness:
        if len(map_krs) != 0: perc_completeness = len(present)/len(map_krs)*100
        else: perc_completeness = 100   # for maps_noreac
        perc_completeness_str = str(round(perc_completeness))   # version to be printed
        if len(perc_completeness_str)==1: 
            perc_completeness_str = ' ' + perc_completeness_str

            
        # append map to list:
        list_coverage.append({
            'map_id': map_id,
            'map_name_short': map_name_short, 
            'perc_completeness': perc_completeness,
            'perc_completeness_str': perc_completeness_str,
            'present': present,
            'missing': missing,
            'md_ids': [j['md_id'] for j in i['mds']],
        })
        
        
    
    # create coverage dataframe
    if eggnog != '-' and len(eggnog) >= 2:  
        df_coverage = {}
        for i in list_coverage:
            for kr in i['present'].union(i['missing']):
                if kr not in df_coverage.keys(): 
                    df_coverage[kr] = {'map_ids': set()}
                df_coverage[kr]['map_ids'].add(i['map_id'])
        df_coverage = pnd.DataFrame.from_records(df_coverage).T
        df_coverage['modeled'] = False
        for kr, row in df_coverage.iterrows():
            if kr in kr_ids_modeled:
                df_coverage.loc[kr, 'modeled'] = True
        # build strain columns all at once
        df_strains = []  # list of small DataFrames
        for eggfile in eggnog:
            strain = Path(eggfile).stem
            eggset = parse_eggnog(model, eggfile, idcollection_dict)
            col = df_coverage.index.to_series().isin(eggset).astype(int)
            df_strains.append(col.rename(strain))
        df_strains = pnd.concat(df_strains, axis=1)
        # sort rows: upper rows are present in more strains
        df_strains = df_strains.loc[df_strains.sum(axis=1).sort_values(ascending=False).index]
        df_coverage = df_coverage.loc[df_strains.index]
        df_coverage = pnd.concat([df_coverage, df_strains], axis=1)
        # split in 2: modeled above, non-modeled below:
        df_coverage = pnd.concat([df_coverage[df_coverage['modeled']==True], df_coverage[df_coverage['modeled']==False]])
    else:  # not interesting in a super-long table without strains in column
        df_coverage = None
    
           
            
    # order list by '%' of completness and print if needed:
    list_coverage = sorted(list_coverage, key=lambda x: x['perc_completeness'], reverse=True)
    for i in list_coverage:
        if progress:
            if focus=='-' or focus in i['md_ids'] or focus==i['map_id']:
                if i['map_id'] in maps_missing or i['map_id'] in maps_partial:
                    logger.info(f"{i['map_id']}: {i['map_name_short']} {i['perc_completeness_str']}% completed, {len(i['present'])} added, {len(i['missing'])} missing.")
        
        
        # get the correspondent pathway element of the 'summary_dict'
        right_item = None
        for k in summary_dict:
            if k['map_id'] == i['map_id']:
                right_item = k
                
                
        # define some counters:
        mds_completed = set()
        mds_noreac = set()
        mds_missing = set()
        mds_partial = set()


        list_coverage_md  = []
        spacer = '    '


        # iterate over each module:
        for z in right_item['mds']:


            # get ID and name: 
            md_id = z['md_id']
            md_name_short = f"{z['md_name'][:20]}"
            if len(z['md_name']) > 20: 
                md_name_short = md_name_short + '...'
            else:  # add spaces as needed: 
                md_name_short = md_name_short + ''.join([' ' for i in range(23-len(md_name_short))])


            # check if this module was (at least partially) covered:
            md_krs = set([kr for kr in z['kr_ids_md'] if kr in kr_uni])
            missing = md_krs - kr_ids_modeled
            present = kr_ids_modeled.intersection(md_krs)
            if focus == md_id: 
                missing_logger = (md_id, missing)
            
            
            # put the map in the right bucket:
            if missing == set() and md_krs != set():
                mds_completed.add(md_id)
            elif md_krs == set():
                mds_noreac.add(md_id)
            elif missing == md_krs:
                mds_missing.add(md_id)
            elif len(missing) < len(md_krs):
                mds_partial.add(md_id)

                
            # get '%' of completeness:
            if len(md_krs) != 0: perc_completeness = len(present)/len(md_krs)*100
            else: perc_completeness = 100   # for mds_noreac
            perc_completeness_str = str(round(perc_completeness))   # version to be printed
            if len(perc_completeness_str)==1: 
                perc_completeness_str = ' ' + perc_completeness_str

                
            # append md to list:
            list_coverage_md.append({
                'md_id': md_id,
                'md_name_short': md_name_short, 
                'perc_completeness': perc_completeness,
                'perc_completeness_str': perc_completeness_str,
                'present': present,
                'missing': missing,
            })
               
            
        # order list by '%' of completness and print if needed:
        list_coverage_md = sorted(list_coverage_md, key=lambda x: x['perc_completeness'], reverse=True)
        for z in list_coverage_md:
            if module:
                if focus=='-' or focus==z['md_id']:
                    if z['md_id'] in mds_missing or z['md_id'] in mds_partial:
                        logger.info(f"{spacer}{z['md_id']}: {z['md_name_short']} {z['perc_completeness_str']}% completed, {len(z['present'])} added, {len(z['missing'])} missing.")
        
        
        # print summary:
        if module and focus=='-':
            logger.info(f"{spacer}Modules of {right_item['map_id']}: completed {len(mds_completed)} - partial {len(mds_partial)} - missing {len(mds_missing)} - noreac {len(mds_noreac)}")
    if focus != '-':
        logger.info(f"Missing reactions focusing on {missing_logger[0]}: {' '.join(list(missing_logger[1]))}.")
    if progress:
        logger.info(f"Maps: finished {len(maps_finished)} - partial {len(maps_partial)} - missing {len(maps_missing)} - noreac {len(maps_noreac)}")
            
        
    return df_coverage     


