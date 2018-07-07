from configparser import RawConfigParser
import io


def get_config(section):
    config_txt = r""" 
                [idis]
                browser='firefox'
                browser_binary="C:\Program Files\Mozilla Firefox\firefox.exe"
                profile_path='C:\Users\basov\AppData\Roaming\Mozilla\Firefox\Profiles\6ti8l5bx.default'
                driver_exe_path='C:\Firefox\geckodriver.exe'
                login="basov"
                password="Planet%Mars%Flight"
                portal_url="https://portal.intra.infineon.com/irj/portal"
                idis_url="https://sappc1lb.eu.infineon.com:8410/sap(bD1lbiZjPTEwMCZkPW1pbg==)/bc/bsp/sap/crm_ui_start/default.htm
                [logging]
                level='DEBUG'
                file='dreg.log'
                format='%(asctime)s %(funcName)s: %(message)s'
                """

    config = RawConfigParser(allow_no_value=True)
    config.read_file(io.StringIO(config_txt))

    items = [(i[0], i[1].strip(' "\'')) for i in config.items(section)]

    return dict(items)
