import irispie as ir
import numpy as np

def main():
    out = ir.Series(periods=ir.qq(2023, 1) >> ir.qq(2025, 4), values=np.random.normal(0, 10, 12)).plot(return_info=True, show_figure=False,)
    out["figure"].update_layout(
        {"title": {
            "text": "Hello world",
        },
            "xaxis": {
                "ticks": "inside",
                "tickcolor": "black",
                "linewidth": 1,
                "tickwidth": 1,
                "tickmode": "sync",
                "showline": True,
                "ticklabel": "Period",
                "linecolor": "black"
            }
        }
    )

    out["figure"].show()


if __name__ == "__main__":
    main()