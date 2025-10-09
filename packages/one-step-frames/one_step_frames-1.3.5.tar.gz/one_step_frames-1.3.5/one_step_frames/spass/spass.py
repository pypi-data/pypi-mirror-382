from .util import load_config,create_dfg_file,run_SPASS

def SPASS(first_order:str,S:str,config=None|dict[str,str]):
    config = load_config()
    id = create_dfg_file(config,first_order,S)
    output,error = run_SPASS(id)
    return output,error
