#!/usr/bin/env python2
import mapnik 
import os 

def getMapImage( box ):

  highwaList= dict({ "motorway": {'width': 4, 'color': 'green', 'fontSize' : 12}, "trunk" : {'width':3, 'color': 'green', 'fontSize': 11}  , "primary" : {'width':1.5, 'color':'#0090ff', 'fontSize' : 10} , "secondary": {'width': 0.8, 'color': '#ff00ff',  'fontSize' : 8} , "tertiary" : {'width' :0.42, 'color': '#000000',  'fontSize' : 8}, "residential":{'width': 0.21, 'color':'black',  'fontSize' : 8}})
  
  
  map_output = 'mymap.png'
  
  m = mapnik.Map(1024,1024)
  m.background = mapnik.Color('white')
  
  
  for highwayType in highwaList.keys():
    styleType = mapnik.Style()
    rule = mapnik.Rule()
    rule.filter = mapnik.Expression('[highway]=' +"'" + (highwayType)+ "'")
    stk = mapnik.Stroke()
    stk.color = mapnik.Color(highwaList[ highwayType ][ 'color' ])
    stk.line_cap = mapnik.line_cap.ROUND_CAP
    stk.width = highwaList[ highwayType ][ 'width' ]
    line_symbolizer = mapnik.LineSymbolizer(stk)
    rule.symbols.append(line_symbolizer)
    
    rule2 = mapnik.Rule()
    rule2.filter = mapnik.Expression('[highway]=' +"'" + (highwayType)+ "'")
    text_symbolizer = mapnik.TextSymbolizer(mapnik.Expression("[name]"), "DejaVu Sans Book", highwaList[highwayType]['fontSize'], mapnik.Color('black'))
    text_symbolizer.halo_fill = mapnik.Color('white')
    rule2.symbols.append(text_symbolizer)
    styleType.rules.append(rule)
    styleType.rules.append(rule2)
    
    m.append_style( highwayType, styleType)
  
  
  ds = mapnik.Osm(url='http://api.openstreetmap.org/api/0.6/map', bbox= str(box)[1:-1].replace(" ", "") )
  
  layer=mapnik.Layer('world')
  layer.datasource = ds
  for highwayType in highwaList.keys():
    layer.styles.append(highwayType)
  m.layers.append(layer)
  
  m.zoom_all()
  mapnik.render_to_file(m, map_output, 'png')
 
  openImage = os.system( 'xdg-open ' + map_output)


