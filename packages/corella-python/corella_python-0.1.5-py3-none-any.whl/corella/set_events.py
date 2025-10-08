import pandas as pd
from .add_unique_IDs import add_unique_IDs
from .check_events import check_events
from .common_functions import check_for_dataframe,set_data_workflow
from .generate_eventID_parentEventID import generate_eventID_parentEventID

def set_events(dataframe=None,
               eventID=None,
               parentEventID=None,
               eventType=None,
               Event=None,
               samplingProtocol=None,
               event_hierarchy=None,
               sep='-'):
    """
    Identify or format columns that contain information about an Event. An "Event" in Darwin Core Standard refers to an action that occurs at a place and time. Examples include:

    - A specimen collecting event
    - A survey or sampling event
    - A camera trap image capture
    - A marine trawl
    - A camera trap deployment event
    - A camera trap burst image event (with many images for one observation)

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        eventID: ``str``, ``list``, ``logical``
            You can provide 3 types of arguments to ``eventID``:
            - ``str``: rename the column of interest to ``eventID``
            - ``list``: generate composite ids.  If you want either sequential numbers or 
                        random UUIDs added, use the keywords ``"sequential"`` or ``"random"``
                        to your 
            *Note*: Every occurrence should have an eventID entry. Ideally, IDs should be 
            persistent to avoid being lost in future updates. They should also be unique, both within 
            the dataset, and (ideally) across all other datasets.
        sep: ``char``
            Separation character for composite IDs.  Default is ``-``.
        parentEventID: ``str``
            A column name (``str``) that contains a unique ID belonging to an event below 
            it in the event hierarchy.
        eventType: ``str`` 
            A column name (``str``) or a ``str`` denoting what type of event you have.
        Event: ``str`` 
            A column name (``str``) or a ``str`` denoting the name of the event.
        samplingProtocol: ``str`` or 
            Either a column name (``str``) or a ``str`` denoting how you collected the data, 
            i.e. "Human Observation".
        event_hierarchy: ``dict``
            A dictionary containing a hierarchy of all events so they can be linked.  For example, 
            if you have a set of observations that were taken at a particular site, you can use the 
            dict {1: "Site Visit", 2: "Sample", 3: "Observation"}.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_events vignette <../../html/corella_user_guide/longitudinal_studies/set_events.html>`_
    """
    
    # first, check for data frame
    check_for_dataframe(dataframe=dataframe,func='set_events')

    # mapping of column names and variables
    mapping = {
        'eventID': eventID,
        'parentEventID': parentEventID, 
        'eventType': eventType,
        'Event': Event,
        'samplingProtocol': samplingProtocol
    }

    # accepted data formats for each argument
    accepted_formats = {
        'eventID': [str,list],
        'parentEventID': [str,list], 
        'eventType': [str],
        'Event': [str],
        'samplingProtocol': [str]
    }

    # specify variables and values for set_data_workflow()
    variables = [eventID,parentEventID,eventType,Event,samplingProtocol]
    values = ['eventID','parentEventID','eventType','Event','samplingProtocol']

    # check that parentEventID is not present without eventID
    if parentEventID is not None and eventID is None:
        raise ValueError("You cannot set parentEventID without defining your eventID.")

    # check if user wants a random or sequential ID
    if type(mapping['eventID']) is str or type(mapping['eventID']) is list:
        if mapping['eventID'] in ['random','sequential'] or any(x in ['random','sequential'] for x in mapping['eventID']):
            values.remove('eventID')
            variables.remove(mapping['eventID'])
            del mapping['eventID']
            del accepted_formats['eventID']

    # make sure the eventID variable is a list
    if type(eventID) is str:
        eventID = [eventID]

    # set column names and values specified by user
    if eventID is not None:
        if any(x in ['random','sequential'] for x in eventID):
            if not all(mapping[x] is None for x in mapping):
                # set column names and values specified by user
                dataframe = set_data_workflow(func='set_events',dataframe=dataframe,mapping=mapping,variables=variables,
                                              values=values,accepted_formats=accepted_formats)
            elif event_hierarchy is None:
                dataframe = add_unique_IDs(dataframe=dataframe,column_name='eventID',column_info=eventID,sep=sep)
        else:
            dataframe = set_data_workflow(func='set_events',dataframe=dataframe,mapping=mapping,variables=variables,
                                          values=values,accepted_formats=accepted_formats)
    else:
        dataframe = set_data_workflow(func='set_events',dataframe=dataframe,mapping=mapping,variables=variables,
                                      values=values,accepted_formats=accepted_formats)

    # check for event_hierarchy
    # need to figure out parentEventID...
    if event_hierarchy is not None and not set(dataframe.columns).issuperset({'eventID','parentEventID'}):
        if eventID is None and (eventID not in dataframe.columns):
            print('setting your eventIDs to a random UUID.  To make a custom eventID, provide column names, and/or the words \'random\', \'sequential\'.')
            eventID='random'
        dataframe=generate_eventID_parentEventID(dataframe=dataframe,event_hierarchy=event_hierarchy,
                                                 sep=sep,eventID=eventID)
    else:
        pass

    # check for errors
    errors = check_events(dataframe=dataframe,errors=[])

    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe