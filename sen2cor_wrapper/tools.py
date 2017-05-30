import os
import re
import glob

import osr

from gdal_utils import gdal_utils as gu
import sentinel_meta.s2.meta as s2meta


def tile_from_fname(fname):
    """Get tile name from S2 standard file name"""
    bn = os.path.basename(fname)
    try:
        tilepattern = '(?<=T)([0-9]{2}[A-Z]{3})'
        return re.search(tilepattern, bn).group(0)
    except AttributeError:
        raise ValueError('Unable to get tile from {} '
                'looking for \'{}\''.format(bn, tilepattern))


def path_L1C_to_L2A(path):
    """Convert path name from L1C to L2A"""
    root, base = os.path.split(path)
    return os.path.join(root,
            base.replace('L1C', 'L2A').replace('OPER', 'USER'))


def find_classfiles(L2A_path):
    """Find classification files in L2A_path"""
    # make sure input data exist
    if not os.path.isdir(L2A_path):
        raise ValueError('sen2cor directory {} '
                'not found.'.format(L2A_path))
    # find class files
    pattern = os.path.join(L2A_path, 'GRANULE', 'S2A_*_L2A_*',
            'IMG_DATA', 'S2A_USER_SCL_L2A_*_60m.jp2')
    classfiles = sorted(glob.glob(pattern))
    if not classfiles:
        raise ValueError('No classificiation files found '
                'for pattern \'{}\'.'.format(pattern))
    return classfiles


def get_tiles_projtrans(xmlfile, granules, out_res):
    """Get tiles projection and geotramsform from meta data

    Parameters
    ----------
    xmlfile : str
        path to meta data xml file
    granules : list of str
        list of granules to extract
    out_res : int
        resolution of interest

    Returns
    -------
    dict : {'WWDDD': dict(projection=str, geotransform=[float]*6)}
    """
    out_res_str = str(out_res)

    # parse meta data
    meta = s2meta.find_parse_metadata(xmlfile)
    granulemeta = meta['granules']

    # get projection and geotramsform plus size
    projtrans = {}
    for granulename in granules:
        key = granulename
        if not key.startswith('T'):
            key = 'T'+key
        ULX = float(granulemeta[key]['ULX_'+out_res_str])
        ULY = float(granulemeta[key]['ULY_'+out_res_str])
        xsize = int(granulemeta[key]['cols_'+out_res_str])
        ysize = int(granulemeta[key]['rows_'+out_res_str])
        geotransform = (ULX, float(out_res), 0.0, ULY, 0.0, float(out_res)*-1)
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(int(granulemeta[key]['projection'][5:]))
        projection = sr.ExportToWkt()

        projtrans[granulename] = dict(
                projection=projection,
                geotransform=geotransform,
                nx=xsize, ny=ysize)
    return projtrans


def set_projection_on_classfiles(L2A_path, xmlfile, out_res):

    classfiles = find_classfiles(L2A_path)
    granules = [tile_from_fname(fn) for fn in classfiles]
    projtrans = get_tiles_projtrans(xmlfile, granules, out_res)

    for classfile, granule in zip(classfiles, granules):
        gu.add_crs(classfile,
                projection=projtrans[granule]['projection'],
                geotransform=projtrans[granule]['geotransform'])
