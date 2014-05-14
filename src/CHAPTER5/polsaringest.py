#!/usr/bin/env python
#******************************************************************************
#  Name:     polsaringest.py
#  Purpose:
#    utility to ingest georeferenced single, dual or quad polSAR 
#    files generated by ENVI/SARscape or polSARpro/MapReady 
#    from TerraSAR-X, Radarsat-2, Cosmo-Skymed SLC images and 
#    convert to a single 9-band (quad), 4-band (dual), or 1-band (single), 
#    float32 image.
#  Usage:             
#    python polsaringest.py 
#
#  Copyright (c) 2014, Mort Canty
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import auxil.auxil as auxil
import os, re
import numpy as np
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32

def main():
    gdal.AllRegister()
    path = auxil.select_directory('Choose working directory')
    if path:
        os.chdir(path)        
#  get (spatial subset of) the C11 or C33 file first    
    file1 = auxil.select_infile(title='Choose one componenst (C11, C22 or C33) ') 
    if file1:                   
        inDataset1 = gdal.Open(file1,GA_ReadOnly)     
        cols = inDataset1.RasterXSize
        rows = inDataset1.RasterYSize    
        bands = inDataset1.RasterCount
    else:
        return
    inDataset = None
#  spatial subset    
    x0,y0,rows,cols=auxil.select_dims([0,0,rows,cols])    
#  output file
    outfile,fmt = auxil.select_outfilefmt() 
    if not outfile:
        return    
#  output image
    outim = np.zeros((9,rows,cols), dtype=np.float32)    
#  get list of all files
    files = os.listdir(path) 
    for afile in files:
        if re.search('hdr|sml',afile):
            continue       
#      single polarimetry  
        if re.search('pwr_geo',afile): 
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[0,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None
#      dual and quad polarimetry                
        elif re.search('hh_hh_geo|C11\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[0,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None 
        elif re.search('re_hh_hv_geo|C12_real\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[1,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None     
        elif re.search('im_hh_hv_geo|C12_imag\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[2,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None      
        elif re.search('re_hh_vv_geo|C13_real\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[3,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None     
        elif re.search('im_hh_vv_geo|C13_imag\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[4,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None       
        elif re.search('hv_hv_geo|C22\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[5,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None     
        elif re.search('re_hv_vv_geo|C23_real\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[6,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None     
        elif re.search('im_hv_vv_geo|C23_imag\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[7,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None      
        elif re.search('vv_vv_geo|C33\.tif',afile):
            inDataset = gdal.Open(afile,GA_ReadOnly)
            band = inDataset.GetRasterBand(1)
            outim[8,:,:] = band.ReadAsArray(x0,y0,cols,rows)   
            inDataset = None  
    outim = np.nan_to_num(outim)           
    idx = np.where(np.sum(np.abs(outim),axis=(1,2))>0)[0]
    if idx == []:
        print 'no polarimetric bands found'    
        return
    bands = len(idx)
    driver = gdal.GetDriverByName(fmt)   
    outDataset = driver.Create(outfile,cols,rows,bands,GDT_Float32)
    projection = inDataset1.GetProjection()
    geotransform = inDataset1.GetGeoTransform()
    if geotransform is not None:
        gt = list(geotransform)
        gt[0] = gt[0] + x0*gt[1]
        gt[3] = gt[3] + y0*gt[5]
        outDataset.SetGeoTransform(tuple(gt))
    if projection is not None:
        outDataset.SetProjection(projection)        
    for k in range(bands):        
        outBand = outDataset.GetRasterBand(k+1)
        outBand.WriteArray(outim[idx[k],:,:],0,0) 
        outBand.FlushCache() 
    outDataset = None            
    print 'polarimetric image written to: %s'%outfile        
            
if __name__ == '__main__':
    main()
    