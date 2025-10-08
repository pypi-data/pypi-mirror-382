# test bokeh
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import WheelZoomTool, BoxZoomTool, HoverTool, ColumnDataSource, CustomJS, \
                        LegendItem, Legend, ColorBar, LinearColorMapper, TableColumn, DataTable, TapTool
from bokeh.models.widgets import Select
from bokeh.layouts import column, row
from ..layout.circle_collision import Circle
from collections import defaultdict
import re


def CoordinatesToCircles(xs, ys, ids):
    '''
    Convert a list of x and y coordinates to a list of Circle objects.

    Arguments:
    - xs: list
        list of x coordinates
    - ys: list
        list of y coordinates
    - ids: list
        list of ids

    Returns:
    - circles: list
        list of Circle objects
    '''
    return [Circle(x,y,1,id) for x,y,id in zip(xs,ys,ids)]

rgba_re=re.compile(r'rgba\((\d+),(\d+),(\d+),(\d+)\)')
output_notebook()
black='rgba(0,0,0,255)'
def CirclePlot(layout, layout_order=None,
               size=800, fill_legend_width=200, outline_legend_width=200, # general
               annot_text:list=None, annot_top_n:int=None, annot_na=True, singleton_annot_text=False, # annotation related
               annot_colors=None, base_fill=None,  # face color related
               outlines=None, base_line='rgba(0,0,0,255)', base_line_width=1, highlight_line_width=1, # outline related
               fixed_point_size=None # if set, overrides individual radii
                ,
               ## more experimental features
                mapping_table=None,
                data_on_select_table=None,
                data_key_column='id',
                data_table_width=800,
                data_table_height=300
               ):
    '''
    Make a hierarchical circle plot using bokeh. Adds colors and annotations to the circles.

    Arguments:
    - General:
        - layout: dict
            layout of the circles
        - size: int
            size of the plot
    - Tooltip text:
        - annot_text: list
            list of annotation dictionaries generated with AnnotCluster
        - annot_top_n: int
            number of highest proportion entries to show in the text annotations
        - annot_na: bool
            whether to show NA values in the text annotations
        - singleton_annot_text: bool
            assumes data is singletons, to allow faster mapping of annotations to data points
    - Fill coloring:
        - annot_colors: dict
            dictionary of annotation colors, generated with ColorAnnot
        - base_fill: str
            default fill color for the circles if there are no annotations
    - Outline coloring:
        - outlines: dict
            dictionary of outline colors, generated with ColorAnnot
        - base_line: str
            default outline color for the circles if there are no annotations
        - base_line_width: int
            default outline width for the circles if there are no annotations
        - highlight_line_width: int
            width of the outline for highlighted circles
    - Other:
        - fixed_point_size: int
            if set, overrides individual radii

    Returns:
    - p: bokeh.plotting.figure
        bokeh figure object
    - manual_plot_data: dict
        data used for plotting, in a format that can be used to replicate the plot in matplotlib
    '''
    wheel_zoom=WheelZoomTool()
    wheel_zoom.zoom_on_axis=False
    box_zoom=BoxZoomTool()
    box_zoom.match_aspect=True

    # make figure
    fig_args={'width':size, 'height':size, 'match_aspect':True, 'min_border':50,
                'tools':['pan', wheel_zoom, box_zoom, 'reset', 'save']}
    p=figure(**fig_args)
    p.toolbar.active_scroll=wheel_zoom

    # plotting circles
    renderers={}
    levels=sorted(list(layout.keys()), key=float) if layout_order is None else layout_order
    manual_plot_data=defaultdict(list)
    annot_hover=[]
    apply_data_table=mapping_table is not None and data_on_select_table is not None
    if apply_data_table:
        # downfilter to only Entries that have data
        mapping_table=mapping_table[mapping_table[data_key_column].isin(data_on_select_table[data_key_column])]
        data_on_select_table=data_on_select_table.reset_index(drop=True)

    render_sources={}
    for tgt_level in levels:
        # print(f'Plotting level {tgt_level}')
        # print('Organizing data')
        x=[c.x for c in layout[tgt_level].values()]
        y=[c.y for c in layout[tgt_level].values()]
        r=[c.r for c in layout[tgt_level].values()]
        colors=[annot_colors[tgt_level][c.id] if tgt_level in annot_colors and c.id in annot_colors[tgt_level] else base_fill for c in layout[tgt_level].values()] if annot_colors is not None else [base_fill]*len(x)
        line_colors=[outlines[tgt_level][c.id] if tgt_level in outlines and c.id in outlines[tgt_level] else base_line for c in layout[tgt_level].values()] if outlines is not None else [base_line]*len(x)
        line_widths=[highlight_line_width if tgt_level in outlines and c.id in outlines[tgt_level] else base_line_width for c in layout[tgt_level].values()] if outlines is not None else [base_line_width]*len(x)

        draw_dict={'x':x, 'y':y, 'r':r, 'colors':colors, 'line_colors':line_colors, 'line_widths':line_widths,
                            'name':[c.id for c in layout[tgt_level].values()], 
                            'level':[tgt_level]*len(x),
                            'size':[c.size for c in layout[tgt_level].values()],
                            }
        
        # if mappings are available, add them as circle data
        if apply_data_table and tgt_level in mapping_table:
            mapping_slice=mapping_table[[tgt_level,data_key_column]]
            # assign based on c.id
            # mapping = [data_on_select_table[data_on_select_table[data_key_column].isin(mapping_slice[mapping_slice[tgt_level]==c.id][data_key_column])].index.to_list() \
            #           for c in layout[tgt_level].values()]
            
            # use multiprocessing for mapping task
            with mp.Pool() as pool:
                mapping=pool.starmap(GetTableIndices, [(data_on_select_table, mapping_slice, tgt_level, c.id, data_key_column) for c in layout[tgt_level].values()])
            
            # bit of debugging
            # debug_id=list(layout[tgt_level].values())[0].id
            # print(type(debug_id))
            # # print(mapping_slice[mapping_slice[tgt_level]==debug_id])
            # print(data_on_select_table[data_on_select_table[data_key_column].isin(mapping_slice[mapping_slice[tgt_level]==debug_id][data_key_column])].index.to_list())

            # for i in range(len(mapping)):
            #     if len(mapping[i])>0:
            #         print(mapping[i])
            #         break

            # append mapping data
            draw_dict['mapping']=mapping
        
        # print('Making tooltip text')
        # add text
        if annot_text is not None:
            for annot in annot_text:
                annot_label=f'{annot['value']} {annot['method']}'.capitalize()
                annot_key=f'{annot['value']}_{annot['method']}'
                annot_tooltip=(annot_label, f'@{annot_key}{{safe}}')
                if annot_tooltip not in annot_hover:
                    annot_hover.append(annot_tooltip)
                if tgt_level in annot:
                    if singleton_annot_text:
                        level_annot_dict=annot[tgt_level].set_index('id')['value'].to_dict()
                        hover_text=[level_annot_dict[c.id] if c.id in level_annot_dict else None for c in layout[tgt_level].values()]
                    else:
                        hover_text=MakeHoverText(annot, tgt_level, draw_dict['name'], top_n=annot_top_n, 
                                             blank_fill=None, cluster_sizes=draw_dict['size'], annot_na=annot_na)
                else:
                    hover_text=[None]*len(x)
                draw_dict[annot_key]=hover_text
        # print('Drawing circles')
        circles=ColumnDataSource(data=draw_dict)
        render_sources[tgt_level]=circles

        if fixed_point_size is None:
            renderers[tgt_level]=p.circle('x', 'y', radius='r', fill_color='colors', line_color='line_colors', source=circles, line_width='line_widths')
        else:
            renderers[tgt_level]=p.scatter('x', 'y', size=fixed_point_size, fill_color='colors', line_color='line_colors', source=circles, line_width='line_widths')

        # print('Collecting plot data')
        # save data for manual plotting
        manual_plot_data['x'].extend(x)
        manual_plot_data['y'].extend(y)
        manual_plot_data['r'].extend(r if fixed_point_size is None else [fixed_point_size]*len(x))
        c_conv=[]
        lc_conv=[]
        for i in range(len(x)):
            if colors[i] is None:
                c_conv.append([1,1,1,0])
            else:
                c_conv.append([float(v)/255 for v in rgba_re.match(colors[i]).groups()])
            if line_colors[i] is None:
                lc_conv.append([1,1,1,0])
            else:
                lc_conv.append([float(v)/255 for v in rgba_re.match(line_colors[i]).groups()])
        manual_plot_data['colors'].extend(c_conv)
        manual_plot_data['line_colors'].extend(lc_conv)
        manual_plot_data['line_widths'].extend(line_widths)
        manual_plot_data['name'].extend([c.id for c in layout[tgt_level].values()])
        manual_plot_data['level'].extend([tgt_level]*len(x))
    
    # print('Finishing up')
    # Define tooltips
    no_size=all([v is None for v in draw_dict['size']])
    tooltips = [
        ("Level", "@level"),
        ("Cluster", "@name"),
        # ("(x,y)", "($x, $y)"),
    ] + ([("Size", "@size")] if not no_size else []) + annot_hover

    hover=HoverTool(tooltips=tooltips, renderers=list(renderers.values())[-1:])
    p.add_tools(hover)
    tap_tool = TapTool(mode='replace')
    p.add_tools(tap_tool)

    # apply data table if available
    data_table=None
    data_on_select_source=None
    table_view_source=None
    if apply_data_table:
        data_on_select_source=ColumnDataSource(data_on_select_table)
        columns=[TableColumn(field=col, title=col) for col in data_on_select_table.columns]
        table_view_source=ColumnDataSource(data=dict(zip(columns, []*len(columns))))
        
        data_table=DataTable(source=table_view_source, columns=columns, width=data_table_width, height=data_table_height, fit_columns=True)

    # selection for which tooltips to show
    dropdown=Select(title='Label level', options=levels, value=levels[-1])
    
    # Callback function to update hover renderers
    dropdown.js_on_change('value', CustomJS(args=dict(hover=hover, options=renderers), code="""
        hover.renderers = [options[cb_obj.value]];
                                            """))
    
    # dropdown.js_on_change('value', callback)

    # callback function to update data table
    callback = CustomJS(args=dict(dropdown=dropdown, sources=render_sources, 
                                  full_data_table=data_on_select_source,
                                  shown_table_source=table_view_source
                                  ), code="""
        const value = dropdown.value;
        const source = sources[dropdown.value];
        // clear unselected sources
        for (const key in sources) {
            if (key!=value) {
                sources[key].selected.indices=[];
            }
        }
        // only keep first selected index
        //source.selected.indices=[source.selected.indices[0]];
         
        // check if data table can be updated
        if ('mapping' in source.data && full_data_table!=null) {
            if (source.selected.indices.length>0) {
                const selected_index=source.selected.indices[0];
                const mapping_ids=source.data.mapping[selected_index];

                // update data table
                const data_table=full_data_table.data;
                const new_data={};
                for (const key in data_table) {
                    new_data[key]=[];
                }
                
                for(const id of mapping_ids) {
                    for (const key in data_table) {
                        new_data[key].push(data_table[key][id]);
                    }
                }

                // update table view
                // put one extra row in table for debug to show clicked
                // for (const key in data_table) {
                    // new_data[key].push(data_table[key][mapping_ids[0]]);
                   // new_data[key].push(source.data.mapping.length);
                //}
                shown_table_source.data=new_data;
            }
            else{
                shown_table_source.data={};
            }
        }
    """)

    for render_source in render_sources.values():
        render_source.selected.js_on_change('indices', callback)
    
    # Layout
    legends=[]
    if annot_colors is not None:
        legend, manual_data=MakeLegend(annot_colors, p, legend_width=fill_legend_width)
        manual_plot_data['fill_legend']=manual_data
        legends.append(legend)
    if outlines is not None:
        legend, manual_data=MakeLegend(outlines, p, outline=True, legend_width=outline_legend_width)
        manual_plot_data['line_legend']=manual_data
        legends.append(legend)

    if apply_data_table:
        row1=row(*([p] + legends+[dropdown]))
        row2=row(data_table)
        layout=column(row1, row2)
    else:
        layout=row(*([p] + legends + [dropdown]))
    show(layout)

    return layout, manual_plot_data

def GetTableIndices(data_table, mapping_table, level, level_id, id_col):
    '''
    Get the indices of the data table that correspond to the selected id in the mapping table.

    Arguments:
    - data_table: pandas.DataFrame
        data table
    - mapping_table: pandas.DataFrame
        mapping table
    - level: str
        level of the mapping table
    - id_col: str
        column name of the id in the mapping table

    Returns:
    - indices: list
        list of indices in the data table
    '''
    return data_table[data_table[id_col].isin(mapping_table[mapping_table[level]==level_id][id_col])].index.to_list()

def MakeLegend(annot_colors, p, outline=False, legend_width=200):
    legend_fig = figure(width=legend_width, height=p.height, toolbar_location=None, min_border=0, outline_line_color=None)
    legend_fig.xaxis.visible = False
    legend_fig.yaxis.visible = False
    legend_fig.xgrid.visible = False
    legend_fig.ygrid.visible = False

    manual_plot_data={}            
    if 'categories' in annot_colors:
        legend_items=[]
        manual_plot_data['legend_colors']={}
        for cat, color in annot_colors['categories'].items():
            # if outline:
            #     legend_items.append(LegendItem(label=cat, renderers=[legend_fig.circle(0,0, color=['grey'], line_color=[color], radius=0)]))
            # else:
            legend_items.append(LegendItem(label=cat, renderers=[legend_fig.circle(0,0, color=[color], line_color=['black'], radius=0)]))
            manual_plot_data['legend_colors'][cat]=[float(v)/255 for v in rgba_re.match(color).groups()]
        legend=Legend(items=legend_items)
        legend_fig.add_layout(legend)
        # modify legend text size
        legend_fig.legend.label_text_font_size = '9pt'
        legend_fig.legend.spacing = 1
    elif 'colorscale' in annot_colors:
        colorscale=[v[1] for v in annot_colors['colorscale']]
        for i, v in enumerate(colorscale):
            colorscale[i]=[float(x)/255 for x in rgba_re.match(v).groups()]
        manual_plot_data['colorscale']=colorscale
        manual_plot_data['colorscale_range']=[annot_colors['min'], annot_colors['max']]
        # convert to hex rgb
        colorscale=[f'#{"".join([hex(int(x*255))[2:].zfill(2) for x in c])}' for c in colorscale]
        color_mapper=LinearColorMapper(palette=colorscale, low=annot_colors['min'], high=annot_colors['max'])
        legend=ColorBar(color_mapper=color_mapper, label_standoff=12, location=(0,0))
        legend_fig.add_layout(legend, 'left')
        # plot 1 invisible circle to stop error message
        legend_fig.circle(0,0, color='white', line_color='white', radius=0)
    # add title to legend
    legend_fig.title.text_font_size='10pt'
    legend_fig.title.align='center'
    legend_fig.title.text=annot_colors['value']+' '+ annot_colors['method'] + (' (fill)' if not outline else ' (outline)')
    manual_plot_data['title']=legend_fig.title.text
    return legend_fig, manual_plot_data

import multiprocessing as mp

def MakeHoverText(annot, level, ids, top_n=None, blank_fill=None, cluster_sizes=None, annot_na=True):
    hover_text=[] # one per id, in the order they appear
    is_numeric=annot['method']!='counts'
    
    # use multiprocessing
    with mp.Pool() as pool:
        hover_text=pool.starmap(ClusterHoverText, [(annot, level, id, top_n, blank_fill, 
                                                    cluster_sizes[i] if cluster_sizes is not None else None, 
                                                    annot_na, is_numeric) for i, id in enumerate(ids)])

    return hover_text

def ClusterHoverText(annot, level, id, top_n=None, blank_fill=None, cluster_size=None, annot_na=True, is_numeric=False):
    # cluster_size=None if cluster_sizes is None else cluster_sizes[i]
    if id not in annot[level].id.values:
        return blank_fill
    else:
        data=annot[level].loc[annot[level].id==id].copy()
        if not annot_na:
            data=data.dropna(subset=['value'])
        if is_numeric:
            return f'{data.value.iloc[0]:.2f}'
        else:
            total=data['count'].sum() if cluster_size is None else cluster_size # explicit will be more accurate as some may just be missing annotations
            data['frac']=(data['count']/total*100).round(2)
            item_total=len(data)
            if top_n is not None:
                data=data.nlargest(top_n, 'count')
            row_text=[]
            for row in data.itertuples():
                row_text.append(f'{row.value}: {row.count} ({row.frac}%)')
            if item_total!=len(data):
                row_text.append(f'...{item_total-len(data)} more')
            return '<br>'.join(row_text)

#####
# Saving figures as PDF
#####

# saving plot with bokeh is finicky, use matplotlib instead
import matplotlib.pyplot as plt
import matplotlib as mpl
from ..layout.circle_collision import GetLimits

def ExportFigure(layout, plot_data, size=5, legend_padding=1, as_scatter=False, fixed_point_size=None):
    '''
    Export a plot from bokeh by replicating the same plot in matplotlib.

    Arguments:
    - layout: dict
        layout of the circles
    - plot_data: dict
        data used for plotting, output from CirclePlot
    - size: int
        Height of the plot in inches. Extra width will be added for legends
    - legend_padding: int
        Factor for extra space added for each legend. Default figure is 3, and each legend is 1.
    - as_scatter: bool
        If True, plot as scatter plot instead of circles (much faster with a lot more points). Circle plots cannot use scatter, as the radii do not scale properly.
    - fixed_point_size: int
        If set, overrides individual radii. Use for setting a specific size for scatters with uniform size.

    Returns:
    - f: matplotlib.figure.Figure
    '''
    all_c=[]
    for lv, c_dict in layout.items():
        all_c+=list(c_dict.values())
    xmin, xmax, ymin, ymax=GetLimits(all_c, 5)

    legends_expected=sum([1 for key in ['fill_legend', 'line_legend'] if key in plot_data])
    width_ratios=[3]+[legend_padding]*legends_expected
    size_extra=size * sum(width_ratios[1:])/width_ratios[0] if legends_expected>0 else 0
    f, axes = plt.subplots( 1, 1+legends_expected, figsize=(size+size_extra, size), gridspec_kw={'width_ratios': width_ratios})
    ax=axes[0]
    ax.axis('off')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal', adjustable='box')
    # remove padding on margins
    if as_scatter:
        sizes=plot_data['r'] if fixed_point_size is None else fixed_point_size
        ax.scatter(plot_data['x'], plot_data['y'], s=sizes, c=plot_data['colors'], edgecolors=plot_data['line_colors'], linewidths=plot_data['line_widths'])
    else:
        for i in range(len(plot_data['x'])):
            circle=plt.Circle((plot_data['x'][i], plot_data['y'][i]), plot_data['r'][i], 
                            facecolor=plot_data['colors'][i], edgecolor=plot_data['line_colors'][i], lw=plot_data['line_widths'][i])
            ax.add_patch(circle)

    legend_count=1
    for key in ['fill_legend', 'line_legend']:
        if key not in plot_data:
            continue
        lax = axes[legend_count]
        lax.axis('off')
        legend_data=plot_data[key]
        # make legend if data given
        if 'legend_colors' in legend_data:
            legend_items=[]
            for cat, color in legend_data['legend_colors'].items():
                legend_items.append(plt.Line2D([0], [0], marker='o', linestyle='None', color=color, markeredgecolor='black', label=cat, markersize=5, markeredgewidth=1))
            # place legend outside to the right, also remove frame
            leg=lax.legend(handles=legend_items, loc='center', title=legend_data['title'], bbox_to_anchor=(0.5, 0.5), frameon=False)
            # Customize the legend title
            plt.setp(leg.get_title(), fontweight='bold')
        elif 'colorscale' in legend_data:
            # make color bar
            custom_cmap=mpl.colors.ListedColormap(legend_data['colorscale'])
            norm=mpl.colors.Normalize(vmin=legend_data['colorscale_range'][0], vmax=legend_data['colorscale_range'][1])
            scalar_mappable=mpl.cm.ScalarMappable(norm=norm, cmap=custom_cmap)
            plt.colorbar(scalar_mappable, ax=lax, label=legend_data['title'], fraction=.2, anchor=(0,0.5))
        legend_count+=1
    # f.subplots_adjust(wspace=0, hspace=0)
    f.tight_layout(w_pad=0)
    return f