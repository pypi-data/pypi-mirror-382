#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 15:28:36 2025

@author: Ken Carlton

Allow a comparison of SW/SL parts to those in slow_moving inventory.
This allows possible substitution of slow_moving parts in systems
currently being built so that slow_moving parts can be used up.
"""

#import pdb # use with pdb.set_trace()
import pandas as pd
from difflib import SequenceMatcher
import fnmatch
import re


def check_sm_parts(files_list, sm_files, cfg):
    ''' Collect part numbers and their descriptions that come from SolidWorks
    and SyteLine.  Compare the part numbers to those from a list of slow_moving
    parts to see if any of the slow_moving parts can be substituted.

    Parameters
    ----------
    files_list : list
        This list of two dictionaries that bomcheck.py supplies.
        It has the form:
        [{assembly_pn1: df1, assembly_pn2: df2, ..., assembly_pnN: dfN},
         {assembly_pn1: df1, assembly_pn2: df2, ..., assembly_pnN: dfN}]
        Where the first dictionary comes from SyteLine; the second from
        SolidWorks.  The df1, df2, etc. are the BOMs in DataFrame form
        that correspond to the assembly_pn.  The function discards the
        assembly part numbers.

    cfg : dictionary
        cfg is comes from bomcheck.py and is the exact same dictionary that
        is in bomcheck.py.  cfg provides alternative header names that the
        BOMs might have, such as "Material", "PARTNUMBER", "PART NUMBER",
        "Part Number", "Item"; and "DESCRIPTION", "Material Description", and
        "Description".  With these alternative names, this check_sm_parts
        function figures out what the correct headers should be for the part
        no. and descriptions fields.

    pn_fltr : string
        Part no. filter.  Normally will be assigned a value like '....-....-'.
        With this, part numbers 4610-2008-203, 5500-0025-001, and 6220-0055-004
        will be reduced to 4610-2008-, 5500-0025-, and 6220-0055-.  This
        reduction occurs in both the SW/SL BOMs and the slow_moving BOM.
        The shortened part nos. will be used for matching between BOM.  This
        will result in, for example 4610-2008-203 finding the closest matching
        parts from the slow_moving BOM to be 4610-2008-198, 4610-2008-199,
        4610-2008-200, etc..

        The string is a regex string
        (https://en.wikipedia.org/wiki/Regular_expression).  The dot, .,
        represents one character.  Other suitable values for pn_filtr could be
        '.{10}', '.+-.+-'.  (.{10} means ten characters.  The .+ means one or
        more characters)

    descrip_filter : string, optional
        This filters the 'Item Description' field of the slow moving BOM.
        Only parts who's descriptions that are able to pass through this filter
        will show up in the results of this check_sm_parts function.

        The string is a regex string.  Furthermore the string allows for "or"
        and "and" types of filtering.  For example if you want to reduce
        the parts shown to only stainless steel parts that are Nema 7, you
        could use the filter 'S/S|SS|316|304&N7|NEMA 7'  This means
        '(SS or 316 or 304) and (N7 or NEMA 7)'.  The bar, !, represents "or".
        The ampersand character, &, represents "and".  Note: spaces count.
        Thus 'SS|316|304&N7|NEMA 7' is different from 'SS|316|304& N7 | NEMA 7'

        The default is ''.

    Returns
    -------
    DataFrame

    Only the union of the SW/SL BOMs and the slow_moving BOM is output; 
    e.g. pt nos and desriptions, costs, usage, etc.
    '''
        
    # extract from "cfg" args from the user.
    pn_fltr = cfg['filter_pn'].text()
    descrip_filter = cfg['filter_descrip'].text() if cfg['filter_descrip'] else ''

    ####################################################################################
    ##### create df and populate it.  df is a collection of BOMs from SW & SL      #####
    ####################################################################################
    df = pd.DataFrame() # start with an empty DataFrame
    for f in files_list:
        for k, v in f.items():
            dfi = v.copy()
            values = dict.fromkeys(cfg['part_num'], 'pn sw/sl')   # make sure pns headers are all the same: pn
            values.update(dict.fromkeys(cfg['descrip'], 'descrip sw/sl'))  # make sure descrip headers all the same: descrip
            dfi.rename(columns=values, inplace=True)   # rename appropriate column headers to "pn" and "descrip"
            if 'cost' in dfi.columns:
                dfi = dfi[['pn sw/sl', 'descrip sw/sl', 'cost']]   # delete all columns but "pn", "descrip"
            else:
                dfi = dfi[['pn sw/sl', 'descrip sw/sl']]
            df = pd.concat([df, dfi])
    #df.sort_values(by='pn sw/sl', ascending=True, inplace=True)
    df.drop_duplicates(subset=['pn sw/sl'], keep='first')
    df['common_pn'] = df['pn sw/sl'].str.extract('(' + pn_fltr +')')  # apply the pn_fltr
        
    if cfg['drop_bool']==True and cfg['drop']:
        filtr3 = is_in(cfg['drop'], df['pn sw/sl'], cfg['exceptions'])
        df.drop(df[filtr3].index, inplace=True)
    
    
    ####################################################################################
    ##### dfinv is the dataframe derived from the excel sheet of slow_moving parts #####
    ####################################################################################
    dfinv = pd.DataFrame()  # start with an empty DataFrame
    for k, v in sm_files.items():
        dfinv = pd.concat([dfinv, v])
            
    # Some more preperation to df. Get costs of parts from dfinv.  
    df2 = df.merge(dfinv, left_on='pn sw/sl', right_on='Item', how='left')
    df2 = df2.rename(columns={'Unit\nCost': 'cost2'})
    s = df2['cost2'].copy(deep=True)
    s = s.fillna(0).tolist()
    df['cost_'] = s
    df['cost_'] = '$' + df['cost_'].round(2).astype('string')
    
    
    dfinv['De-\nmand?']= dfinv['De-\nmand?'].replace('No Demand', 'No')
    dfinv['De-\nmand?']= dfinv['De-\nmand?'].replace('Demand', 'Yes')
    
    if not cfg['show_demand']:    
        dfinv = dfinv[dfinv['De-\nmand?'] == 'No']
        dfinv = dfinv.drop('De-\nmand?', axis=1)
    if not cfg['on_hand']:    
        dfinv = dfinv[dfinv['On\nHand'] != 0.0]
        
    # match sure only number, e.g. "100, extracted from 'Last Used\n(Days)'
    # and not "100 days", that a user could enter.    
    match = re.search(r'\d+', cfg['filter_age'].text())
    if match:
        min_age = float(match.group())
    else:
        min_age = 0  
    dfinv = dfinv[dfinv['Last Used\n(Days)'] > min_age]
    dfinv['common_pn'] = dfinv['Item'].str.extract('(' + pn_fltr +')')
    dfinv = dfinv.drop(dfinv.index[-1])
    dfinv['Description'] = dfinv['Description'].fillna('')
    dfinv = dfinv.dropna(subset=['common_pn'])
    dfinv['Unit\nCost'] = '$' + dfinv['Unit\nCost'].round(2).astype('string')
    # dfinv = dfinv[dfinv['Movement?'] == 'No Demand']
    
    # apply the descrip_filter
    if descrip_filter:
        for f in descrip_filter.split('&'):
            dfinv = dfinv[dfinv['Description'].str.contains(f, case=False, regex=True)]
    if descrip_filter and cfg['repeat']:
        for f in descrip_filter.split('&'):
            df = df[df['descrip sw/sl'].str.contains(f, case=False, regex=True)]
  
    
    ####################################################################################
    ##### merge df & dfinv                                                         #####
    ####################################################################################    
    df = df.merge(dfinv, on='common_pn', how=cfg['merge'])
    df = df.drop('common_pn', axis=1)
    
    alter_score = [(r'S/S|[^A-Z]SS[^A-Z]|304|316|STAINLESS|LSS|SST', .2),
                              (r'NEMA 7|N7', .2), (r'24V', .2), (r'125V|120V|115V|110V|100V', .2)]
    
    
    ####################################################################################
    ##### Finish up                                                                #####
    ####################################################################################
    
    # similarity_score is based on what the module SequenceMatcher produces.  However
    # I want the score reduced more if, for example, the "descrip sw/sl" is SS and
    # "Description" is not SS.  In this case, reduce similarity_score by %20.
    # The variable 'alter_score' looks for these adjustments.    
    alter_score = [(r'S/S|[^A-Z]SS[^A-Z]|304|316|STAINLESS|LSS|SST|[^A-Z]SS$', .2),
                              (r'NEMA 7|N7', .2), (r'24\s*V', .2), (r'1[0-2][0-5]\s*V', .2),
                              (r'230/460\s*V|230\s*V|460\s*V', .2), (r'575\s*V', .2), (r'200\s*V', .2)] 
    
    df['descrip sw/sl'] = df['descrip sw/sl'].replace(0, 'missing description')
    if cfg['merge'] == 'inner':
        similarity_score = df.apply(lambda row: SequenceMatcher(None, row['descrip sw/sl'], row['Description']).ratio(), axis=1) 
        for alter in alter_score:
            similarity_score = similarity_score.where(~(df['descrip sw/sl'].str.contains(alter[0],case=False, regex=True) &
                                          ~df['Description'].str.contains(alter[0], case=False, regex=True)),
										  similarity_score*alter[1])
        # If someone enters a percent character, %, when indicating the min similarity he wishes
        # to see, for example 86%, the % chacter will crash the program.  So this program will
        # fix the problem by extracting the number, i.e. 86, from the text, i.e. 86%
        match = re.search(r'\d+', cfg['similar'].text())
        if match:
            min_similarity = float(match.group())
        else:
            min_similarity = 0               
        similarity_bool = similarity_score*100 > min_similarity
        df['similar'] = (similarity_score*100).round().astype(int)
        df = df[similarity_bool]
        
    if 'cost' in df.columns:
        df['cost'] = '$' + df['cost'].round(2).astype('string')
    
    # if leading or trailing spaces differ, for example, between a text
    # in one descrip and another, then the df.drop_duplicates() won't work
    # to catch the duplicate line.
    for col in ['pn sw/sl', 'descrip sw/sl', 'Item', 'Description']:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
    
    df = df.drop_duplicates()
    df.sort_values(by=['pn sw/sl', 'similar'], ascending=[True, False], inplace=True)
    df['similar'] = df['similar'].astype('string') + '%'
# =============================================================================
#     if 'cost' in df.columns:
#         new_column_order = ['pn sw/sl', 'descrip sw/sl', 'cost', 'similar', 'Item', 'Description',
#                             'Unit Cost', 'On Hand', 'Yr n-1 Usage', 'Yr n-2 Usage', 'Last Used']
#     else:
#         new_column_order = ['pn sw/sl', 'descrip sw/sl', 'similar', 'Item', 'Description',
#                             'Unit Cost', 'On Hand', 'Yr n-1 Usage', 'Yr n-2 Usage', 'Last Used']
#     df = df[new_column_order]
# =============================================================================
    if 'De-\nmand?' in df.columns:
        new_column_order = ['pn sw/sl', 'descrip sw/sl', 'cost_', 'Item', 'Description',
                            'similar', 'On\nHand', 'Unit\nCost', 'Yr n-1\nUsage', 'Yr n-2\nUsage',
                            'Last Used\n(Days)', 'De-\nmand?']
    else:
        new_column_order = ['pn sw/sl', 'descrip sw/sl', 'cost_', 'Item', 'Description',
                            'similar', 'On\nHand', 'Unit\nCost', 'Yr n-1\nUsage', 'Yr n-2\nUsage',
                            'Last Used\n(Days)']
  
    df = df[new_column_order]

    if 'cost' in df.columns:
        df.drop(columns=['cost'])
        
    df['alt\nqty'] = ''


    df.reset_index(drop=True, inplace=True)
    return df


def is_in(find, series, xcept):
    '''Argument "find" is a list of strings that are glob
    expressions.  The Pandas Series "series" will be
    evaluated to see if any members of find exists as
    substrings within each member of series.  Glob
    expressions are strings like '3086-*-025' or *2020*.
    '3086-*-025' for example will match'3086-0050-025'
    and '3086-0215-025'.

    The output of the is_in function is a Pandas Series.
    Each member of the Series is True or False depending on
    whether a substring has been found or not.

    xcept is a list of exceptions to those in the find list.
    For example, if '3086-*-025' is in the find list and
    '3086-3*-025' is in the xcept list, then series members
    like '3086-0515-025' or '3086-0560-025' will return a
    True, and '3086-3050-025' or '3086-3060-025' will
    return a False.

    For reference, glob expressions are explained at:
    https://en.wikipedia.org/wiki/Glob_(programming)

    Parmeters
    =========

    find: string or list of strings
        Items to search for

    series:  Pandas Series
        Series to search

    xcept: string or list of strings
        Exceptions to items to search for

    Returns
    =======

    out: Pandas Series, dtype: bool
        Each item is True or False depending on whether a
        match was found or not
    '''
    if not isinstance(find, list):
        find = [find]
    if not isinstance(xcept, list) and xcept:
        xcept = [xcept]
    elif isinstance(xcept, list):
        pass
    else:
        xcept = []
    series = series.astype(str).str.strip()  # ensure that all elements are strings & strip whitespace from ends
    find2 = []
    for f in find:
        find2.append('^' + fnmatch.translate(str(f)) + '$')  # reinterpret user input with a regex expression
    xcept2 = []
    for x in xcept:  # exceptions is also a global variable
        xcept2.append('^' +  fnmatch.translate(str(x))  + '$')
    if find2 and xcept2:
        filtr = (series.str.contains('|'.join(find2)) &  ~series.str.contains('|'.join(xcept2)))
    elif find2:
        filtr = series.str.contains('|'.join(find2))
    else:
        filtr = pd.Series([False]*series.size)
    return filtr











