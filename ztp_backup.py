# ----------------------------------------------------------------------------------------------------------------------
# Project Code    : SULTAN
# File name       : ZTP_for_MS.py
# Author          : Weizihuan 00391570
# ----------------------------------------------------------------------------------------------------------------------
# History:
# Date               version                     Modification
# 20180707           1.21                       add link number design
# ----------------------------------------------------------------------------
import xlrd
from jinja2 import Environment, FileSystemLoader
import os
from pprint import pprint
# ==========================val. definitions==========================
site_list='.\\al.xlsx'
order_map='.\\merged_ms_al.xlsx'
templates='.\\templates'
import shutil
#==========================val. definitions==========================
def clear_folder():
    shutil.rmtree('.\\cascade')
    shutil.rmtree('.\\ms')
    os.mkdir('.\\cascade')
    os.mkdir('.\\ms')
# ===================== Method Area ============
def data_pre_process(site_list,order_map):
    al = xlrd.open_workbook(site_list)
    df_site=al.sheet_by_name("NE")
    ordermap=xlrd.open_workbook(order_map)
    df_NE=ordermap.sheet_by_name("NE")
    df_L2link=ordermap.sheet_by_name("L2link")
    df_L3link = ordermap.sheet_by_name("L3link")
    return df_site,df_NE,df_L2link,df_L3link

def generate_site_data(df_site,df_NE,df_L2link,df_L3link):
    site_ms_l2,site_ms_l3,site_cascade_l2,site_cascade_l3 = {},{},{},{}
    ne_match_list,site_list,ne_list=[],[],[]
    ### get site list##########
    for row in range(1,df_site.nrows):
        if df_site.cell_value(row, 0) is not None:
            site_list.append(df_site.cell_value(row, 0))
    #####get ne list ####################
    for row in range(1,df_NE.nrows):
        if df_NE.cell_value(row, 0) is not None:
            ne_list.append(df_NE.cell_value(row, 0))
    #####generate match site list#############
    for site in site_list:
        for ne in ne_list:
            if site in ne and '-al-' in ne:
               ne_match_list.append(ne)
    #########match layer2 planning#############
    for row in range(1,df_L2link.nrows):
        row_value=[df_L2link.cell_value(row, 0),df_L2link.cell_value(row, 1),
                   df_L2link.cell_value(row, 2),df_L2link.cell_value(row, 3),
                   df_L2link.cell_value(row, 4),df_L2link.cell_value(row, 5),
                   df_L2link.cell_value(row, 6),df_L2link.cell_value(row, 7)
                   ]
        if '-ms-' in str(row_value[0]) and  str(row_value[3]) in ne_match_list:
            site_id=str(row_value[3])
            if site_id not in site_ms_l2:
                site_ms_l2[site_id]=[row_value]
            else:
                site_ms_l2[site_id].append(row_value)
        if 'al'==str(row_value[3]).split('-')[3] and \
                ('02'==str(row_value[3]).split('-')[4]or'52'==str(row_value[3]).split('-')[4]) and\
                ('01'==str(row_value[0]).split('-')[4]or'51'==str(row_value[0]).split('-')[4]) \
                and str(row_value[3])in ne_match_list:
            site_id = str(row_value[3])
            if site_id not in site_cascade_l2:
                site_cascade_l2[site_id]=[row_value]
            else:
                site_cascade_l2[site_id].append(row_value)
    #########match layer3 planning#############
    for row in range(1,df_L3link.nrows):
        row_value = [df_L3link.cell_value(row, 0), df_L3link.cell_value(row, 1),
                     df_L3link.cell_value(row, 2), df_L3link.cell_value(row, 3),
                     df_L3link.cell_value(row, 4), df_L3link.cell_value(row, 5),
                     df_L3link.cell_value(row, 6), df_L3link.cell_value(row, 7),
                     df_L3link.cell_value(row, 8), df_L3link.cell_value(row, 9)
                     ]
        if '-ms-' in str(row_value[0]) and str(row_value[4]) in ne_match_list:
            site_id=str(row_value[4])
            if site_id not in site_ms_l3:
                site_ms_l3[site_id] = [row_value]
            else:
                site_ms_l3[site_id].append(row_value)
        if 'al' == str(row_value[4]).split('-')[3] and \
                ('02' == str(row_value[4]).split('-')[4] or '52' == str(row_value[4]).split('-')[4]) and \
                ('01' == str(row_value[0]).split('-')[4] or '51' == str(row_value[0]).split('-')[4]) \
                and str(row_value[4])in ne_match_list:
            site_id = str(row_value[4])
            if site_id not in site_cascade_l3:
                site_cascade_l3[site_id] =[row_value]
            else:
                site_cascade_l3[site_id].append(row_value)
    return site_list,ne_match_list,site_ms_l2,site_ms_l3,site_cascade_l2,site_cascade_l3

def data_check(sitelist,nelist,site_ms_l2,site_ms_l3,site_cascade_l2,site_cascade_l3):
    error_ne_site,error_L2_site,error_L3_site = [],[],[]
    for site in sitelist:
        counter = 0
        for ne in nelist:
            if site in ne and "-ms-" not in ne:
                counter=counter+1
        if counter%2!=0 or counter==0:
            error_ne_site.append(site)
    for ne in nelist:
        if ne not in site_ms_l2 and not ne in site_cascade_l2:
            error_L2_site.append(ne)
        if ne  not in site_ms_l3 and ne not in site_cascade_l3:
            error_L3_site.append(ne)
    return error_ne_site,error_L2_site,error_L3_site

def generate_conf(site_ms_l2,site_ms_l3,site_cascade_l2,site_cascade_l3):
    TEMPLATE = Environment(loader=FileSystemLoader(templates))
    for al,links in site_ms_l2.items():
        if al in site_ms_l2 and al in site_ms_l3:
            template = TEMPLATE.get_template('site_ms.j2')
            file=template.render(sitel2=site_ms_l2[al], sitel3=site_ms_l3[al])
            ms=site_ms_l2[al][0][0]
            if not os.path.exists('.//ms//'+ms):
                os.mkdir('.//ms//'+ms)
            with open('.//ms//'+ms+'//'+al+'.cfg', 'w') as fp:
                fp.write(file)
    for al, links in site_cascade_l2.items():
        if al in site_cascade_l2 and al in site_cascade_l2:
            template = TEMPLATE.get_template('site_cascade.j2')
            file = template.render(sitel2=site_cascade_l2[al], sitel3=site_cascade_l3[al])
            cascade = site_cascade_l2[al][0][0]
            if not os.path.exists('.//cascade//' + cascade):
                os.mkdir('.//cascade//' + cascade)
            with open('.//cascade//' + cascade + '//' + al + '.cfg', 'w') as fp:
                fp.write(file)
def error_log(error_ne_site,error_L2_site,error_L3_site):
    with open('error_ztp_log.log','w') as fp :
        if len(error_ne_site):
            fp.write(" This {0} site missing at order map page NE\n".format(error_ne_site))
        if len(error_L2_site):
            fp.write(" This {0} link missing at order map page L2link\n".format(error_L2_site))
        if len(error_L3_site):
            fp.write(" This {0} link missing at order map page L3link\n".format(error_L3_site))
    fp.close()
#===============main=========================
if __name__ == '__main__':
    print("ztp start running ......")
    clear_folder()
    df_site, df_NE, df_L2link, df_L3link=data_pre_process(site_list, order_map)
    site,nelist,site_ms_l2,site_ms_l3,site_cascade_l2,site_cascade_l3=\
         generate_site_data(df_site,df_NE,df_L2link,df_L3link)
    print("start order_map checking ......")
    error_ne_site, error_L2_site, error_L3_site=\
        data_check(site,nelist,site_ms_l2,site_ms_l3,site_cascade_l2,site_cascade_l3)
    print("start generate configuration ......")
    generate_conf(site_ms_l2,site_ms_l3,site_cascade_l2,site_cascade_l3)
    print("start to generate error log")
    error_log(error_ne_site,error_L2_site,error_L3_site)
    print("ztp running completed")





