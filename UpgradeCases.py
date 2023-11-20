import win32com.client
from time import time
import os
import pandas as pd
from openpyxl import load_workbook
import datetime
import pandas as pd
from datetime import datetime, timedelta
import sys

# Get username PC
us = os.getlogin()

# SAP Conection
try:
    SapGuiAuto = win32com.client.GetObject("SAPGUI")
    application = SapGuiAuto.GetScriptingEngine
    connection = application.Children(0)
    session = connection.Children(0)
    print("SAP successfully connected.")
except:
    print("SAP não está conectado, verifique!")

# Obter a data atual
data_atual = datetime.now()

# Obter o primeiro dia do mês atual
primeiro_dia = datetime(data_atual.year, data_atual.month, 1)

# Formatando a data para "dd.mm.yyyy"
primeiro_dia_formatado = primeiro_dia.strftime("%d.%m.%Y")

# Obter o último dia do mês atual
ultimo_dia = datetime(data_atual.year, data_atual.month + 1, 1) - timedelta(days=1)

# Formatando a data para "dd.mm.yyyy"
ultimo_dia_formatado = ultimo_dia.strftime("%d.%m.%Y")

def obter_data_formatada():
    # Obter a data atual
    data_atual = datetime.now()

    # Formatar a data no padrão dd.mm.yyyy
    data_formatada = data_atual.strftime("%d.%m.%Y")

    return data_formatada

# Chamar a função e imprimir a data formatada
data_atual_formatada = obter_data_formatada()


# Script SAP para obter as ordens de upgrade cases
try:
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nzsd_orders_kpi"
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]/usr/ctxtP_VKORG").text = "4400"
    session.findById("wnd[0]/tbar[1]/btn[25]").press()
    session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").currentCellRow = (-1)
    session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").selectColumn ("VARIANT")
    session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").selectedRows = ""
    session.findById("wnd[1]/tbar[0]/btn[38]").press()
    session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "/upgrade"
    session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = (8)
    session.findById("wnd[2]/tbar[0]/btn[0]").press()
    session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").selectedRows = "0"
    session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").clickCurrentCell()
    session.findById("wnd[0]/usr/ctxtS_VBELN-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_VBELN-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_AUART-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_AUART-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_AUGRU-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_AUGRU-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_VSBED-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_VSBED-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_VBL_VL-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_VBL_VL-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_ERDAT-LOW").text = primeiro_dia_formatado
    session.findById("wnd[0]/usr/ctxtS_ERDAT-HIGH").text = ultimo_dia_formatado
    session.findById("wnd[0]/usr/txtS_ERNAM-LOW").text = ""
    session.findById("wnd[0]/usr/txtS_ERNAM-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_KUNNR-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_KUNNR-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_WERKS-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_MATNR-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_MATNR-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_CHARG-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_CHARG-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_ZTERM-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_ZTERM-HIGH").text = ""
    session.findById("wnd[0]/usr/txtS_BSTKD-LOW").text = "*Upgrade"
    session.findById("wnd[0]/usr/txtS_BSTKD-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_BSARK-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_BSARK-HIGH").text = ""
    session.findById("wnd[0]/usr/txtS_ASSESS-LOW").text = ""
    session.findById("wnd[0]/usr/txtS_ASSESS-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_PROM_C-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_PROM_C-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_VBL_RK-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_VBL_RK-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_DCNMNF-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_DCNMNF-HIGH").text = ""
    session.findById("wnd[0]/usr/txtS_NFENUM-LOW").text = ""
    session.findById("wnd[0]/usr/txtS_NFENUM-HIGH").text = ""
    session.findById("wnd[0]/usr/ctxtS_BRANCH-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_BRANCH-HIGH").text = ""
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[4,0]").select()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[4,0]").setFocus()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
except Exception as e:
    print(f"Nenhum criterio selecionado: {e}")
    sys.exit()


# Trata Clipboard com o numero dos pedidos
gusta = pd.read_clipboard(sep='|', header=3, dtype=str)
gusta = gusta[gusta['  Sales Doc.'].notnull()][['  Sales Doc.']]
gusta = gusta[gusta['  Sales Doc.']!='          ']
# Verifica se não há nenhum pedido encontrado
if 'No Data' in gusta.iloc(0)[0][0]:
    print("Nenhum pedido encontrado")
    sys.exit()
else:
    # output
    print(gusta)


for index, row in gusta.iterrows():
# acessa VA02 para iniciar faturamento
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nva02"
    session.findById("wnd[0]").sendVKey (0)    
    session.findById("wnd[0]/usr/ctxtVBAK-VBELN").text = row['  Sales Doc.']
    session.findById("wnd[0]").sendVKey (0)

    # verifica bloqueio
    session.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/btnBT_HEAD").press()
    session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\11").select()
    var = session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\11/ssubSUBSCREEN_BODY:SAPMV45A:4305/txtVBSTT-SPSTG_BEZ").text
    if var == "Blocked":
        print(f"Pedido bloqueado - {row['  Sales Doc.']}")
    else:
        session.findById("wnd[0]/tbar[0]/btn[3]").press()    
        session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01/ssubSUBSCREEN_BODY:SAPMV45A:4402/ssubHEADER_FRAME:SAPMV45A:9440/cmbVBAK-AUGRU").key = ("Y99")
        session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01/ssubSUBSCREEN_BODY:SAPMV45A:4402/ssubHEADER_FRAME:SAPMV45A:9440/cmbVBAK-AUGRU").setFocus()
        session.findById("wnd[0]/mbar/menu[0]/menu[8]").select()
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        try:
            # bandeira nota na J1BNFE
            session.findById("wnd[0]/tbar[0]/okcd").text = "/nj1bnfe"
            session.findById("wnd[0]").sendVKey (0)
            session.findById("wnd[0]/usr/ctxtDATE0-LOW").text = data_atual_formatada
            session.findById("wnd[0]/usr/ctxtBUKRS-LOW").text = "4400"
            session.findById("wnd[0]/usr/txtSHIPT-LOW").text = "4401"
            session.findById("wnd[0]/usr/txtUSERCRE-LOW").text = us
            session.findById("wnd[0]/tbar[1]/btn[8]").press()
            session.findById("wnd[0]/usr/cntlNFE_CONTAINER/shellcont/shell").pressToolbarContextButton ("&MB_VARIANT")
            session.findById("wnd[0]/usr/cntlNFE_CONTAINER/shellcont/shell").selectContextMenuItem ("&LOAD")
            session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").currentCellRow = (5)
            session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectedRows = "5"
            session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()
            session.findById("wnd[0]/usr/cntlNFE_CONTAINER/shellcont/shell").setCurrentCell (-1,"")
            session.findById("wnd[0]/usr/cntlNFE_CONTAINER/shellcont/shell").selectColumn ("STATUS")
            session.findById("wnd[0]/usr/cntlNFE_CONTAINER/shellcont/shell").selectColumn ("ACTION_REQU")
            session.findById("wnd[0]/usr/cntlNFE_CONTAINER/shellcont/shell").selectColumn ("ERRLOG")    
            session.findById("wnd[0]/usr/cntlNFE_CONTAINER/shellcont/shell").selectColumn ("DOCNUM")
            session.findById("wnd[0]/usr/cntlNFE_CONTAINER/shellcont/shell").selectedRows = ("0")
            session.findById("wnd[0]/tbar[1]/btn[30]").press()
        except Exception as e:
            print(f"Erro ao faturar, verifique! Sales Doc.: {row['  Sales Doc.']}")
