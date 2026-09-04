from src.Trade_Module.core.InputManager import InputManager
from src.Trade_Module.core.OutputManager import OutputManager

im = InputManager()
om = OutputManager()

if __name__== "__main__":
    data = im.main()
    om.save_df(
        df=data,
        file_name="v003"
    )