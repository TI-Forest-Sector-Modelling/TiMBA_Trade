from src.Trade_Module.core.InputManager import InputManager
from src.Trade_Module.core.OutputManager import OutputManager
from src.Trade_Module.core.ProcessManager import ProcessManager

im = InputManager()
om = OutputManager()

if __name__== "__main__":
    data = im.main()
    pm = ProcessManager(data=data)
    df = pm.main()
    om.save_df(
        df=df,
        file_name="v008_DEU"
    )