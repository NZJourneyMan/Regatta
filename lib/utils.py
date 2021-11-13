def mkcrewStr(crew):
    #return ','.join(('' if x is None else x) for x in crew)
    return ','.join(mkCrewList(crew))

def mkCrewList(crew):
    return [x for x in crew if x not in (None, '')]