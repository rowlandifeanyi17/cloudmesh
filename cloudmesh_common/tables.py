from pytimeparse.timeparse import timeparse
from prettytable import PrettyTable

def column_table(column_dict, order=None):
    """prints a pretty table from data in the dict.
    :param column_dict: A dict that has an array for each key in the dict.
                        All arrays are of the same length.
                        The keys are used as headers
    :param order: The orde in which the columns are printed.XS
                  The order is specified by the key names of the dict.
    """
    # header
    header = column_dict.keys()
    x = PrettyTable()
    if order is None:
        order = header
    for key in order:
        x.add_column(key, column_dict[key])
    x.align = "l"
    return x

def two_column_table(column_dict):
    # header
    header = ['Default','Value']
    x = PrettyTable()
    x.add_column('Default', column_dict.keys())
    x.add_column('Value', column_dict.values())
    x.align = "l"
    return x

def table_printer(the_dict, header_info=None):
    """
    prints recurseively a dict as an html. The header info is simpli a list with
    collun names.

    :param the_dict: the dictionary to be printed.
    :param header_info: an array of two values that are used in the header

    """
    # header_info ["attribute", "value"]
    if (header_info is not None) or (header_info == ""):
        result = '<tr><th>{0}</th><th>{1}</th></tr>'\
                .format(header_info[0], header_info[1])
    else:
        result = ''
    if isinstance(the_dict, dict):
        for name, value in the_dict.iteritems():
            result = result + \
                '<tr><td>{0}</td><td>{1}</td></tr>'\
                .format(name.title(), str(table_printer(value)))
        result = '<table>' + result + '</table>'
        return result
    elif isinstance(the_dict, list):
        for element in the_dict:
            try:
                for name, value in element.iteritems():
                    result = result + \
                        '<tr><td>{0}</td><td>{1}</td></tr>'\
                        .format(name.title(), str(table_printer(value)))
            except:
                #If the element is not dict
                return str(element)
        result = '<table>' + result + '</table>'
        return result
    else:
        return the_dict
        

def parse_time_interval (time_start, time_end):
    """created time values for time_start and time_end, while time_end
    will be replaced with time_start+ a duration if the duration is
    given in time_end. The format of the duration is intuitive through
    the timeparse module. YOu can specify values such as +1d, +1w10s.

    :param time_start: the start time, if the string 'current_time' is passed it will be replaced by the current time
    :param time_end: either a time or a duration
    """ 
    t_end = time_end
    t_start = time_start

    if t_start is not None:
        if t_start in ["current_time","now"]:
            t_start = str(datetime.now())

    if t_end is not None:
        if t_end.startswith("+"):
            duration = t_end[1:]
            delta = timeparse(duration)
            t_start = datetime.strptime(t_start, "%Y-%m-%d %H:%M:%S.%f")
            t_end = t_start + timedelta(seconds=delta)

    return (str(t_start), str(t_end))


