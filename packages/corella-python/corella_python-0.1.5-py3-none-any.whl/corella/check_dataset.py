import pandas as pd
from tabulate import tabulate
import os
from operator import itemgetter
from .get_dwc_noncompliant_terms import get_dwc_noncompliant_terms
from .check_abundance import check_abundance
from .check_basisOfRecord import check_basisOfRecord
from .check_collection import check_collection
from .check_coordinates import check_coordinates
from .check_datetime import check_datetime
from .check_events import check_events
from .check_individual_traits import check_individual_traits
from .check_license import check_license
from .check_locality import check_locality
from .check_observer import check_observer
from .check_occurrences import check_occurrences
from .check_occurrenceIDs import check_occurrenceIDs
from .check_occurrenceStatus import check_occurrenceStatus
from .check_scientificName import check_scientificName
from .check_taxonomy import check_taxonomy
from .common_dictionaries import terms_and_check_functions

def check_dataset(occurrences=None,
                  events=None,
                  occurrences_filename='occurrences.csv',
                  events_filename='events.csv',
                  publishing_dir='./data-publish/',
                  max_num_errors=5,
                  print_report=True):
    """
    Checks whether or not the data in your occurrences complies with
    Darwin Core standards.

    Parameters
    ----------
        occurrences: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your occurrences.
        events: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your events.
        occurrences_filename: ``str``
            The name of your final file containing your occurrences.  Default is ``occurrences.csv``.
        events_filename: ``pandas.DataFrame``
            The name of your final file containing your events.  Default is ``events.csv``.
        publishing_dir: ``str``
            The name of the folder your final data is written in.  Default is ``./data-publish/``.        
        max_num_errors: ``int``
            The maximum number of errors to display at once.  Default is ``5``.
        print_report: ``logical``
            Specify whether you want to print the report or return a ``Boolean`` 
            denoting whether or not the dataset passed.  Default is ``True``

    Returns
    -------
        Raises a ``ValueError`` if something is not valid.
    
    Examples
    --------
        `Passing Dataset Occurrences using check_dataset <../../html/corella_user_guide/independent_observations/passing_dataset.html>`_
    """
    all_functions = [check_abundance,check_basisOfRecord,check_collection,check_coordinates,check_dataset,
                     check_datetime,check_events,check_individual_traits,check_license,check_locality,
                     check_observer,check_occurrences,check_scientificName,check_taxonomy]

    # First, check if a dataframe is provided
    if occurrences is None and events is None:
        if not os.path.isfile('{}/{}'.format(publishing_dir,occurrences_filename)) and not os.path.isfile('{}/{}'.format(publishing_dir,events_filename)): 
            raise ValueError("Please provide either a dataframe or valid file name to this function.")
        else:
            if os.path.isfile('{}/{}'.format(publishing_dir,occurrences_filename)):
                occurrences = pd.read_csv('{}/{}'.format(publishing_dir,occurrences_filename))
                if 'eventDate' in occurrences.columns:
                    occurrences['eventDate'] = pd.to_datetime(occurrences['eventDate'])
            if os.path.isfile('{}/{}'.format(publishing_dir,events_filename)):
                events = pd.read_csv('{}/{}'.format(publishing_dir,events_filename))
                if 'eventDate' in events.columns:
                    events['eventDate'] = pd.to_datetime(events['eventDate'])

    # initialise errors 
    errors = []

    # initialise unicode symbols
    check_mark = u'\u2713'
    cross_mark = u'\u2717'

    # data
    compliance_dwc_standard = True

    # first, check for all terms that are not compliant
    vocab_check = []
    for df in [occurrences,events]:
        if df is not None:
            vocab_check_temp = get_dwc_noncompliant_terms(dataframe = df)
            vocab_check += vocab_check_temp
    
    # do vocab check 
    if len(vocab_check) > 0:
        compliance_dwc_standard = False
        terms_to_check = []
        for df in [occurrences,events]:
            if df is not None:
                terms_to_check += [x for x in df.columns if x not in vocab_check]

    occ_terms_check = []
    events_terms_check = []
    if occurrences is not None:
        occ_terms_check = list(occurrences.columns)
    if events is not None:
        events_terms_check = list(events.columns)
    
    # initialise table
    data_table = {
            'Number of Errors': [0 for x in range(len(terms_to_check))],
            'Pass/Fail': [check_mark for x in range(len(terms_to_check))],
            'Column name': list(terms_to_check)
    }

    # determine functions to check
    str_occ_functions = []
    str_event_functions = []
    for term in occ_terms_check:
        if term in terms_and_check_functions.keys():
            str_occ_functions.append(terms_and_check_functions[term])
    if events_terms_check is not None:
        for term in events_terms_check:
            if term in terms_and_check_functions.keys():
                str_event_functions.append(terms_and_check_functions[term])
    str_occ_functions = list(set(str_occ_functions))
    str_event_functions = list(set(str_event_functions))

    occ_functions=[]
    event_functions=[]
    for f in all_functions:
        if f.__name__ in str_occ_functions:
            occ_functions.append(f)
        if events is not None:
            if f.__name__ in str_event_functions:
                event_functions.append(f)

    # run all checks on occurrences
    if occurrences is not None:
        for f in occ_functions:
            errors_f = f(dataframe=occurrences)
            if type(errors_f) is list and len(errors_f) > 0:
                errors += errors_f

    # run all checks on events
    if events is not None:
        for f in event_functions:
            errors_f = f(dataframe=events)
            if type(errors_f) is list and len(errors_f) > 0:
                errors += errors_f
    
    # print out message to screen
    for i,cname in enumerate(data_table['Column name']):
        if any(cname in x for x in errors):
            data_table['Number of Errors'][i] += 1
            data_table['Pass/Fail'][i] = cross_mark
    
    df_data_table = pd.DataFrame(data_table)

    if print_report:
    
        print()
        print(tabulate(df_data_table, showindex=False, headers=df_data_table.columns))
        print()
        print("\n══ Results ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\n")
        print()
        total_errors = df_data_table['Number of Errors'].sum()
        total_passes = df_data_table[df_data_table['Pass/Fail'] == check_mark].value_counts().sum()
        print('Errors: {} | Passes: {}'.format(total_errors,total_passes))
        print()
        if not compliance_dwc_standard:
            print("{} Data does not meet minimum Darwin core requirements".format(cross_mark))
            print("Use corella.suggest_workflow()\n")
        else:
            print("{} Data meets minimum Darwin core requirements".format(check_mark))
        
        # Loop over column names that have errors
        num_errors = 0
        for i,cname in enumerate(data_table['Column name']):
            if data_table['Number of Errors'][i] > 0:
                print('── Error in {} ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────\n'.format(cname))
                temp_errors = [x for x in errors if cname in x]
                for e in temp_errors:
                    print(e)
                    num_errors += 1
                    if num_errors >= max_num_errors:
                        break 
                print()
    
    if df_data_table['Number of Errors'].sum() == 0 and compliance_dwc_standard:
        return True
    return False